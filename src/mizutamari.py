import cmd
from argparse import ArgumentParser
from collections.abc import Set
from dataclasses import dataclass
from itertools import combinations, product
from random import choice
from typing import IO

type Point = tuple[int, int]


@dataclass(frozen=True)
class Board:
    size: int
    player: int
    points: Set[Point] = frozenset()
    last: Point | None = None
    catch: tuple[Point, Point, Point] | None = None
    turn: int = 1


def check_concyclic(p: Point, p1: Point, p2: Point, p3: Point) -> bool:
    a, b = p
    d = [[(x * x + y * y) - (a * a + b * b), x - a, y - b] for x, y in (p1, p2, p3)]
    return (
        d[0][0] * d[1][1] * d[2][2]
        + d[0][1] * d[1][2] * d[2][0]
        + d[0][2] * d[1][0] * d[2][1]
    ) - (
        d[0][0] * d[1][2] * d[2][1]
        + d[0][1] * d[1][0] * d[2][2]
        + d[0][2] * d[1][1] * d[2][0]
    ) == 0


def find_concyclic(p: Point, ps: Set[Point]) -> tuple[Point, Point, Point] | None:
    for p1, p2, p3 in combinations(ps, 3):
        if check_concyclic(p, p1, p2, p3):
            return (p1, p2, p3)
    return None


def move(p: Point, b: Board) -> Board:
    points = b.points | {p}
    catch = find_concyclic(p, b.points)
    turn = ((b.turn + 1) if b.turn != b.player else 1) if catch is None else b.turn
    return Board(
        size=b.size,
        player=b.player,
        points=points,
        last=p,
        catch=catch,
        turn=turn,
    )


def is_end_board(b: Board) -> bool:
    return b.catch is not None


def get_points(b: Board) -> Set[Point]:
    return frozenset(product(range(1, b.size + 1), range(1, b.size + 1)))


def get_moves(b: Board) -> Set[Point]:
    return get_points(b) - b.points


def visualize(b: Board) -> str:
    blacks, whites = b.points, {b.last} | set(b.catch if b.catch is not None else ())
    labels = (str(i) for i in range(1, b.size + 1))
    string = "  " + " ".join(labels) + "\n"
    for i in range(1, b.size + 1):
        cells = (
            "◯" if (i, j) in whites else "●" if (i, j) in blacks else "+"
            for j in range(1, b.size + 1)
        )
        string += f"{i} " + " ".join(cells) + "\n"
    string += "\n"
    string += (
        f"Player {b.turn}'s turn.\n"
        if not is_end_board(b)
        else f"Game Set: Player {b.turn} lost.\n"
    )
    return string


def evaluate_board(b: Board, depth: int) -> list[float]:
    if is_end_board(b):
        return [-1.0 if i == b.turn else 1.0 for i in range(1, b.player + 1)]
    elif depth == 0:
        return [0.0] * b.player
    else:
        scores = [evaluate_board(move(p, b), depth - 1) for p in get_moves(b)]
        max_score = max(v[b.turn - 1] for v in scores)
        best_scores = [v for v in scores if v[b.turn - 1] == max_score]
        return [
            sum(score[i] for score in best_scores) / len(best_scores)
            for i in range(b.player)
        ]


def play_auto(b: Board, depth: int) -> Point:
    score_table = {p: evaluate_board(move(p, b), depth) for p in get_moves(b)}
    max_score = max(v[b.turn - 1] for v in score_table.values())
    return choice([p for p, v in score_table.items() if v[b.turn - 1] == max_score])


class Cli(cmd.Cmd):
    prompt = "> "

    def __init__(
        self,
        size: int,
        player: int,
        stdin: IO[str] | None = None,
        stdout: IO[str] | None = None,
    ) -> None:
        super().__init__(stdin=stdin, stdout=stdout)
        self.use_rawinput = stdin is None
        self.board = Board(size, player)

    def preloop(self) -> None:
        self.stdout.write(visualize(self.board))

    def postcmd(self, stop: bool, line: str) -> bool:
        self.stdout.write(visualize(self.board))
        return stop or is_end_board(self.board)

    def emptyline(self) -> bool:
        return False

    def do_EOF(self, arg: str) -> bool:  # noqa: N802
        return True

    def _move(self, p: Point) -> None:
        if p in get_moves(self.board):
            self.board = move(p, self.board)
        else:
            self.stdout.write(f"Cannot Move: {p[0]}{p[1]}\n")

    def do_move(self, arg: str) -> None:
        self._move((int(arg[0]), int(arg[1])))

    def do_auto(self, arg: str) -> None:
        self._move(play_auto(self.board, int(arg)))


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--size", "-s", type=int, default=9, choices=range(2, 10), help="Size of board"
    )
    parser.add_argument("--player", "-p", type=int, default=2, help="Number of player")
    args = parser.parse_args()
    Cli(args.size, args.player).cmdloop()


if __name__ == "__main__":
    main()
