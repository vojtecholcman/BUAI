"""Testy správnosti BFS řešení.

1) validate_path   – nalezená cesta je platná (začíná ve startu, končí v cíli,
                     kroky jsou mezi sousedními poli, nevede přes zeď)
2) brute_force     – na malých mřížkách projde VŠECHNY cesty (DFS) a najde
                     nejkratší; porovnáme délku i existenci s BFS
3) bellman_ford    – nezávislý výpočet vzdáleností opakovaným relaxováním
                     do ustálení; porovnáme s BFS na větších mřížkách
"""
from maze import generate_maze, bfs, FREE, WALL


def neighbors(i, n):
    x = i % n
    if i >= n:
        yield i - n
    if i < n * n - n:
        yield i + n
    if x > 0:
        yield i - 1
    if x < n - 1:
        yield i + 1


def validate_path(grid, n, path):
    assert path[0] == 0, "cesta nezačíná ve startu"
    assert path[-1] == n * n - 1, "cesta nekončí v cíli"
    for a, b in zip(path, path[1:]):
        assert b in set(neighbors(a, n)), f"kroky {a}->{b} nejsou sousední"
    for i in path:
        assert grid[i] == FREE, f"cesta vede přes zeď na poli {i}"
    assert len(set(path)) == len(path), "cesta navštíví pole dvakrát"


def brute_force(grid, n):
    """Vyčerpávající DFS přes všechny jednoduché cesty. Jen pro malé n!
    Vrátí délku nejkratší cesty v krocích, nebo None."""
    goal = n * n - 1
    best = [None]
    visited = bytearray(n * n)

    def dfs(i, d):
        if best[0] is not None and d >= best[0]:
            return  # ořez: delší už nebude lepší
        if i == goal:
            best[0] = d
            return
        visited[i] = 1
        for j in neighbors(i, n):
            if grid[j] == FREE and not visited[j]:
                dfs(j, d + 1)
        visited[i] = 0

    dfs(0, 0)
    return best[0]


def bellman_ford(grid, n):
    """Vzdálenost ze startu opakovaným relaxováním všech hran do ustálení.
    Úplně jiný princip než BFS (žádná fronta)."""
    INF = float("inf")
    dist = [INF] * (n * n)
    dist[0] = 0
    changed = True
    while changed:
        changed = False
        for i in range(n * n):
            if grid[i] == WALL or dist[i] == INF:
                continue
            for j in neighbors(i, n):
                if grid[j] == FREE and dist[i] + 1 < dist[j]:
                    dist[j] = dist[i] + 1
                    changed = True
    d = dist[n * n - 1]
    return None if d == INF else d


def bfs_len(grid, n):
    p = bfs(grid, n)
    if p is not None:
        validate_path(grid, n, p)
        return len(p) - 1
    return None


def test_brute_force(sizes=(3, 4, 5, 6), seeds=300):
    tested = with_path = 0
    for n in sizes:
        for s in range(seeds):
            g = generate_maze(n, seed=s)
            assert bfs_len(g, n) == brute_force(g, n), f"n={n}, seed={s}"
            tested += 1
            with_path += bfs_len(g, n) is not None
    print(f"brute force: {tested} instancí OK ({with_path} s cestou)")


def test_bellman_ford(sizes=(10, 20, 50, 100), seeds=100):
    tested = with_path = 0
    for n in sizes:
        for s in range(seeds):
            g = generate_maze(n, seed=s)
            assert bfs_len(g, n) == bellman_ford(g, n), f"n={n}, seed={s}"
            tested += 1
            with_path += bfs_len(g, n) is not None
    # explicitně i známé instance s cestou pro n = 100
    for s in (114, 175, 228, 359, 435):
        g = generate_maze(100, seed=s)
        assert bfs_len(g, 100) == bellman_ford(g, 100), f"n=100, seed={s}"
        tested += 1
        with_path += 1
    print(f"Bellman-Ford: {tested} instancí OK ({with_path} s cestou)")


def test_edge_cases():
    # bez překážek: délka = 2(n-1)
    for n in (2, 5, 50):
        assert bfs_len(bytearray(n * n), n) == 2 * (n - 1)
    # start zazděný
    n = 5
    g = bytearray(n * n)
    g[1] = g[n] = WALL
    assert bfs(g, n) is None
    # cíl zazděný
    g = bytearray(n * n)
    g[n * n - 2] = g[n * n - 1 - n] = WALL
    assert bfs(g, n) is None
    # přetečení přes okraj řádku: zeď ve sloupci 1 kromě posledního řádku;
    # cesta musí vést dolů sloupcem 0, ne "skokem" z konce řádku na začátek dalšího
    n = 4
    g = bytearray(n * n)
    for y in range(n - 1):
        g[y * n + 1] = WALL
    assert bfs_len(g, n) == 2 * (n - 1)
    print("hraniční případy: OK")


if __name__ == "__main__":
    test_edge_cases()
    test_brute_force()
    test_bellman_ford()
    print("Všechny testy prošly.")
