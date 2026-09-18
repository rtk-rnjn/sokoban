from __future__ import annotations

import os
import pathlib
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import StrEnum

FPS = 30
LEVELS_DIR = pathlib.Path("levels")


class Direction(StrEnum):
    UP = "w"
    LEFT = "a"
    DOWN = "s"
    RIGHT = "d"


PLAYER_SYMBOLS = {
    Direction.UP: "\N{BLACK UP-POINTING TRIANGLE}",
    Direction.DOWN: "\N{BLACK DOWN-POINTING TRIANGLE}",
    Direction.LEFT: "\N{BLACK LEFT-POINTING TRIANGLE}",
    Direction.RIGHT: "\N{BLACK RIGHT-POINTING TRIANGLE}",
}

WALL_SYMBOL = "\N{FULL BLOCK}"
FLOOR_SYMBOL = "\N{MIDDLE DOT}"
TARGET_SYMBOL = "\N{BULLSEYE}"
BLOCK_SYMBOL = "\N{WHITE SQUARE CONTAINING BLACK SMALL SQUARE}"
BLOCK_ON_TARGET_SYMBOL = "\N{FISHEYE}"

if os.name == "nt":
    import msvcrt

    @contextmanager
    def raw_terminal():
        yield

    def read_key() -> str:
        return msvcrt.getwch()

    def key_available() -> bool:
        return msvcrt.kbhit()

else:
    import select
    import termios
    import tty

    @contextmanager
    def raw_terminal():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setcbreak(fd)
            yield
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def read_key() -> str:
        return sys.stdin.read(1)

    def key_available() -> bool:
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        return bool(ready)


@dataclass(frozen=True)
class Position:
    row: int
    col: int

    def moved(self, direction: Direction) -> Position:
        match direction:
            case Direction.UP:
                return Position(self.row - 1, self.col)
            case Direction.DOWN:
                return Position(self.row + 1, self.col)
            case Direction.LEFT:
                return Position(self.row, self.col - 1)
            case Direction.RIGHT:
                return Position(self.row, self.col + 1)


@dataclass(frozen=True)
class GameState:
    player: Position
    blocks: frozenset[Position]
    moves: int
    last_direction: Direction


@dataclass
class Game:
    rows: int
    cols: int
    player: Position
    blocks: set[Position]
    targets: set[Position]
    walls: set[Position]

    moves: int = 0
    running: bool = True
    won: bool = False
    last_direction: Direction = Direction.DOWN

    history: list[GameState] = field(default_factory=list)

    starting_player: Position | None = None
    starting_blocks: frozenset[Position] | None = None

    def __post_init__(self) -> None:
        self.starting_player = self.player
        self.starting_blocks = frozenset(self.blocks)
        self.won = self.is_won()

    def is_inside(self, position: Position) -> bool:
        return 0 <= position.row < self.rows and 0 <= position.col < self.cols

    def is_wall(self, position: Position) -> bool:
        return position in self.walls

    def is_block(self, position: Position) -> bool:
        return position in self.blocks

    def is_won(self) -> bool:
        return self.blocks == self.targets

    def move(self, direction: Direction) -> None:
        new_player = self.player.moved(direction)

        # Can't walk outside the level or through a wall.
        if not self.is_inside(new_player) or self.is_wall(new_player):
            return

        # Player walks into an empty cell.
        if new_player not in self.blocks:
            self.save_state()

            self.player = new_player
            self.last_direction = direction
            self.moves += 1
            self.won = self.is_won()

            return

        # Player is trying to push a block.
        new_block = new_player.moved(direction)

        if not self.is_inside(new_block):
            return

        if self.is_wall(new_block):
            return

        if new_block in self.blocks:
            return

        self.save_state()

        self.blocks.remove(new_player)
        self.blocks.add(new_block)

        self.player = new_player
        self.last_direction = direction
        self.moves += 1

        self.won = self.is_won()

    def save_state(self) -> None:
        self.history.append(
            GameState(
                player=self.player,
                blocks=frozenset(self.blocks),
                moves=self.moves,
                last_direction=self.last_direction,
            )
        )

    def undo(self) -> None:
        if not self.history:
            return

        state = self.history.pop()

        self.player = state.player
        self.blocks = set(state.blocks)
        self.moves = state.moves
        self.last_direction = state.last_direction
        self.won = self.is_won()

    def restart(self) -> None:
        if self.starting_player is None or self.starting_blocks is None:
            return

        self.player = self.starting_player
        self.blocks = set(self.starting_blocks)
        self.moves = 0
        self.history.clear()
        self.last_direction = Direction.DOWN
        self.won = self.is_won()

    def handle_key(self, key: str) -> None:
        key = key.lower()

        if key == "q":
            self.running = False
            return

        if key in {"w", "a", "s", "d"}:
            self.move(Direction(key))
            return

        if key == "u":
            self.undo()
            return

        if key == "r":
            self.restart()

    def render(self) -> None:
        print("\033[2J\033[H", end="")

        title_width = max(self.cols, 20)

        print("=" * title_width)
        print("SOKOBAN")
        print("=" * title_width)
        print()

        for row in range(self.rows):
            cells = []

            for col in range(self.cols):
                position = Position(row, col)

                if position in self.walls:
                    cell = WALL_SYMBOL

                elif position == self.player:
                    cell = PLAYER_SYMBOLS[self.last_direction]

                elif position in self.blocks:
                    if position in self.targets:
                        cell = BLOCK_ON_TARGET_SYMBOL
                    else:
                        cell = BLOCK_SYMBOL

                elif position in self.targets:
                    cell = TARGET_SYMBOL

                else:
                    cell = FLOOR_SYMBOL

                cells.append(cell)

            print(" ".join(cells))

        print()
        print(f"Moves: {self.moves}")
        print()
        print("+--------------+------------+---------------+-----------+")
        print("| WASD - Move  |  U - Undo  |  R - Restart  |  Q - Quit |")
        print("+--------------+------------+---------------+-----------+")

        if self.won:
            print()
            print("YOU WIN!")


