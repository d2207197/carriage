from carriage import Row, X


def test_basic():
    assert X.y(Row(x=2, y=3)) == 3
    assert X['x'](dict(x=4, y=5)) == 4
    assert (X + 3)(5) == 8
    assert (X - 2)(6) == 4
    assert (X * 3)(4) == 12
    assert (X / 2)(9) == 4.5
    assert (X // 2)(9) == 4
    assert (X % 3)(5) == 2
    assert (divmod(X, 3))(5) == (1, 2)
    assert (X**2)(4) == 16


def test_reflected():
    # assert X.y(Row(x=2, y=3)) == 3
    # assert X['x'](dict(x=4, y=5)) == 4
    assert (3 + X)(5) == 8
    assert (2 - X)(6) == -4
    assert (3 * X)(4) == 12
    assert (9 / X)(2) == 4.5
    assert (9 // X)(2) == 4
    assert (5 % X)(3) == 2
    assert (divmod(5, X))(3) == (1, 2)
    assert (2**X)(3) == 8


def test_multiple_X():
    assert (X.y + X.x)(Row(x=2, y=3)) == 5
    assert (X['x'] + X['y'])(dict(x=2, y=3)) == 5
    assert (X + X)(5) == 10
    assert (X - X)(5) == 0
    assert (X * X)(5) == 25
    assert (X / X)(5) == 1
    assert (X.y / X.x)(Row(x=2, y=3)) == 1.5
    assert (X.y // X.x)(Row(x=2, y=3)) == 1
    assert (X.y % X.x)(Row(x=3, y=5)) == 2
    assert (divmod(X.y, X.x))(Row(x=3, y=5)) == (1, 2)
    assert (X**X)(3) == 27
