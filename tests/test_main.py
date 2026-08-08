import io
from collections.abc import Set

from mizutamari import (
    Board,
    Cli,
    Point,
    evaluate_board,
    get_moves,
    is_end_board,
    move,
    play_auto,
    visualize,
)


def get_safe_moves(b: Board) -> Set[Point]:
    return frozenset(p for p in get_moves(b) if not is_end_board(move(p, b)))


def check_board_history(ps: list[Point], size: int, player_count: int):
    board = Board(size=size, player_count=player_count)
    assert board.last is None
    assert board.current_player == 1
    for p in ps:
        assert p in get_safe_moves(board)
        board = move(p, board)
        assert board.last == p
        assert not is_end_board(board)
    assert len(get_safe_moves(board)) == 0
    assert board.current_player == len(ps) % player_count + 1
    board = move(play_auto(board, 0), board)
    assert is_end_board(board)
    assert board.current_player == len(ps) % player_count + 1


def test_board_history_1():
    check_board_history([(4, 2), (3, 3), (4, 3), (2, 4), (1, 1), (4, 4)], 4, 4)


def test_board_history_2():
    check_board_history(
        [(6, 3), (1, 5), (5, 6), (1, 1), (2, 5), (6, 6), (2, 2), (4, 6), (5, 4)], 6, 2
    )


def test_board_history_3():
    check_board_history(
        [(7, 8), (4, 8), (5, 6), (4, 4), (7, 6), (1, 1), (8, 1), (7, 2)]
        + [(1, 2), (6, 8), (5, 3)],
        8,
        3,
    )


def test_board_history_4():
    check_board_history(
        [(7, 4), (7, 6), (9, 6), (1, 2), (8, 5), (7, 8), (5, 5), (3, 3)]
        + [(1, 9), (3, 1), (6, 1), (5, 3)],
        9,
        5,
    )


def test_board_visualize_1():
    assert (
        visualize(
            Board(
                size=4,
                player_count=4,
                points=frozenset([(4, 2), (3, 3), (4, 3), (2, 4), (1, 1), (4, 4)]),
                last=(4, 4),
                current_player=1,
            )
        )
        == """  1 2 3 4
1 ● + + +
2 + + + ●
3 + + ● +
4 + ● ● ◯

Player 1's turn.
"""
    )


def test_board_visualize_2():
    assert (
        visualize(
            Board(
                size=6,
                player_count=5,
                points=frozenset(
                    [(6, 3), (1, 5), (5, 6), (1, 1), (2, 5), (6, 6), (2, 2), (4, 6)]
                    + [(5, 4)]
                ),
                last=(5, 4),
                current_player=3,
            )
        )
        == """  1 2 3 4 5 6
1 ● + + + ● +
2 + ● + + ● +
3 + + + + + +
4 + + + + + ●
5 + + + ◯ + ●
6 + + ● + + ●

Player 3's turn.
"""
    )


def test_board_visualize_3():
    assert (
        visualize(
            Board(
                size=8,
                player_count=2,
                points=frozenset(
                    [(7, 8), (4, 8), (5, 6), (4, 4), (7, 6), (1, 1), (8, 1), (7, 2)]
                    + [(1, 2), (6, 8), (5, 3)],
                ),
                last=(5, 3),
                current_player=1,
            )
        )
        == """  1 2 3 4 5 6 7 8
1 ● ● + + + + + +
2 + + + + + + + +
3 + + + + + + + +
4 + + + ● + + + ●
5 + + ◯ + + ● + +
6 + + + + + + + ●
7 + ● + + + ● + ●
8 ● + + + + + + +

Player 1's turn.
"""
    )


def test_board_visualize_4():
    assert (
        visualize(
            Board(
                size=9,
                player_count=5,
                points=frozenset(
                    [(7, 4), (7, 6), (9, 6), (1, 2), (8, 5), (7, 8), (5, 5), (3, 3)]
                    + [(1, 9), (3, 1), (6, 1), (5, 3)],
                ),
                last=(5, 3),
                current_player=2,
            )
        )
        == """  1 2 3 4 5 6 7 8 9
1 + ● + + + + + + ●
2 + + + + + + + + +
3 ● + ● + + + + + +
4 + + + + + + + + +
5 + + ◯ + ● + + + +
6 ● + + + + + + + +
7 + + + ● + ● + ● +
8 + + + + ● + + + +
9 + + + + + ● + + +

Player 2's turn.
"""
    )


def test_board_visualize_5():
    assert (
        visualize(
            Board(
                size=9,
                player_count=3,
                points=frozenset(
                    [(7, 4), (7, 6), (9, 6), (1, 2), (8, 5), (7, 8), (5, 5), (3, 3)]
                    + [(1, 9), (3, 1), (6, 1), (5, 3), (7, 2)],
                ),
                last=(7, 2),
                catch=((7, 4), (7, 6), (7, 8)),
                current_player=2,
            )
        )
        == """  1 2 3 4 5 6 7 8 9
1 + ● + + + + + + ●
2 + + + + + + + + +
3 ● + ● + + + + + +
4 + + + + + + + + +
5 + + ● + ● + + + +
6 ● + + + + + + + +
7 + ◯ + ◯ + ◯ + ◯ +
8 + + + + ● + + + +
9 + + + + + ● + + +

Game Set: Player 2 lost.
"""
    )


