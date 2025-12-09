import threading
import math

def count_fragment_with_lock(L, counters, start, end, lock):
    for x in L[start:end]:
        with lock: 
            counters[x] += 1


def count_multi_threads_with_lock(L, max_value, threads_count):
    counters = [0] * (max_value + 1)
    lock = threading.Lock()

    length = len(L)
    step = math.ceil(length / threads_count)

    threads = []

    for i in range(threads_count):
        start = i * step
        end = min((i + 1) * step, length)

        t = threading.Thread(
            target=count_fragment_with_lock,
            args=(L, counters, start, end, lock)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return counters
import random

L = [random.randint(0, 200) for _ in range(500)]
max_value = max(L)

result = count_multi_threads_with_lock(L, max_value, threads_count=10)

print(result)
print("Suma:", sum(result))
