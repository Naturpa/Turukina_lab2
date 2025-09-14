import sys
import re
from difflib import SequenceMatcher
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor


class PlagiarismChecker(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Загрузка интерфейса из файла
        uic.loadUi('plagiarism_checker.ui', self)

        # Настройка фиксированного размера окна
        self.setFixedSize(900, 700)

        # Подключение обработчиков
        self.checkButton.clicked.connect(self.check_plagiarism)
        self.clearButton.clicked.connect(self.clear_all)

        # Подключение обработчиков изменения текста для статистики
        self.originalTextEdit.textChanged.connect(self.update_text1_stats)
        self.checkedTextEdit.textChanged.connect(self.update_text2_stats)

        # Настройка шрифтов
        font = QFont('Courier New', 10)
        self.detailsTextEdit.setFont(font)

        # Инициализация статистики
        self.update_text1_stats()
        self.update_text2_stats()

        # Обновление статусной строки
        self.statusbar.showMessage("Готов к проверке. Введите тексты и нажмите 'Проверить на плагиат'")

    def preprocess_text(self, text):
        """Предобработка текста: приведение к нижнему регистру и удаление лишних символов"""
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)  # Удаляем пунктуацию
        text = re.sub(r'\s+', ' ', text)  # Заменяем множественные пробелы на один
        return text.strip()

    def calculate_similarity(self, text1, text2):
        """Расчет схожести текстов с использованием нескольких методов"""
        if not text1 or not text2:
            return 0.0

        # Метод 1: Сравнение по словам (Jaccard similarity)
        words1 = set(self.preprocess_text(text1).split())
        words2 = set(self.preprocess_text(text2).split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)
        jaccard_similarity = len(intersection) / len(union) * 100

        # Метод 2: Последовательное сравнение (SequenceMatcher)
        seq_similarity = SequenceMatcher(None, text1, text2).ratio() * 100

        # Метод 3: Сравнение по n-граммам (биграммы)
        def get_ngrams(text, n=2):
            words = text.split()
            return [' '.join(words[i:i + n]) for i in range(len(words) - n + 1)]

        ngrams1 = set(get_ngrams(self.preprocess_text(text1), 2))
        ngrams2 = set(get_ngrams(self.preprocess_text(text2), 2))

        if ngrams1 and ngrams2:
            ngram_similarity = len(ngrams1.intersection(ngrams2)) / len(ngrams1.union(ngrams2)) * 100
        else:
            ngram_similarity = 0.0

        # Взвешенное среднее всех методов
        similarity = (jaccard_similarity * 0.4 + seq_similarity * 0.3 + ngram_similarity * 0.3)

        return round(similarity, 2)

    def find_similar_lines(self, text1, text2):
        """Поиск похожих строк в текстах"""
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')

        similar_lines = []

        for i, line1 in enumerate(lines1, 1):
            if not line1.strip():
                continue

            for j, line2 in enumerate(lines2, 1):
                if not line2.strip():
                    continue

                line_similarity = self.calculate_similarity(line1, line2)
                if line_similarity > 50:  # Порог для похожих строк
                    similar_lines.append({
                        'line1_num': i,
                        'line1_text': line1,
                        'line2_num': j,
                        'line2_text': line2,
                        'similarity': line_similarity
                    })

        return similar_lines

    def check_plagiarism(self):
        """Основная функция проверки на плагиат"""
        text1 = self.originalTextEdit.toPlainText().strip()
        text2 = self.checkedTextEdit.toPlainText().strip()

        if not text1 or not text2:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Оба текстовых поля должны быть заполнены!")
            return

        # Расчет общей схожести
        similarity = self.calculate_similarity(text1, text2)

        # Поиск похожих строк
        similar_lines = self.find_similar_lines(text1, text2)

        # Обновление интерфейса
        self.update_results(similarity, similar_lines, text1, text2)

        # Проверка порога срабатывания
        threshold = self.thresholdSpinBox.value()
        self.check_threshold(similarity, threshold)

    def update_results(self, similarity, similar_lines, text1, text2):
        """Обновление результатов проверки"""
        # Общая схожесть
        self.similarityLabel.setText(f"Схожесть: {similarity}%")

        # Цвет в зависимости от уровня схожести
        if similarity < 30:
            color = "#27ae60"  # зеленый - низкая схожесть
        elif similarity < 70:
            color = "#f39c12"  # оранжевый - средняя схожесть
        else:
            color = "#e74c3c"  # красный - высокая схожесть

        self.similarityLabel.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {color};")

        # Детальная информация
        details = f"ОБЩАЯ СХОЖЕСТЬ: {similarity}%\n"
        details += f"Исходный текст: {len(text1.split())} слов, {len(text1)} символов\n"
        details += f"Проверяемый текст: {len(text2.split())} слов, {len(text2)} символов\n\n"

        if similar_lines:
            details += "НАЙДЕНЫ ПОХОЖИЕ ФРАГМЕНТЫ:\n"
            details += "=" * 50 + "\n"

            for i, line_info in enumerate(similar_lines, 1):
                details += f"\nФрагмент #{i} (схожесть: {line_info['similarity']}%):\n"
                details += f"Исходный текст (строка {line_info['line1_num']}): {line_info['line1_text'][:100]}...\n"
                details += f"Проверяемый текст (строка {line_info['line2_num']}): {line_info['line2_text'][:100]}...\n"
                details += "-" * 30 + "\n"
        else:
            details += "Похожих фрагментов не найдено.\n"

        self.detailsTextEdit.setPlainText(details)

    def check_threshold(self, similarity, threshold):
        """Проверка порога срабатывания и обновление статусной строки"""
        if similarity >= threshold:
            self.statusbar.showMessage(f"⚠️  ВНИМАНИЕ: Обнаружен возможный плагиат! Схожесть: {similarity}%")
            self.statusbar.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        else:
            self.statusbar.showMessage(f"✓ Текст прошел проверку. Схожесть: {similarity}%")
            self.statusbar.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold;")

    def update_text1_stats(self):
        """Обновление статистики первого текста"""
        text = self.originalTextEdit.toPlainText()
        char_count = len(text)
        word_count = len(text.split())
        self.text1StatsLabel.setText(f"Символов: {char_count}, Слов: {word_count}")

    def update_text2_stats(self):
        """Обновление статистики второго текста"""
        text = self.checkedTextEdit.toPlainText()
        char_count = len(text)
        word_count = len(text.split())
        self.text2StatsLabel.setText(f"Символов: {char_count}, Слов: {word_count}")

    def clear_all(self):
        """Очистка всех полей"""
        self.originalTextEdit.clear()
        self.checkedTextEdit.clear()
        self.detailsTextEdit.clear()
        self.similarityLabel.setText("Схожесть: 0.00%")
        self.similarityLabel.setStyleSheet("font-size: 16px; font-weight: bold; color: #27ae60;")
        self.statusbar.showMessage("Поля очищены. Готов к новой проверке.")
        self.statusbar.setStyleSheet("")  # Сброс стиля статусной строки


def main():
    app = QtWidgets.QApplication(sys.argv)
    checker = PlagiarismChecker()
    checker.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()