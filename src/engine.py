import cmd
from collections.abc import Callable, Set
from dataclasses import dataclass
from random import choice
from typing import IO


@dataclass(frozen=True)
class Game[S, M]:
    get_moves: Callable[[S], Set[M]]
    apply_move: Callable[[M, S], S]
    is_end: Callable[[S], bool]
    current_player: Callable[[S], int]
    player_count: Callable[[S], int]
    parse_move: Callable[[str], M]
    format_move: Callable[[M], str]
    render: Callable[[S], str]
    evaluate: Callable[[S], dict[int, float] | None]


def evaluate_board[S, M](game: Game[S, M], b: S, depth: int) -> dict[int, float]:
    score = game.evaluate(b)
    if score is not None:
        return score
    elif depth == 0:
        return dict.fromkeys(range(1, game.player_count(b) + 1), 0.0)
    else:
        current = game.current_player(b)
        scores = [
            evaluate_board(game, game.apply_move(m, b), depth - 1)
            for m in game.get_moves(b)
        ]
        max_score = max(v[current] for v in scores)
        best_scores = [v for v in scores if v[current] == max_score]
        return {
            i: sum(score[i] for score in best_scores) / len(best_scores)
            for i in range(1, game.player_count(b) + 1)
        }


def play_auto[S, M](game: Game[S, M], b: S, depth: int) -> M:
    score_table = {
        m: evaluate_board(game, game.apply_move(m, b), depth) for m in game.get_moves(b)
    }
    current = game.current_player(b)
    max_score = max(v[current] for v in score_table.values())
    return choice([m for m, v in score_table.items() if v[current] == max_score])


class Cli[S, M](cmd.Cmd):
    prompt = "> "

    def __init__(
        self,
        game: Game[S, M],
        initial: S,
        stdin: IO[str] | None = None,
        stdout: IO[str] | None = None,
    ) -> None:
        super().__init__(stdin=stdin, stdout=stdout)
        self.use_rawinput = stdin is None
        self.game = game
        self.board = initial

    def preloop(self) -> None:
        self.stdout.write(self.game.render(self.board))

    def postcmd(self, stop: bool, line: str) -> bool:
        self.stdout.write(self.game.render(self.board))
        return stop or self.game.is_end(self.board)

    def emptyline(self) -> bool:
        return False

    def do_EOF(self, arg: str) -> bool:  # noqa: N802
        return True

    def _move(self, m: M) -> None:
        if m in self.game.get_moves(self.board):
            self.board = self.game.apply_move(m, self.board)
        else:
            self.stdout.write(f"Cannot Move: {self.game.format_move(m)}\n")

    def do_move(self, arg: str) -> None:
        self._move(self.game.parse_move(arg))

    def do_auto(self, arg: str) -> None:
        self._move(play_auto(self.game, self.board, int(arg)))
