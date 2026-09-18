from __future__ import annotations

import os
import random
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import StrEnum

BOARD_SIZE = 9
FPS = 30


class Direction(StrEnum):
    UP = "w"
    LEFT = "a"
    DOWN = "s"
    RIGHT = "d"


PLAYER_SYMBOLS = {
    Direction.UP: "^",
    Direction.DOWN: "v",
    Direction.LEFT: "<",
    Direction.RIGHT: ">",
}


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


@dataclass
class Game:
    player: Position
    block: Position
    target: Position
    walls: set[Position] = field(default_factory=set)

    moves: int = 0
    running: bool = True
    won: bool = False

    last_direction: Direction = Direction.DOWN

    history: list[tuple[Position, Position, int, Direction]] = field(
        default_factory=list
    )

    starting_player: Position | None = None
    starting_block: Position | None = None

    def __post_init__(self) -> None:
        self.starting_player = self.player
        self.starting_block = self.block

    def is_inside(self, position: Position) -> bool:
        return 0 <= position.row < BOARD_SIZE and 0 <= position.col < BOARD_SIZE

    def is_wall(self, position: Position) -> bool:
        return position in self.walls

    def move(self, direction: Direction) -> None:
        new_player = self.player.moved(direction)

        if not self.is_inside(new_player) or self.is_wall(new_player):
            return

        # Player is moving into an empty cell.
        if new_player != self.block:
            self.save_state()

            self.player = new_player
            self.last_direction = direction
            self.moves += 1

            return

        new_block = self.block.moved(direction)

        if not self.is_inside(new_block) or self.is_wall(new_block):
            return

        self.save_state()

        self.player = new_player
        self.block = new_block
        self.last_direction = direction
        self.moves += 1

        if self.block == self.target:
            self.won = True

    def save_state(self) -> None:
        self.history.append(
            (
                self.player,
                self.block,
                self.moves,
                self.last_direction,
            )
        )

    def undo(self) -> None:
        if not self.history:
            return

        (
            self.player,
            self.block,
            self.moves,
            self.last_direction,
        ) = self.history.pop()

        self.won = self.block == self.target

    def restart(self) -> None:
        if self.starting_player is None or self.starting_block is None:
            return

        self.player = self.starting_player
        self.block = self.starting_block
        self.moves = 0
        self.history.clear()
        self.won = False

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
            return

    def render(self) -> None:
        print("\033[2J\033[H", end="")

        print("=" * (BOARD_SIZE * 2 - 1))
        print("SOKOBAN")
        print("=" * (BOARD_SIZE * 2 - 1))
        print()

        for row in range(BOARD_SIZE):
            cells = []

            for col in range(BOARD_SIZE):
                position = Position(row, col)

                if position == self.player:
                    cells.append(PLAYER_SYMBOLS[self.last_direction])

                elif position == self.block:
                    if position == self.target:
                        cells.append("@")
                    else:
                        cells.append("#")

                elif position == self.target:
                    cells.append("*")

                elif position in self.walls:
                    cells.append("\N{FULL BLOCK}")

                else:
                    cells.append(".")

            print(" ".join(cells))

        print()
        print(f"Moves: {self.moves}")
        print()
        print("WASD  Move    U  Undo    R  Restart    Q  Quit")

        if self.won:
            print()
            print("YOU WIN!")


def create_game(level: int = 1) -> Game:
    max_walls = (BOARD_SIZE * BOARD_SIZE) // 3
    wall_count = min(4 + level * 2, max_walls)

    positions = [
        Position(row, col) for row in range(BOARD_SIZE) for col in range(BOARD_SIZE)
    ]

    while True:
        player, block, target = random.sample(positions, 3)

        # Give the block some room around it.
        if block.row in {0, BOARD_SIZE - 1} or block.col in {0, BOARD_SIZE - 1}:
            continue

        available = [
            position
            for position in positions
            if position not in {player, block, target}
        ]

        walls = set(random.sample(available, wall_count))

        # Don't completely surround the player.
        neighbours = [player.moved(direction) for direction in Direction]

        free_neighbours = [
            position
            for position in neighbours
            if (
                0 <= position.row < BOARD_SIZE
                and 0 <= position.col < BOARD_SIZE
                and position not in walls
            )
        ]

        if not free_neighbours:
            continue

        return Game(
            player=player,
            block=block,
            target=target,
            walls=walls,
        )


def main() -> None:
    level = 1
    game = create_game(level)

    try:
        with raw_terminal():
            while game.running:
                while key_available():
                    key = read_key()
                    game.handle_key(key)

                game.render()

                if game.won:
                    time.sleep(1.0)

                    level += 1
                    game = create_game(level)

                time.sleep(1 / FPS)

    except KeyboardInterrupt:
        pass

    finally:
        # Ensure the terminal doesn't remain in an unusual state.
        # I chatGPT. lol
        print("\033[0m\033[?25h", end="")
        print("\nGame ended.")


if __name__ == "__main__":
    main()
