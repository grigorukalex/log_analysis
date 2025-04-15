import _io
import argparse
from typing import List, Dict, Any, TextIO
import tracemalloc
import time
from reports import handlers

# НАСТРОЙКИ КОНФИГУРАЦИИ
REPORTS: Dict[str, Any] = {  # Названия отчётов
    'handlers': handlers,
}
BUFFER_SIZE: int = 1024 * 1024 * 100  # 100 MB Размер буфера для ограничения использования ОЗУ
THREADS: int = 5  # Кол-во процессов


def run(log_files: List[TextIO], report_name: str):
    report: Any = REPORTS[report_name]
    # Список отчётов по файлам
    counters_list: report.Reports = []

    for log in log_files:
        # Генерация отчёта по файлу лога
        counters: report.Report = report.generate_report(log, buffer_size=BUFFER_SIZE)
        counters_list.append(counters)
        print(f"Обработка файла лога: {log.name}")
        # report.print_report(counters)
    print()

    merged_counters: report.Report = report.summary_report(counters_list)
    # Вывод общего отчёта по всем файлам
    report.print_report(merged_counters)


def main() -> None:
    # Запускаем отслеживание памяти
    tracemalloc.start()
    # Замер времени выполнения
    start_time: float = time.perf_counter()

    report_keys: List[str] = list(REPORTS.keys())

    parser = argparse.ArgumentParser(description='Анализатор логов Django.')
    parser.add_argument('logs', nargs='+', type=argparse.FileType('r'), help='Пути к логам')
    parser.add_argument('--report', type=str, choices=report_keys, default='handlers', help='Тип отчёта')
    args = parser.parse_args()

    run(args.logs, args.report)

    # Получаем статистику по памяти
    current, peak = tracemalloc.get_traced_memory()
    print(f"Использовано памяти: {current / 1024 / 1024:.2f} MB")
    print(f"Пиковое использование: {peak / 1024 / 1024:.2f} MB")

    end_time: float = time.perf_counter()
    tracemalloc.stop()
    print(f"Время выполнения: {end_time - start_time:.2f} сек")


if __name__ == '__main__':
    main()