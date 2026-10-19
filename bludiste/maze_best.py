"""
Délka nejkratší cesty v bludišti N x N (implicitní, 10 % překážek).

Dolní mez délky je Manhattanská vzdálenost 2*(N-1). Pokud se najde cesta jen
dolů/doprava, má právě tuto délku, a je tedy PROKAZATELNĚ nejkratší.
Cesta se neukládá jako seznam bodů: pamatuje se jen 1 bajt (směr) na krok
a množina slepých uliček. Bludiště samotné se nikdy nevytváří v paměti.

Vrací délku, nebo None, pokud se to touto metodou nepodařilo prokázat
(v tom případě je skutečná délka větší než 2*(N-1) nebo cesta neexistuje).
"""
import time

MASK = (1 << 64) - 1
C1 = 0x9E3779B97F4A7C15
C2 = 0xD6E8FEB86659FD93


def make_blocked(n, seed=12345, density=0.10):
    threshold = int(density * (1 << 64))
    target = n * n - 1

    def blocked(idx):
        if idx == 0 or idx == target:
            return False
        h = ((idx ^ seed) * C1) & MASK
        h ^= h >> 32
        h = (h * C2) & MASK
        h ^= h >> 29
        return h < threshold

    return blocked


def shortest_length(n, seed=12345, density=0.10, limit_factor=50):
    blocked = make_blocked(n, seed, density)
    n1 = n - 1
    limit = limit_factor * n
    dirs = bytearray()          # 0 = dolů, 1 = doprava
    dead = set()                # slepé uličky (idx = x*n + y)
    x = y = 0
    t = 0                       # kolikátou možnost v aktuální buňce zkoušíme
    steps = 0

    while True:
        if x == n1 and y == n1:
            return len(dirs)    # == 2*(n-1) -> optimální
        steps += 1
        if steps > limit:
            return None

        first = 0 if x <= y else 1      # držet se diagonály
        advanced = False
        while t < 2:
            d = first if t == 0 else 1 - first
            t += 1
            if d == 0:
                if x == n1:
                    continue
                nx, ny = x + 1, y
            else:
                if y == n1:
                    continue
                nx, ny = x, y + 1
            idx = nx * n + ny
            if idx not in dead and not blocked(idx):
                dirs.append(d)
                x, y = nx, ny
                t = 0
                advanced = True
                break

        if not advanced:
            dead.add(x * n + y)
            if not dirs:
                return None
            d = dirs.pop()
            if d == 0:
                x -= 1
            else:
                y -= 1
            first = 0 if x <= y else 1
            t = (0 if d == first else 1) + 1


if __name__ == "__main__":
    import resource
    N = 31_622_777              # N*N ≈ 10^15 buněk
    print(f"N = {N:,}  ({N * N:.3e} buněk), 10 % překážek")
    t0 = time.perf_counter()
    length = shortest_length(N, seed=42)
    dt = time.perf_counter() - t0
    mem = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss // 1024
    if length is None:
        print("Optimální délku se touto metodou nepodařilo prokázat.")
    else:
        print(f"Délka nejkratší cesty: {length:,} kroků "
              f"(dolní mez {2 * (N - 1):,}, prokazatelně optimální)")
    print(f"Čas {dt:.1f} s, špičková paměť ~{mem} MB")
