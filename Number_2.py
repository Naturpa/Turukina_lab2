import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QDateTime, Qt
from PyQt5.QtGui import QFont


class DailyPlanner(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('daily_planner.ui', self)

        # Настройка фиксированного размера окна
        self.setFixedSize(800, 600)

        # Подключение обработчиков кнопок
        self.addButton.clicked.connect(self.add_event)
        self.deleteButton.clicked.connect(self.delete_event)
        self.clearButton.clicked.connect(self.clear_events)

        # Инициализация списка событий
        self.events = []

        # Настройка шрифта для списка событий
        font = QFont('Courier New', 10)
        self.eventsList.setFont(font)

    def add_event(self):
        """Добавление нового события"""
        event_name = self.eventNameEdit.text().strip()

        if not event_name:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите название события!")
            return

        # Получаем выбранную дату и время
        selected_date = self.calendarWidget.selectedDate()
        selected_time = self.timeEdit.time()

        # Создаем объект datetime
        event_datetime = QDateTime(selected_date, selected_time)

        # Добавляем событие в список
        event_data = {
            'datetime': event_datetime,
            'name': event_name,
            'display_text': f"{event_datetime.toString('dd.MM.yyyy HH:mm')} - {event_name}"
        }

        self.events.append(event_data)

        # Сортируем события по дате
        self.events.sort(key=lambda x: x['datetime'])

        # Обновляем список
        self.update_events_list()

        # Очищаем поле ввода
        self.eventNameEdit.clear()

        QtWidgets.QMessageBox.information(self, "Успех", "Событие добавлено!")

    def delete_event(self):
        """Удаление выбранного события"""
        current_row = self.eventsList.currentRow()

        if current_row == -1:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите событие для удаления!")
            return

        # Удаляем событие из списка
        del self.events[current_row]

        # Обновляем список
        self.update_events_list()

        QtWidgets.QMessageBox.information(self, "Успех", "Событие удалено!")

    def clear_events(self):
        """Очистка всех событий"""
        if not self.events:
            QtWidgets.QMessageBox.information(self, "Информация", "Список событий уже пуст!")
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить все события?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.events.clear()
            self.update_events_list()
            QtWidgets.QMessageBox.information(self, "Успех", "Все события удалены!")

    def update_events_list(self):
        """Обновление списка событий"""
        self.eventsList.clear()

        for event in self.events:
            item = QtWidgets.QListWidgetItem(event['display_text'])
            self.eventsList.addItem(item)


def main():
    app = QtWidgets.QApplication(sys.argv)
    planner = DailyPlanner()
    planner.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()