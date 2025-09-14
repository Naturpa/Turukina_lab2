import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class AddressBook(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('address_book.ui', self)

        # Настройка фиксированного размера окна
        self.setFixedSize(600, 500)

        # Подключение обработчиков кнопок
        self.addButton.clicked.connect(self.add_contact)
        self.clearButton.clicked.connect(self.clear_fields)
        self.deleteButton.clicked.connect(self.delete_contact)
        self.clearAllButton.clicked.connect(self.clear_all_contacts)

        # Подключение обработчика нажатия Enter в полях ввода
        self.nameEdit.returnPressed.connect(self.add_contact)
        self.phoneEdit.returnPressed.connect(self.add_contact)

        # Инициализация списка контактов
        self.contacts = []

        # Настройка шрифта для списка контактов
        font = QFont('Segoe UI', 10)
        self.contactsList.setFont(font)

        # Обновление статусной строки
        self.update_status()

    def add_contact(self):
        """Добавление нового контакта"""
        name = self.nameEdit.text().strip()
        phone = self.phoneEdit.text().strip()

        # Валидация ввода
        if not name:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите имя контакта!")
            self.nameEdit.setFocus()
            return

        if not phone:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Введите номер телефона!")
            self.phoneEdit.setFocus()
            return

        # Проверка на уникальность имени
        for contact in self.contacts:
            if contact['name'].lower() == name.lower():
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Контакт с таким именем уже существует!")
                self.nameEdit.selectAll()
                self.nameEdit.setFocus()
                return

        # Добавляем контакт в список
        contact_data = {
            'name': name,
            'phone': phone,
            'display_text': f"{name} - {phone}"
        }

        self.contacts.append(contact_data)

        # Сортируем контакты по имени
        self.contacts.sort(key=lambda x: x['name'].lower())

        # Обновляем список
        self.update_contacts_list()

        # Очищаем поля ввода
        self.clear_fields()

        # Обновляем статус
        self.update_status()

        QtWidgets.QMessageBox.information(self, "Успех", "Контакт добавлен!")

    def clear_fields(self):
        """Очистка полей ввода"""
        self.nameEdit.clear()
        self.phoneEdit.clear()
        self.nameEdit.setFocus()

    def delete_contact(self):
        """Удаление выбранного контакта"""
        current_row = self.contactsList.currentRow()

        if current_row == -1:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите контакт для удаления!")
            return

        # Получаем имя контакта для подтверждения
        contact_name = self.contacts[current_row]['name']

        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить контакт '{contact_name}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            # Удаляем контакт из списка
            del self.contacts[current_row]

            # Обновляем список
            self.update_contacts_list()

            # Обновляем статус
            self.update_status()

            QtWidgets.QMessageBox.information(self, "Успех", "Контакт удален!")

    def clear_all_contacts(self):
        """Очистка всех контактов"""
        if not self.contacts:
            QtWidgets.QMessageBox.information(self, "Информация", "Список контактов уже пуст!")
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение",
            "Вы уверены, что хотите удалить все контакты?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            self.contacts.clear()
            self.update_contacts_list()
            self.update_status()
            QtWidgets.QMessageBox.information(self, "Успех", "Все контакты удалены!")

    def update_contacts_list(self):
        """Обновление списка контактов"""
        self.contactsList.clear()

        for contact in self.contacts:
            item = QtWidgets.QListWidgetItem(contact['display_text'])
            self.contactsList.addItem(item)

    def update_status(self):
        """Обновление статусной строки"""
        count = len(self.contacts)
        if count == 0:
            self.statusbar.showMessage("Список контактов пуст")
        elif count == 1:
            self.statusbar.showMessage("1 контакт в списке")
        elif 2 <= count <= 4:
            self.statusbar.showMessage(f"{count} контакта в списке")
        else:
            self.statusbar.showMessage(f"{count} контактов в списке")


def main():
    app = QtWidgets.QApplication(sys.argv)
    address_book = AddressBook()
    address_book.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()