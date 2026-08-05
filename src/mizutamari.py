from argparse import ArgumentParser
from collections.abc import Set
from dataclasses import dataclass
from itertools import combinations, product
from typing import IO

from engine import Agent, Game
from engine import Cli as EngineCli
from engine import evaluate_board as engine_evaluate_board
from engine import play_auto as engine_play_auto

type Point = tuple[int, int]


@dataclass(frozen=True)
class Board:
    size: int
    player_count: int
    points: Set[Point] = frozenset()
    last: Point | None = None
    catch: tuple[Point, Point, Point] | None = None
    current_player: int = 1


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
    current_player = (
        ((b.current_player + 1) if b.current_player != b.player_count else 1)
        if catch is None
        else b.current_player
    )
    return Board(
        size=b.size,
        player_count=b.player_count,
        points=points,
        last=p,
        catch=catch,
        current_player=current_player,
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
        f"Player {b.current_player}'s turn.\n"
        if not is_end_board(b)
        else f"Game Set: Player {b.current_player} lost.\n"
    )
    return string


def evaluate_state(b: Board) -> dict[int, float] | None:
    if not is_end_board(b):
        return None
    return {
        i: -1.0 if i == b.current_player else 1.0 for i in range(1, b.player_count + 1)
    }


KYOUEN_GAME: Game[Board, Point] = Game(
    get_moves=get_moves,
    apply_move=move,
    is_end=is_end_board,
    current_player=lambda b: b.current_player,
    player_count=lambda b: b.player_count,
    parse_move=lambda arg: (int(arg[0]), int(arg[1])),
    format_move=lambda p: f"{p[0]}{p[1]}",
    render=visualize,
)


def evaluate_board(b: Board, depth: int) -> dict[int, float]:
    return engine_evaluate_board(KYOUEN_GAME, Agent(evaluate_state, depth), b)


def play_auto(b: Board, depth: int) -> Point:
    return engine_play_auto(KYOUEN_GAME, Agent(evaluate_state, depth), b)


class Cli(EngineCli[Board, Point]):
    def __init__(
        self,
        size: int,
        player_count: int,
        depth: int,
        stdin: IO[str] | None = None,
        stdout: IO[str] | None = None,
    ) -> None:
        super().__init__(
            KYOUEN_GAME,
            Agent(evaluate_state, depth),
            Board(size, player_count),
            stdin=stdin,
            stdout=stdout,
        )


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--size", "-s", type=int, default=9, choices=range(2, 10), help="Size of board"
    )
    parser.add_argument(
        "--players", "-p", type=int, default=2, help="Number of players"
    )
    parser.add_argument(
        "--depth", "-d", type=int, default=0, help="Search depth for auto command"
    )
    args = parser.parse_args()
    Cli(args.size, args.players, args.depth).cmdloop()


if __name__ == "__main__":
    main()
