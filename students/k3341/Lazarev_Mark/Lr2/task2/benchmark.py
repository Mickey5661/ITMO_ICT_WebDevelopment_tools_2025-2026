"""
Сравнительный бенчмарк всех трёх подходов для Задачи 2.
Запускает threading, multiprocessing и async последовательно
и выводит таблицу с временем выполнения.
"""

import threading_parser
import multiprocessing_parser
import async_parser


def run_benchmark():
    print("  БЕНЧМАРК: параллельный парсинг веб-страниц")

    t_threading = threading_parser.main()
    t_multiprocessing = multiprocessing_parser.main()
    t_async = async_parser.main()


    print(f"  {'Подход':<25} {'Время (сек)':>12}")

    print(f"  {'Threading':<25} {t_threading:>12.4f}")
    print(f"  {'Multiprocessing':<25} {t_multiprocessing:>12.4f}")
    print(f"  {'Async / aiohttp':<25} {t_async:>12.4f}")


    fastest = min(t_threading, t_multiprocessing, t_async)
    names = {
        t_threading: "Threading",
        t_multiprocessing: "Multiprocessing",
        t_async: "Async / aiohttp",
    }
    print(f"\n  Победитель: {names[fastest]} ({fastest:.4f} сек)")


if __name__ == "__main__":
    run_benchmark()
