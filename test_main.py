from unittest import mock
import sys
from io import StringIO
from main import run

@mock.patch("reports.handlers.generate_report")
@mock.patch("reports.handlers.print_report")
@mock.patch("reports.handlers.summary_report")
def test_run_multiple_logs(mock_summary, mock_print, mock_generate):
    # Создаём фейковые лог-файлы (TextIO)
    file1 = StringIO("django.request: INFO /api/v1/test/")
    file1.name = "log1.log"

    file2 = StringIO("django.request: DEBUG /api/v1/test/")
    file2.name = "log2.log"

    mock_generate.side_effect = [
        {'/api/v1/test/': {'INFO': 1}},
        {'/api/v1/test/': {'DEBUG': 1}},
    ]

    mock_summary.return_value = {
        '/api/v1/test/': {'INFO': 1, 'DEBUG': 1}
    }

    run([file1, file2], report_name='handlers')

    assert mock_generate.call_count == 2
    assert mock_summary.called
    assert mock_print.call_count == 3



# def test_main_with_two_logs(mock_summary, mock_print, mock_generate, tmp_path):
#     # Создание временных логов
#     log1 = tmp_path / "log1.log"
#     log2 = tmp_path / "log2.log"
#     log1.write_text("2025-03-28 12:09:16,000 INFO django.request: GET /api/v1/cart/ 204 OK [192.168.1.93]\n")
#     log2.write_text("2025-03-28 12:31:51,000 ERROR django.request: Internal Server Error: /api/v1/cart/ [192.168.1.90] - SuspiciousOperation: Invalid HTTP_HOST header\n")
#
#     log1.write_text("django.request: INFO /api/v1/test/\n")
#     log2.write_text("django.request: DEBUG /api/v1/test/\n")
#
#     # Заглушки возвращаемых значений
#     mock_generate.side_effect = [
#         {'/api/v1/cart/': {'INFO': 1}},
#         {'/api/v1/cart/': {'ERROR': 1}}
#     ]
#     mock_summary.return_value = {
#         '/api/v1/cart/': {'INFO': 1, 'DEBUG': 1}
#     }
#
#     # Подмена sys.argv
#     test_args = [
#         "main.py",
#         str(log1),
#         str(log2),
#         "--report", "handlers"
#     ]
#     with mock.patch.object(sys, 'argv', test_args):
#         import main  # 👈 запускаем main как модуль
#
#     # Проверки
#     assert mock_generate.call_count == 2
#     assert mock_summary.call_count == 1
#     assert mock_print.call_count == 3  # по одному на файл + итог
#
#     mock_generate.assert_any_call(mock.ANY)
#     mock_summary.assert_called_once()




