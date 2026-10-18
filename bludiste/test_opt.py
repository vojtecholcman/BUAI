"""Testy optimalizované verze: na stejných bludištích musí dát stejný
výsledek jako původní (už otestované) BFS z maze.py, a vrácená cesta
musí být platná."""
import math

import maze
import maze_opt as mo
from test_maze import validate_path


def check(grid1, n):
    expected = maze.bfs(grid1, n)
    g = mo.from_bytes(grid1, n)
    res = mo.bfs(g, n)
    if expected is None:
        assert res is None
        return False
    D, moves = res
    assert D == len(expected) - 1
    validate_path(grid1, n, list(mo.path_cells(n, moves)))
    return True


if __name__ == "__main__":
    tested = with_path = 0
    for n in (2, 3, 4, 5, 10, 30, 100):
        for s in range(300):
            with_path += check(maze.generate_maze(n, seed=s), n)
            tested += 1
    for s in (114, 175, 228, 359, 435):
        with_path += check(maze.generate_maze(100, seed=s), 100)
        tested += 1
    # bez překážek – dlouhé cesty přes všechny hodnoty bitu b
    for n in (2, 7, 64, 200):
        with_path += check(bytearray(n * n), n)
        tested += 1
    print(f"shoda s původním BFS: {tested} instancí OK ({with_path} s cestou)")

    # generátor: přesný počet překážek, volný start a cíl
    for n in (2, 3, 10, 101, 500):
        g = mo.generate_maze(n, seed=1)
        walls = sum(mo.get(g, i) == mo.WALL for i in range(n * n))
        assert walls == math.ceil(0.4 * n * n), (n, walls)
        assert mo.get(g, 0) == mo.FREE and mo.get(g, n * n - 1) == mo.FREE
    print("generátor: OK")
    print("Všechny testy prošly.")
