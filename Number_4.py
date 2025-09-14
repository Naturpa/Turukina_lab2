import sys
import random
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class PseudonymGame(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('pseudonym_game.ui', self)

        # Настройка фиксированного размера окна
        self.setFixedSize(500, 600)

        # Подключение обработчиков
        self.newGameButton.clicked.connect(self.start_new_game)
        self.take1Button.clicked.connect(lambda: self.player_turn(1))
        self.take2Button.clicked.connect(lambda: self.player_turn(2))
        self.take3Button.clicked.connect(lambda: self.player_turn(3))

        # Инициализация переменных игры
        self.total_stones = 0
        self.current_stones = 0
        self.game_active = False

        # Настройка шрифта для лога
        font = QFont('Courier New', 9)
        self.logText.setFont(font)

        # Блокировка кнопок хода до начала игры
        self.set_move_buttons_enabled(False)

    def start_new_game(self):
        """Начало новой игры"""
        self.total_stones = self.stonesSpinBox.value()
        self.current_stones = self.total_stones
        self.game_active = True

        # Очистка лога
        self.logText.clear()

        # Обновление интерфейса
        self.update_stones_display()
        self.turnLabel.setText("Ваш ход! Выберите камни")
        self.turnLabel.setStyleSheet("font-size: 14px; color: #27ae60; font-weight: bold;")
        self.add_to_log(f"Начало новой игры! Камней: {self.total_stones}")
        self.add_to_log("Игрок ходит первым")

        # Активация кнопок хода
        self.set_move_buttons_enabled(True)

        # Проверка выигрышной позиции
        if self.is_winning_position(self.current_stones):
            self.add_to_log("⚠️  ИИ имеет выигрышную стратегию!")
        else:
            self.add_to_log("🎯 У вас есть шанс выиграть!")

    def player_turn(self, stones_to_take):
        """Ход игрока"""
        if not self.game_active:
            return

        # Проверка валидности хода
        if stones_to_take < 1 or stones_to_take > 3:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Можно взять только 1, 2 или 3 камня!")
            return

        if stones_to_take > self.current_stones:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Нельзя взять больше камней, чем есть на столе!")
            return

        # Ход игрока
        self.current_stones -= stones_to_take
        self.add_to_log(f"👤 Игрок взял {stones_to_take} камней. Осталось: {self.current_stones}")

        # Проверка победы игрока
        if self.current_stones == 0:
            self.game_over("Игрок")
            return

        # Ход компьютера
        self.turnLabel.setText("Ход компьютера...")
        self.turnLabel.setStyleSheet("font-size: 14px; color: #e67e22; font-weight: bold;")
        self.set_move_buttons_enabled(False)

        # Задержка для имитации "думания" компьютера
        QtWidgets.QApplication.processEvents()
        QtWidgets.QApplication.processEvents()

        # Выполняем ход компьютера
        self.computer_turn()

    def computer_turn(self):
        """Ход компьютера с выигрышной стратегией"""
        if self.current_stones == 0:
            return

        # Вычисляем оптимальный ход
        stones_to_take = self.calculate_computer_move()

        # Ход компьютера
        self.current_stones -= stones_to_take
        self.add_to_log(f"🤖 Компьютер взял {stones_to_take} камней. Осталось: {self.current_stones}")

        # Проверка победы компьютера
        if self.current_stones == 0:
            self.game_over("Компьютер")
            return

        # Возвращаем ход игроку
        self.turnLabel.setText("Ваш ход! Выберите камни")
        self.turnLabel.setStyleSheet("font-size: 14px; color: #27ae60; font-weight: bold;")
        self.set_move_buttons_enabled(True)
        self.update_stones_display()

    def calculate_computer_move(self):
        """Вычисление оптимального хода для компьютера"""
        # Выигрышная стратегия: оставлять противнику количество камней, кратное 4
        remainder = self.current_stones % 4

        if remainder == 0:
            # Если текущее количество кратно 4, берем случайное количество (1-3)
            return random.randint(1, min(3, self.current_stones))
        else:
            # Берем столько, чтобы оставить кратное 4
            return remainder

    def is_winning_position(self, stones):
        """Проверка, является ли позиция выигрышной для ходящего"""
        return stones % 4 != 0

    def game_over(self, winner):
        """Завершение игры"""
        self.game_active = False
        self.set_move_buttons_enabled(False)

        if winner == "Игрок":
            self.turnLabel.setText("🎉 Вы победили!")
            self.turnLabel.setStyleSheet("font-size: 16px; color: #27ae60; font-weight: bold;")
            self.add_to_log("🎉 ПОБЕДА ИГРОКА!")
        else:
            self.turnLabel.setText("💻 Победил компьютер!")
            self.turnLabel.setStyleSheet("font-size: 16px; color: #e74c3c; font-weight: bold;")
            self.add_to_log("💻 ПОБЕДА КОМПЬЮТЕРА!")

        self.add_to_log("Игра завершена. Нажмите 'Новая игра' для продолжения")

    def update_stones_display(self):
        """Обновление отображения количества камней"""
        self.stonesLabel.setText(f"Камней на столе: {self.current_stones}")

        # Визуальная индикация количества камней
        if self.current_stones <= 3:
            color = "#e74c3c"  # красный - мало камней
        elif self.current_stones <= 10:
            color = "#f39c12"  # оранжевый - среднее количество
        else:
            color = "#27ae60"  # зеленый - много камней

        self.stonesLabel.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")

    def set_move_buttons_enabled(self, enabled):
        """Включение/отключение кнопок хода"""
        self.take1Button.setEnabled(enabled)
        self.take2Button.setEnabled(enabled)
        self.take3Button.setEnabled(enabled)

        # Визуальная индикация доступности кнопок
        style_enabled = "font-weight: bold; background-color: #3498db; color: white;"
        style_disabled = "background-color: #bdc3c7; color: #7f8c8d;"

        for button in [self.take1Button, self.take2Button, self.take3Button]:
            button.setStyleSheet(style_enabled if enabled else style_disabled)

    def add_to_log(self, message):
        """Добавление сообщения в лог"""
        self.logText.append(message)
        # Автопрокрутка к последнему сообщению
        self.logText.verticalScrollBar().setValue(
            self.logText.verticalScrollBar().maximum()
        )


def main():
    app = QtWidgets.QApplication(sys.argv)
    game = PseudonymGame()
    game.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()