def load_levels() -> dict[int, str]:
    levels: dict[int, str] = {}

    if not LEVELS_DIR.exists():
        raise FileNotFoundError(f"Levels directory not found: {LEVELS_DIR}")

    for file in LEVELS_DIR.glob("level*.txt"):
        if not file.is_file():
            continue

        try:
            level_number = int(file.stem[5:])
        except ValueError:
            continue

        levels[level_number] = file.read_text(encoding="utf-8").rstrip("\n")

    if not levels:
        raise RuntimeError(f"No level files found in {LEVELS_DIR}")

    return levels


LEVELS = load_levels()


def create_game(level: int) -> Game:
    try:
        level_data = LEVELS[level]
    except KeyError:
        raise ValueError(f"Level {level} does not exist")

    return parse_level(level_data)


def parse_level(level_data: str) -> Game:
    """
    Parse a Sokoban level.

    Supported characters:

        #  wall
        .  target
        $  block
        @  player
        x  block on target
        space  empty floor

    Leading/trailing spaces are preserved because they define the shape
    of irregular Sokoban levels.
    """

    # Remove only newline characters. Do not strip spaces.
    lines = level_data.splitlines()

    if not lines:
        raise ValueError("Level is empty")

    rows = len(lines)
    cols = max(len(line) for line in lines)

    player: Position | None = None
    blocks: set[Position] = set()
    targets: set[Position] = set()
    walls: set[Position] = set()

    valid_characters = {"#", ".", "$", "@", "x", " "}

    for row, line in enumerate(lines):
        for col in range(cols):
            # Shorter lines are padded with floor.
            char = line[col] if col < len(line) else " "

            if char not in valid_characters:
                raise ValueError(
                    f"Invalid character {char!r} at row {row + 1}, column {col + 1}"
                )

            position = Position(row, col)

            match char:
                case "#":
                    walls.add(position)

                case ".":
                    targets.add(position)

                case "$":
                    blocks.add(position)

                case "@":
                    if player is not None:
                        raise ValueError("Level contains multiple players")

                    player = position

                case "x":
                    blocks.add(position)
                    targets.add(position)

                case " ":
                    pass

    if player is None:
        raise ValueError("Level does not contain a player (@)")

    if not blocks:
        raise ValueError("Level does not contain any blocks ($ or x)")

    if len(blocks) != len(targets):
        raise ValueError(
            f"Number of blocks ({len(blocks)}) does not match "
            f"number of targets ({len(targets)})"
        )

    if player in walls:
        raise ValueError("Player cannot be inside a wall")

    if blocks & walls:
        raise ValueError("A block cannot be inside a wall")

    if targets & walls:
        raise ValueError("A target cannot be inside a wall")

    return Game(
        rows=rows,
        cols=cols,
        player=player,
        blocks=blocks,
        targets=targets,
        walls=walls,
    )


def main() -> None:
    level_numbers = sorted(LEVELS)

    if not level_numbers:
        raise RuntimeError("No levels available")

    level_index = 0
    game = create_game(level_numbers[level_index])

    try:
        with raw_terminal():
            while game.running:
                while key_available():
                    key = read_key()
                    game.handle_key(key)

                game.render()

                if game.won:
                    time.sleep(1.0)

                    level_index += 1

                    # All levels completed.
                    if level_index >= len(level_numbers):
                        print()
                        print("ALL LEVELS COMPLETED!")
                        break

                    game = create_game(level_numbers[level_index])

                time.sleep(1 / FPS)

    except KeyboardInterrupt:
        pass

    finally:
        print("\033[0m\033[?25h", end="")
        print("\nGame ended.")


if __name__ == "__main__":
    main()
