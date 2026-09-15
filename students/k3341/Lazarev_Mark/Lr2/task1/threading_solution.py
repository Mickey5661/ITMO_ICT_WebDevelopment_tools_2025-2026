import threading
import time


N_TARGET = 10_000_000_000_000


N_DEMO = 10_000_000

NUM_THREADS = 4


results: dict[int, int] = {}
lock = threading.Lock()


def calculate_sum(start: int, end: int, thread_id: int) -> None:
    """
    Вычислить сумму чисел
    """
    partial = sum(range(start, end + 1))
    
    with lock:
        results[thread_id] = partial
    print(f"  Поток {thread_id}: sum({start}..{end}) = {partial}")


def main(n: int = N_DEMO) -> float:
    """Запустить вычисление суммы 1..n через NUM_THREADS потоков."""
    chunk = n // NUM_THREADS
    threads = []

    for i in range(NUM_THREADS):
        start = i * chunk + 1
        end = (i + 1) * chunk if i < NUM_THREADS - 1 else n
        t = threading.Thread(target=calculate_sum, args=(start, end, i))
        threads.append(t)

    print(f"[Threading] Запуск {NUM_THREADS} потоков, N = {n:,}")
    t0 = time.perf_counter()

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    elapsed = time.perf_counter() - t0
    total = sum(results.values())
    expected = n * (n + 1) // 2

    print(f"\n  Результат : {total:,}")
    print(f"  Ожидалось : {expected:,}")
    print(f"  Корректно : {total == expected}")
    print(f"  Время     : {elapsed:.4f} сек\n")
    return elapsed


if __name__ == "__main__":
    main()
