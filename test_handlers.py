import pytest
from collections import defaultdict

from reports import handlers


@pytest.fixture
def log_lines():
    return """2025-03-28 12:13:12,000 INFO django.request: GET /api/v1/payments/ 201 OK [192.168.1.90]
2025-03-27 12:33:11,000 DEBUG django.request: GET /api/v1/shipping/ 200 OK [192.168.1.86]
2025-03-27 12:41:04,000 WARNING django.request: GET /api/v1/support/ 201 OK [192.168.1.53]
2025-03-27 12:26:19,000 ERROR django.request: GET /api/v1/reviews/ 201 OK [192.168.1.78]
2025-03-27 12:26:19,000 django.request: GET /api/v1/reviews/ 201 OK [192.168.1.78]
2025-03-27 12:36:13,000 CRITICAL django.request: GET /admin/dashboard/ 204 OK [192.168.1.13]
not a valid log line
""".splitlines()


def test_parse_lines(log_lines):
    result = handlers.parse_lines(log_lines)
    assert result['/api/v1/payments/']['INFO'] == 1
    assert result['/api/v1/shipping/']['DEBUG'] == 1
    assert result['/api/v1/reviews/']['ERROR'] == 1
    assert result['/api/v1/support/']['WARNING'] == 1
    assert result['/admin/dashboard/']['CRITICAL'] == 1
    assert 'not a valid log line' not in result


def test_summary_report_merge():
    report1: handlers.Report = defaultdict(lambda: defaultdict(int))

    report1['/api/v1/payments/']['INFO'] = 1
    report1['/api/v1/payments/']['DEBUG'] = 2
    report1['/api/v1/support/']['ERROR'] = 3

    report2: handlers.Report = defaultdict(lambda: defaultdict(int))

    report2['/api/v1/payments/']['INFO'] = 4
    report2['/api/v1/payments/']['WARNING'] = 1
    report2['/api/v1/dashboard/']['CRITICAL'] = 2

    merged = handlers.summary_report([report1, report2])
    assert merged['/api/v1/payments/']['INFO'] == 5
    assert merged['/api/v1/payments/']['DEBUG'] == 2
    assert merged['/api/v1/payments/']['WARNING'] == 1
    assert merged['/api/v1/support/']['ERROR'] == 3
    assert merged['/api/v1/dashboard/']['CRITICAL'] == 2

    report3: handlers.Report = defaultdict(lambda: defaultdict(int))

    report3['/api/v1/payments/']['INFO'] = 7

    merged = handlers.summary_report([report3])
    assert merged['/api/v1/payments/']['INFO'] == 7


def test_generate_report(log_lines, tmp_path):
    log_path = tmp_path / "log.txt"
    log_path.write_text("\n".join(log_lines))

    with open(log_path, 'r') as f:
        result = handlers.generate_report(f, buffer_size=128, num_proc=2)

    assert result['/api/v1/payments/']['INFO'] == 1
    assert result['/api/v1/shipping/']['DEBUG'] == 1
    assert result['/api/v1/support/']['WARNING'] == 1
    assert result['/api/v1/reviews/']['ERROR'] == 1
    assert result['/admin/dashboard/']['CRITICAL'] == 1


def test_print_report_output(capsys):
    counters: handlers.Report = defaultdict(lambda: defaultdict(int))

    counters['/api/v1/test/']['INFO'] = 3
    counters['/api/v1/test/']['ERROR'] = 2
    counters['/api/v1/orders/']['WARNING'] = 1
    counters['/api/v1/orders/']['CRITICAL'] = 1

    handlers.print_report(counters)

    captured = capsys.readouterr()
    output = captured.out

    # Проверяем наличие ключевых элементов
    assert "Total requests: 7" in output
    assert "HANDLER" in output
    assert "/api/v1/test/" in output
    assert "/api/v1/orders/" in output
    assert "INFO" in output
    assert "ERROR" in output
    assert "CRITICAL" in output