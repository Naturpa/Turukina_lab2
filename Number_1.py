import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt


class TextFlagApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('text_flag.ui', self)

        # Настройка фиксированного размера окна
        self.setFixedSize(450, 550)

        # Подключение обработчика кнопки
        self.drawButton.clicked.connect(self.draw_flag)

        # Словарь для соответствия кнопок и цветов
        self.color_mapping = {
            'red': 'Красный',
            'blue': 'Синий',
            'green': 'Зеленый',
            'yellow': 'Желтый',
            'white': 'Белый'
        }

    def get_selected_color(self, button_group):
        """Получить выбранный цвет из группы кнопок"""
        for button in button_group:
            if button.isChecked():
                # Извлекаем название цвета из имени кнопки
                color_name = button.objectName().split('_')[1]
                return self.color_mapping.get(color_name, 'Неизвестный')
        return 'Не выбран'

    def draw_flag(self):
        """Обработчик нажатия кнопки 'Нарисовать'"""
        # Получаем цвета для каждой полосы
        top_buttons = [self.top_red, self.top_blue, self.top_green, self.top_yellow, self.top_white]
        middle_buttons = [self.middle_red, self.middle_blue, self.middle_green, self.middle_yellow, self.middle_white]
        bottom_buttons = [self.bottom_red, self.bottom_blue, self.bottom_green, self.bottom_yellow, self.bottom_white]

        top_color = self.get_selected_color(top_buttons)
        middle_color = self.get_selected_color(middle_buttons)
        bottom_color = self.get_selected_color(bottom_buttons)

        # Формируем результат
        result_text = f"{top_color}, {middle_color}, {bottom_color}"

        # Обновляем текст метки
        self.resultLabel.setText(result_text)


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = TextFlagApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()