def check_cmdcli(input_text: str, size: int, player_count: int, depth: int = 0) -> str:
    stdout = io.StringIO()
    Cli(
        size, player_count, depth, stdin=io.StringIO(input_text), stdout=stdout
    ).cmdloop()
    return stdout.getvalue()


def test_cmdcli_1():
    output = check_cmdcli("move 45\nmove 56\nmove 67\nmove 78\n", 9, 2)
    assert "Cannot Move" not in output
    assert "Game Set: Player 2 lost." in output


def test_cmdcli_2():
    output = check_cmdcli("move 45\nmove 48\nmove 65\nmove 68\n", 9, 3)
    assert "Cannot Move" not in output
    assert "Game Set: Player 1 lost." in output


def test_cmdcli_3():
    output = check_cmdcli(
        "move 45\nmove 11\nmove 12\nmove 11\nmove 21\nmove 22\n", 2, 2
    )
    assert "Cannot Move: 45" in output
    assert "Cannot Move: 11" in output
    assert "Game Set: Player 2 lost." in output


def test_cmdcli_4():
    size = 4
    output = check_cmdcli("auto\n" * (size * size), size, 6)
    assert "Cannot Move" not in output


def test_cmdcli_5():
    output = check_cmdcli("move 45\nmove 56\nUC\nmove 67\nmove 78\n", 9, 4)
    assert "Unknown syntax: UC" in output
    assert "Cannot Move" not in output
    assert "Game Set: Player 4 lost." in output


def test_cmdcli_pass_always_fails():
    output = check_cmdcli("pass\nmove 45\nmove 56\nmove 67\nmove 78\n", 9, 2)
    assert "Cannot Pass" in output
    assert "Cannot Move" not in output
    assert "Game Set: Player 2 lost." in output


def test_cmdcli_pass_does_not_change_turn():
    output = check_cmdcli("pass\n", 9, 2)
    assert output.count("Player 1's turn.") == 3


def test_cmdcli_eof():
    output = check_cmdcli("move 45\n", 9, 2)
    assert "Game Set" not in output


def check_random(b: Board, p: Point | None):
    assert p in get_safe_moves(b) or (len(get_safe_moves(b)) == 0 and p in get_moves(b))


def test_random_1():
    board = Board(size=4, player_count=3)
    check_random(board, play_auto(board, 0))


def test_random_2():
    board = Board(
        size=4,
        player_count=6,
        points=frozenset(
            [(4, 2), (3, 3), (4, 3), (2, 4), (1, 1), (4, 4)],
        ),
        last=(4, 4),
    )
    check_random(board, play_auto(board, 0))


def test_random_3():
    board = Board(
        size=8,
        player_count=15,
        points=frozenset(
            [(7, 8), (4, 8), (5, 6), (4, 4), (7, 6), (1, 1), (8, 1), (7, 2)]
        ),
        last=(7, 2),
    )
    check_random(board, play_auto(board, 0))


def test_evaluate_board_forced_loss_shallow_depth():
    board = Board(size=2, player_count=2)
    for depth in range(4):
        assert evaluate_board(board, depth) == {1: 0.0, 2: 0.0}


def test_evaluate_board_forced_loss_full_depth():
    board = Board(size=2, player_count=2)
    assert evaluate_board(board, 4) == {1: 1.0, 2: -1.0}
    assert evaluate_board(board, 5) == {1: 1.0, 2: -1.0}


def test_evaluate_board_avoids_self_catch():
    board = Board(
        size=3,
        player_count=2,
        points=frozenset({(1, 1), (1, 2), (2, 1)}),
        last=(2, 1),
        current_player=1,
    )
    assert evaluate_board(board, 0) == {1: 0.0, 2: 0.0}
    assert evaluate_board(board, 1) == {1: 0.0, 2: 0.0}


def test_play_auto_avoids_self_catch():
    board = Board(
        size=3,
        player_count=2,
        points=frozenset({(1, 1), (1, 2), (2, 1)}),
        last=(2, 1),
        current_player=1,
    )
    safe_moves = {(1, 3), (2, 3), (3, 1), (3, 2), (3, 3)}
    for _ in range(20):
        assert play_auto(board, 0) in safe_moves


def test_play_auto_forced_move():
    board = Board(
        size=2,
        player_count=2,
        points=frozenset({(1, 1), (1, 2), (2, 1)}),
        last=(2, 1),
        current_player=2,
    )
    for _ in range(20):
        assert play_auto(board, 0) == (2, 2)


def check_autoplay(size: int, depth_p: int, depth_o: int, r_l: int, r_h: int):
    w = 0
    for _ in range(500):
        b = Board(size, 2)
        while not is_end_board(b):
            depth = depth_p if b.current_player == 1 else depth_o
            b = move(play_auto(b, depth), b)
        w += 1 if b.current_player == 2 else 0
    for _ in range(500):
        b = Board(size, 2)
        while not is_end_board(b):
            depth = depth_o if b.current_player == 1 else depth_p
            b = move(play_auto(b, depth), b)
        w += 1 if b.current_player == 1 else 0
    assert r_l < w < r_h


def test_autoplay_1():
    check_autoplay(4, 0, 1, 250, 350)


def test_autoplay_2():
    check_autoplay(4, 1, 2, 170, 270)


def test_autoplay_3():
    check_autoplay(5, 0, 1, 270, 370)
