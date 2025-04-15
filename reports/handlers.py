import _io
import re
from collections import defaultdict
from typing import List, DefaultDict, NoReturn
from multiprocessing import Pool

from func.func import split_list

# Аннотация типов
Report = DefaultDict[str, DefaultDict[str, int]]
Reports = List[Report]

# Регулярные выражения для поиска в строках
pattern_django_request = re.compile(r'django\.request:')
pattern_log_level = re.compile(r'\b(INFO|DEBUG|WARNING|ERROR|CRITICAL)\b')
pattern_request_path = re.compile(r'(/[^ ]*)')


def nested_defaultdict() -> DefaultDict[str, int]:
    return defaultdict(int)


# Составление отчета по текущему списку
def parse_lines(lines: List[str]) -> Report:
    # Хранилище для подсчёта
    counters: Report = defaultdict(nested_defaultdict)

    for line in lines:
        if not pattern_django_request.search(line):
            continue

        # Поиск уровня лога
        level_match = pattern_log_level.search(line)
        if not level_match:
            continue
        level: str = level_match.group(1)

        # Поиск пути запроса
        path_match = pattern_request_path.search(line)
        path: str = 'UNKNOWN'
        if path_match:
            path = path_match.group(1)

        # Увеличиваем счётчик
        counters[path][level] += 1

    return counters


def summary_report(counters_list: Reports) -> Report:
    merged_counters: Report = defaultdict(nested_defaultdict)

    if len(counters_list) > 1:
        # Перебираем все переданные отчёты
        for counters in counters_list:
            # Перебираем все пути и уровни в текущем отчёте
            for path, levels in counters.items():
                for level, count in levels.items():
                    # Добавляем значения из текущего отчёта в итоговый
                    merged_counters[path][level] += count
    else:
        if counters_list:   # Проверка на пустой список
            merged_counters = counters_list[0]

    return merged_counters


def generate_report(log: _io.TextIOWrapper, buffer_size: int = 1024 * 1024, num_proc: int = 5) -> Report:
    """
    :param log: файл
    :param buffer_size: по-умолчанию 1 МБ
    :param num_proc:    кол-во процессов
    """
    # Список отчётов по процессам и буферу
    counters_list: Reports = []

    # "Хвост" буфера
    remainder: str = ''

    # Определяем пул из n процессов
    with Pool(num_proc) as pool:
        chunk: str = log.read(buffer_size)
        while chunk:
            chunk = remainder + chunk
            lines: List[str] = chunk.split('\n')

            # Последняя строка может быть неполной — сохраняем её
            remainder = lines.pop()

            split_lines: List[List[str]] = split_list(lines, num_proc)

            results: Reports = pool.map(parse_lines, split_lines)
            counters_list.extend(results)

            chunk = log.read(buffer_size)

    # Обработка "хвоста"
    if remainder:
        results_remainder: Report = parse_lines([remainder])
        counters_list.append(results_remainder)

    merged_counters: Report = summary_report(counters_list)

    return merged_counters


def print_report(counters: Report) -> NoReturn:
    levels: List[str] = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    totals = defaultdict(int)
    table: str = ''

    for path in sorted(counters.keys()):
        table += f"{path:<30}\t"
        for lvl in levels:
            count: int = counters[path].get(lvl, 0)
            totals[lvl] += count
            table += f"{count:<10}\t"
        table += '\n'

    # Суммарная строка
    table += f"{'':<24}\t"
    for lvl in levels:
        table += f"{totals[lvl]:<10}\t"
    table += '\n'

    total_requests: int = sum(totals.values())
    print(f"Total requests: {total_requests}\n")
    print(f"{'HANDLER':<30}\t" + "\t".join(f"{lvl:<10}" for lvl in levels))
    print(table)
