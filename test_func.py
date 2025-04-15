from func.func import split_list


def test_split_list_balanced():
    data = [str(i) for i in range(10)]
    parts = split_list(data, 3, min_lines=2)
    assert len(parts) == 4
    assert sum(len(p) for p in parts) == 10

    data = [str(i) for i in range(9)]
    parts = split_list(data, 3, min_lines=2)
    assert len(parts) == 3
    assert sum(len(p) for p in parts) == 9

def test_split_list_fallback():
    data = [str(i) for i in range(10)]
    parts = split_list(data, 4, min_lines=40)
    assert len(parts) == 1
    assert parts[0] == data
