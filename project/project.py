import os

import csv


class PriceMachine():

    def __init__(self):
        self.data = []
        self.result = ''
        self.name_length = 0

    def load_prices(self, file_path=''):
        """
            Сканирует указанный каталог. Ищет файлы со словом price в названии.
            В файле ищет столбцы с названием товара, ценой и весом.
            Допустимые названия для столбца с товаром:
                товар
                название
                наименование
                продукт

            Допустимые названия для столбца с ценой:
                розница
                цена

            Допустимые названия для столбца с весом (в кг.)
                вес
                масса
                фасовка
        """
        products_files = []
        current_dir = file_path if file_path else os.getcwd()

        # Перебираем все файлы в директории
        for filename in os.listdir(current_dir):
            if 'price' in filename.lower() and filename.endswith('.csv'):
                file_path = os.path.join(current_dir, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        csv_reader = csv.reader(file, delimiter=',')
                        headers = next(csv_reader)  # Читаем заголовки

                        # Получаем индексы нужных столбцов
                        product_index, price_index, weight_index = self._search_product_price_weight(headers)

                        if -1 in (product_index, price_index, weight_index):
                            print(f"Ошибка: не найдены необходимые столбцы в файле {filename}")
                            continue

                        # Читаем данные
                        for row in csv_reader:
                            if len(row) > max(product_index, price_index, weight_index):
                                try:
                                    name = row[product_index].strip()
                                    if not name:  # Пропускаем пустые строки
                                        continue

                                    price = float(row[price_index].strip())
                                    weight = float(row[weight_index].strip())

                                    # Обновляем максимальную длину названия
                                    self.name_length = max(self.name_length, len(name))

                                    # Добавляем данные в общий список
                                    self.data.append({
                                        'name': name,
                                        'price': price,
                                        'weight': weight,
                                        'file': filename,
                                        'price_per_kg': round(price / weight, 2)
                                    })

                                except (ValueError, IndexError) as e:
                                    print(f"Ошибка обработки строки в файле {filename}: {e}")
                                    continue

                        products_files.append(filename)

                except Exception as e:
                    print(f"Ошибка при обработке файла {filename}: {e}")
                    continue

        return products_files

    def _search_product_price_weight(self, headers):
        """
            Возвращает номера столбцов
        """
        product_index = -1
        price_index = -1
        weight_index = -1

        # Приведем заголовки к нижнему регистру для поиска
        headers = [str(h).lower().strip() for h in headers]

        # Ищем индекс названия товара
        product_names = ['название', 'продукт', 'товар', 'наименование']
        for index, header in enumerate(headers):
            if header in product_names:
                product_index = index
                break

        # Ищем индекс цены
        price_names = ['цена', 'розница']
        for index, header in enumerate(headers):
            if header in price_names:
                price_index = index
                break

        # Ищем индекс веса
        weight_names = ['фасовка', 'масса', 'вес']
        for index, header in enumerate(headers):
            if header in weight_names:
                weight_index = index
                break

        return product_index, price_index, weight_index

    def export_to_html(self, fname='output.html'):
        # Сортируем все данные по цене за килограмм
        sorted_data = sorted(self.data, key=lambda x: x['price_per_kg'])

        html_content = '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Позиции продуктов</title>
            <style>
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                tr:nth-child(even) { background-color: #f9f9f9; }
            </style>
        </head>
        <body>
            <table>
                <tr>
                    <th>Номер</th>
                    <th>Название</th>
                    <th>Цена</th>
                    <th>Фасовка</th>
                    <th>Файл</th>
                    <th>Цена за кг.</th>
                </tr>
        '''

        for i, item in enumerate(sorted_data, 1):
            html_content += f'''
                <tr>
                    <td>{i}</td>
                    <td>{item['name']}</td>
                    <td>{item['price']:.2f}</td>
                    <td>{item['weight']:.1f}</td>
                    <td>{item['price_per_kg']:.2f}</td>
                </tr>
            '''

        html_content += '''
            </table>
        </body>
        </html>
        '''

        with open(fname, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return html_content

    def find_text(self, text):
        found_items = [item for item in self.data
                       if text.lower() in item['name'].lower()]

        # Сортируем по цене за килограмм
        found_items.sort(key=lambda x: x['price_per_kg'])

        # Форматируем и выводим результаты
        if found_items:
            print("\n{:<4}  {:<30}  {:>8}  {:<12}  {:>6}  {:>10}".format(
                "№", "Наименование", "цена",  "вес", "файл", "цена за кг."))
            print("-" * 80)

            for i, item in enumerate(found_items, 1):
                print("{:<4} {:<30} {:>8.2f} {:>6.1f} {:<12} {:>10.2f}".format(
                    i,
                    item['name'][:30],
                    item['price'],
                    item['weight'],
                    item['file'],
                    item['price_per_kg']
                ))

        return found_items


if __name__ == "__main__":
    pm = PriceMachine()

    # Загружаем данные
    processed_files = pm.load_prices()
    # print(f"Обработано файлов: {len(processed_files)}")

    # Экспортируем данные в HTML
    # export_choice = input("Хотите экспортировать данные в HTML файл? (да/нет): ")
    # if export_choice.lower() == 'да':
    #     output_file = input("Введите имя выходного HTML файла (например, output.html): ")
    #     pm.export_to_html(output_file)

    # Основной цикл работы с пользователем
    while True:
        search_text = input("\nВведите текст для поиска (или 'exit' для выхода): ").strip()

        if search_text.lower() == 'exit' and search_text.lower == 'выход':
            print("\nРабота программы завершена.")
            break



        found_items = pm.find_text(search_text)
        if not found_items:
            print("Ничего не найдено.")

        # Экспортируем данные в HTML
        export_choice = input("Хотите экспортировать данные в HTML файл? (да/нет): ")
        if export_choice.lower() == 'да':
            output_file = input("Введите имя выходного HTML файла (например, output.html): ")
            pm.export_to_html(output_file)



