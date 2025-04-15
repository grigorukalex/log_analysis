def enlarge_file(input_file_path, output_file_path, target_size_gb):
    # Открываем исходный файл для чтения
    with open(input_file_path, 'rb') as input_file:
        # Читаем содержимое исходного файла
        content = input_file.read()

    # Рассчитываем размер нужного файла в байтах
    target_size_bytes = target_size_gb * 1024 * 1024

    # Открываем новый файл для записи
    with open(output_file_path, 'wb') as output_file:
        # Пишем содержимое исходного файла многократно до нужного размера
        while output_file.tell() < target_size_bytes:
            output_file.write(content)

    print(f"Файл успешно увеличен до {target_size_gb} МБ: {output_file_path}")


# Пример использования:
input_file = 'logs/app1.log'  # Исходный файл
output_file = 'logs/app2.log'  # Новый увеличенный файл
target_size_gb = 10  # Цель - 3 МБ

enlarge_file(input_file, output_file, target_size_gb)


