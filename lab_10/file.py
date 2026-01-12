import math
import time
import os
from multiprocessing import Pool, cpu_count, freeze_support

# -------------------------
# Parametry testu (można zmieneić na duży przedział)
# -------------------------
L = 1_000_000
R = 2_000_000

# -------------------------
# Szybkie generowanie małych liczb pierwszych (do sqrt(max_n))
# -------------------------
def primes_up_to(n: int) -> list[int]:
    """Sito Eratostenesa do n (włącznie)."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    limit = int(math.isqrt(n))
    for p in range(2, limit + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start:n + 1:step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]

def is_prime_with_small_primes(k: int, small_primes: list[int]) -> bool:
    """Test pierwszości k używając listy małych liczb pierwszych."""
    if k < 2:
        return False
    for p in small_primes:
        if p * p > k:
            return True
        if k % p == 0:
            return k == p
    # jeśli small_primes nie dosięgały do sqrt(k) (teoretycznie nie powinno tu wejść)
    return True

# -------------------------
# Sekwencyjnie: Germain primes w [l, r]
# -------------------------
def germain_sequential(l: int, r: int) -> list[int]:
    # musimy testować też 2p+1, więc small primes do sqrt(2r+1)
    max_q = 2 * r + 1
    sp = primes_up_to(int(math.isqrt(max_q)) + 1)

    out = []
    for p in range(l, r + 1):
        if is_prime_with_small_primes(p, sp):
            q = 2 * p + 1
            if is_prime_with_small_primes(q, sp):
                out.append(p)
    return out

# -------------------------
# Równolegle: Pool + imap_unordered
# -------------------------
_SMALL_PRIMES = None  # ustawiane w initializerze Pool

def _init_worker(small_primes: list[int]):
    global _SMALL_PRIMES
    _SMALL_PRIMES = small_primes

def _germain_chunk(args: tuple[int, int]) -> list[int]:
    """Worker: zwraca listę Germain primes dla przedziału [a,b]."""
    a, b = args
    sp = _SMALL_PRIMES
    out = []
    for p in range(a, b + 1):
        if is_prime_with_small_primes(p, sp):
            q = 2 * p + 1
            if is_prime_with_small_primes(q, sp):
                out.append(p)
    return out

def split_into_chunks(l: int, r: int, chunk_size: int):
    a = l
    while a <= r:
        b = min(r, a + chunk_size - 1)
        yield (a, b)
        a = b + 1

def germain_parallel(l: int, r: int, processes: int, chunk_size: int) -> list[int]:
    max_q = 2 * r + 1
    sp = primes_up_to(int(math.isqrt(max_q)) + 1)

    tasks = list(split_into_chunks(l, r, chunk_size))

    with Pool(processes=processes, initializer=_init_worker, initargs=(sp,)) as pool:
        # imap_unordered -> wyniki spływają jak skończą
        results = pool.imap_unordered(_germain_chunk, tasks, chunksize=1)

        out = []
        for part in results:
            out.extend(part)

    out.sort()
    return out

# -------------------------
# Benchmark / pomiary
# -------------------------
def timed(fn, *args, **kwargs):
    t0 = time.perf_counter()
    res = fn(*args, **kwargs)
    t1 = time.perf_counter()
    return res, (t1 - t0)

def main():
    print(f"Przedział: [{L}, {R}]")
    print(f"CPU: {cpu_count()} (system widzi tyle rdzeni/wątków)")

    # 1) Sekwencyjnie
    seq_res, seq_t = timed(germain_sequential, L, R)
    print(f"\nSEKWENCYJNIE: {len(seq_res)} liczb Germain, czas = {seq_t:.4f} s")

    # 2) Równolegle - testy dla różnych liczby procesów i chunków
    # chunk_size reguluje liczbę podzadań: im mniejszy chunk, tym więcej zadań i narzutu.
    process_list = sorted(set([1, 2, 4, 6, 8, cpu_count()]))
    chunk_list = [5_000, 20_000, 50_000, 100_000]

    print("\nRÓWNOLEGLE (Pool + imap_unordered):")
    for p in process_list:
        for ch in chunk_list:
            par_res, par_t = timed(germain_parallel, L, R, processes=p, chunk_size=ch)
            ok = (par_res == seq_res)
            speedup = (seq_t / par_t) if par_t > 0 else float("inf")
            print(
                f"  proc={p:2d}, chunk={ch:6d} -> czas={par_t:.4f}s, "
                f"przyspieszenie={speedup:.2f}x, zgodne={ok}"
            )

if __name__ == "__main__":
    freeze_support()  # ważne na Windows
    main()
