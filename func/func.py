from typing import List


def split_list(lst: List[str], n: int, min_lines: int = 500) -> List[List[str]]:
    # Вычисляем длину каждой части
    num_lines = len(lst)
    chunk_size: int = num_lines // n
    remainder: int = num_lines % n

    parts: List[List[str]] = []

    if num_lines > min_lines:   # Если строк меньше минимального значения, то не делим список
        for start in range(0, num_lines - remainder, chunk_size):
            parts.append(lst[start:start + chunk_size])
        if remainder > 0:
            parts.append(lst[-remainder:])
        return parts
    else:
        return [lst]