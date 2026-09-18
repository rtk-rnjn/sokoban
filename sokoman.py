from __future__ import annotations

import os
import random
from dataclasses import dataclass
from enum import StrEnum

BOARD_SIZE = 7


class Direction(StrEnum):
    UP = "w"
    LEFT = "a"
    DOWN = "s"
    RIGHT = "d"


@dataclass
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

    def is_inside(self, position: Position) -> bool:
        return 0 <= position.row < BOARD_SIZE and 0 <= position.col < BOARD_SIZE

    def move(self, direction: Direction) -> None:
        new_player = self.player.moved(direction)

        # Player cannot leave the board.
        if not self.is_inside(new_player):
            return

        # Player is not pushing the block.
        if new_player != self.block:
            self.player = new_player
            return

        # Player is pushing the block.
        new_block = self.block.moved(direction)

        # Block cannot leave the board.
        if not self.is_inside(new_block):
            return

        self.block = new_block
        self.player = new_player

    def display(self) -> None:
        clear_screen()

        for row in range(BOARD_SIZE):
            cells = []

            for col in range(BOARD_SIZE):
                position = Position(row, col)

                if position == self.player:
                    cells.append("^")
                elif position == self.block:
                    cells.append("#")
                elif position == self.target:
                    cells.append("*")
                else:
                    cells.append(".")

            print(" ".join(cells))

        print()
        print(f"Player: ({self.player.row}, {self.player.col})")
        print(f"Block:  ({self.block.row}, {self.block.col})")
        print(f"Target: ({self.target.row}, {self.target.col})")


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def create_game() -> Game:
    while True:
        player = Position(
            random.randrange(BOARD_SIZE),
            random.randrange(BOARD_SIZE),
        )

        block = Position(
            random.randrange(1, BOARD_SIZE - 1),
            random.randrange(1, BOARD_SIZE - 1),
        )

        target = Position(
            random.randrange(BOARD_SIZE),
            random.randrange(BOARD_SIZE),
        )

        if len({(player.row, player.col), (block.row, block.col), (target.row, target.col)}) == 3:
            return Game(player, block, target)


def main() -> None:
    game = create_game()
    game.display()

    while True:
        command = (
            input(
                "\nEnter command (w/a/s/d, q to quit): ",
            )
            .strip()
            .lower()
        )

        if command in {"q", "quit"}:
            print("Game ended.")
            return

        try:
            direction = Direction(command)
        except ValueError:
            print("Invalid command. Use w, a, s, d, or q.")
            continue

        game.move(direction)
        game.display()

        if game.block == game.target:
            print("\nYOU WIN")
            return


if __name__ == "__main__":
    main()
