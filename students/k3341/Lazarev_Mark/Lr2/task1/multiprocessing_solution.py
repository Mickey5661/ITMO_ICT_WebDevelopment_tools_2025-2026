import multiprocessing
import time

N_TARGET = 10_000_000_000_000
N_DEMO = 10_000_000
NUM_PROCESSES = 4


def calculate_sum(start: int, end: int) -> int:
    """
    Вычислить сумму целых чисел от start до end включительно.
    Эта функция выполняется в отдельном процессе.
    Возвращает результат, который Pool передаёт главному процессу через IPC.
    """
    return sum(range(start, end + 1))


def main(n: int = N_DEMO) -> float:
    """Запустить вычисление суммы 1..n через NUM_PROCESSES процессов."""
    chunk = n // NUM_PROCESSES
    ranges = []

    for i in range(NUM_PROCESSES):
        start = i * chunk + 1
        end = (i + 1) * chunk if i < NUM_PROCESSES - 1 else n
        ranges.append((start, end))

    print(f"[Multiprocessing] Запуск {NUM_PROCESSES} процессов, N = {n:,}")
    t0 = time.perf_counter()

    
    with multiprocessing.Pool(processes=NUM_PROCESSES) as pool:
        partial_sums = pool.starmap(calculate_sum, ranges)

    elapsed = time.perf_counter() - t0
    total = sum(partial_sums)
    expected = n * (n + 1) // 2

    print(f"  Результат : {total:,}")
    print(f"  Ожидалось : {expected:,}")
    print(f"  Корректно : {total == expected}")
    print(f"  Время     : {elapsed:.4f} сек\n")
    return elapsed


if __name__ == "__main__":
    main()
