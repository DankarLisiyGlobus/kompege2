from platform_kege import copy, delete_temp
from kege import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets
import sys
import sqlite3
import os
import zipfile
from login_form import KEGE_LOGIN
from stop_exam_with_code import KEGE_LOGOUT
from end_form import KEGE_END
from datetime import datetime

button_geted_otvet = """QPushButton {
    color: rgb(255, 255, 255);
    background-color: rgba(5, 175, 105, 130);
}
QPushButton:hover {
    background-color: rgba(1, 145, 68, 130);
}
QPushButton:pressed {
    background-color: rgba(6, 209, 55, 130);
}"""

button_not_geted_otvet = """QPushButton {
    color: black;
    background-color: rgb(200, 200, 200);
}
QPushButton:hover {
    background-color: rgb(233, 233, 233);
}
QPushButton:pressed {
    background-color: rgb(255, 255, 255);
}"""

DOWNLOAD_FOLDER = os.getcwd()


# Кросс-платформенный код


class KEGE(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, variant_name: str):
        super().__init__()
        self.setupUi(self)
        self.variant_name_ = variant_name
        self.move(500, 300)

        self.login_form = KEGE_LOGIN(self.variant_name_)
        self.login_form.show()
        self.login_form.logged_in.connect(self.load)

        self.result_button.clicked.connect(self.set_otvet)

        self.otvets = {}
        self.cur_ans_name = "Info"
        self.cur_ans_type = "line"
        self.buts: list[QtWidgets.QPushButton] = []
        self.stop_ege.clicked.connect(self.stop_exam_but)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_time_label)
        self.shortcut_exit = QtGui.QShortcut(QtGui.QKeySequence(
            "Esc"), self).activated.connect(self.stop_exam)

    def load(self):
        self.fio = self.login_form.fio
        self.fio_label.setText(self.fio)
        files = os.listdir("temp")
        self.DB_PATH = ""
        for file in files:
            if file.split(".")[-1] in ["db", "sqlite", "database"]:
                self.DB_PATH = "temp/" + file

        con = sqlite3.connect(self.DB_PATH)
        cur = con.cursor()
        cur.execute("SELECT description FROM Variants")
        self.variant_name = cur.fetchone()[0]
        self.kim_label.setText(f"КИМ {self.variant_name}")
        self.br_label.hide()
        con.close()

        self.generate_answers()
        self.ost_time = self.max_time_min * 60
        self.tableWidget.hide()
        self.set_content_answer("Info")
        self.show()
        self.timer.start()
        self._center()

    def _center(self):
        screen = self.screen() or QtGui.QGuiApplication.primaryScreen()
        geo = self.frameGeometry()
        geo.moveCenter(screen.availableGeometry().center())
        self.move(geo.topLeft())

    def update_time_label(self):
        self.ost_time -= 1
        self.time_label.setText(
            f"{self.ost_time // 3600}:{(self.ost_time // 60) % 60}:{self.ost_time % 60}")
        if self.ost_time <= 0:
            self.stop_exam()

    def generate_answers(self):
        con = sqlite3.connect(self.DB_PATH)
        cursor = con.cursor()
        cursor.execute("SELECT count_of_quest from Variants")
        self.count_of_quest = cursor.fetchone()[0]
        cursor.execute("SELECT max_time_min from Variants")
        self.max_time_min = cursor.fetchone()[0]
        cursor.execute(
            "SELECT ID, number, question, files, rows_in_answ, col_in_answ from Questions")
        self.answers = cursor.fetchall()
        con.close()

        for ans_i in range(self.count_of_quest + 1):
            but = QtWidgets.QPushButton(self.answers[ans_i][1])
            but.setStyleSheet(button_not_geted_otvet)
            but.clicked.connect(self.set_content_answer_with_sender)
            self.buts.append(but)
            self.verticalLayout_2.addWidget(but)
        os.makedirs("temp", exist_ok=True)
        os.makedirs("temp/ans_images", exist_ok=True)
        for ans in self.answers:
            with open(f"temp/ans_images/{ans[1]}.png", "wb") as file:
                file.write(ans[2])
                file.close()

    def set_content_answer_with_sender(self):
        ans_name = self.sender().text()
        self.set_content_answer(ans_name)

    def set_content_answer(self, ans_name):
        con = sqlite3.connect(self.DB_PATH)
        cursor = con.cursor()
        cursor.execute(
            "SELECT ID from Questions WHERE number = ?", (ans_name,))
        ans_i = cursor.fetchone()[0] - 1
        con.close()
        table_sy, table_sx = self.answers[ans_i][4], self.answers[ans_i][5]
        if table_sx == 1 and table_sy == 1:
            self.tableWidget.hide()
            self.result_lineEdit.setDisabled(False)
            final_width = self.size().width() - self.answers_area.size().width() - 50
            self.cur_ans_type = "line"
        elif table_sx == None and table_sy == None:
            self.tableWidget.hide()
            self.result_lineEdit.setDisabled(False)
            final_width = self.size().width() - self.answers_area.size().width() - 50
            self.cur_ans_type = "line"
        else:
            self.tableWidget.show()
            self.result_lineEdit.setDisabled(True)
            final_width = self.size().width() - self.answers_area.size().width() - \
                self.tableWidget.size().width() - 50
            self.set_table(table_sx, table_sy, ans_i)
            self.cur_ans_type = "table"

        file_name = "temp/ans_images/" + ans_name + ".png"
        pixmap = QtGui.QPixmap(file_name)
        width, height = pixmap.size().width(), pixmap.size().height()
        self.result_lineEdit.setText("")
        if ans_i in self.otvets.keys():
            if self.cur_ans_type == "line":
                self.result_lineEdit.setText(self.otvets[ans_i])

        if ans_name.lower() == "info":
            self.result_lineEdit.setDisabled(True)
            self.result_button.setDisabled(True)
        else:
            self.result_button.setDisabled(False)

        ratio = final_width / width
        pixmap = pixmap.scaled(final_width, int(height * ratio))
        self.label.setPixmap(pixmap)
        self.set_files_to_download(ans_i)
        self.cur_ans_name = ans_name

    def set_table(self, sx: int, sy: int, ans_i):
        self.tableWidget.clear()  # Очищаем от того, что было, даже если ничего не было
        self.tableWidget.setRowCount(sy)  # Задаём количество строчек
        # и столбцов (считаем, что в разных строчках одинаковое количество столбцов)
        self.tableWidget.setColumnCount(sx)
        # В первой строке файла — вертикальные заголовки
        self.tableWidget.setHorizontalHeaderLabels(
            map(lambda x: str(x), range(sx)))
        # В первой строке файла — вертикальные заголовки
        self.tableWidget.setVerticalHeaderLabels(
            map(lambda x: str(x), range(sy)))

        # Умная ширина колонок
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(
            QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

        if not ans_i in self.otvets.keys():
            return

        for r, row in enumerate(self.otvets[ans_i]):
            for c, val in enumerate(row):
                item = QtWidgets.QTableWidgetItem(val)
                if val.isdigit():
                    item.setTextAlignment(
                        QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                # Ставим ячейку в нужное место
                self.tableWidget.setItem(r, c, item)

    def set_files_to_download(self, ans_i):
        while self.files_lay.count():
            item = self.files_lay.takeAt(0)
            item.widget().deleteLater()
        if self.answers[ans_i][3] == None or self.answers[ans_i][3] == "" or self.answers[ans_i][3] == " ":
            return
        list_of_files = self.answers[ans_i][3].split(";")
        for file in list_of_files:
            but = QtWidgets.QPushButton("📥" + file)
            but.setStyleSheet(
                "QPushButton {color: #fff975;font-size: 14px;border-radius: 5px;background-color: #7590ff;padding: 4px 4px;}QPushButton:hover {background-color: #a8b9ff;}QPushButton:pressed {background-color: #dbe2ff;}")
            but.clicked.connect(
                lambda _, _file=file: self.download_file(_file))
            self.files_lay.addWidget(but)

    def download_file(self, filename: str):
        print(f"Перемещение в папку загрузок файла {filename}")
        path = f"temp/{filename}"
        if os.path.exists(filename):
            answer = QtWidgets.QMessageBox.question(
                self,
                'Подтверждение',
                'Вы уверены, что хотите перезаписать файл?\nЭто действие необратимо!',
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No  # Кнопка по умолчанию
            )

            if answer == QtWidgets.QMessageBox.StandardButton.Yes:
                copy(path, DOWNLOAD_FOLDER)
            else:
                return

        copy(path, DOWNLOAD_FOLDER)
        QtWidgets.QMessageBox.information(
            self, "Загрузка завершена", f"Загрузка файла {filename} завершена, проверьте загрузок")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_content_answer(self.cur_ans_name)

    def set_otvet(self):
        con = sqlite3.connect(self.DB_PATH)
        cursor = con.cursor()
        cursor.execute(
            "SELECT ID from Questions WHERE number = ?", (self.cur_ans_name,))
        ans_i = cursor.fetchone()[0] - 1
        con.close()
        if self.cur_ans_type == "line":
            otvet_text = self.result_lineEdit.text()
            if otvet_text in ["", " "] or otvet_text.isspace():
                return
        else:
            data_flag = False
            rows = []
            for r in range(self.tableWidget.rowCount()):
                row = []
                for c in range(self.tableWidget.columnCount()):
                    it = self.tableWidget.item(r, c)
                    row.append("" if it is None else it.text())
                    if it is None:
                        continue
                    if not it.text() in ["", " "] or it.text().isspace():
                        data_flag = True
                rows.append(row)
            if not data_flag:
                return
            otvet_text = rows

        self.buts[ans_i].setStyleSheet(button_geted_otvet)

        self.otvets[ans_i] = otvet_text

    def stop_exam_but(self):
        self.logout_form = KEGE_LOGOUT(self.variant_name_)
        self.logout_form.show()
        self.logout_form.logged_in.connect(self.stop_exam)

    def stop_exam(self):
        if hasattr(self, "logout_form"):
            self.logout_form.close()

        self.hide()
        self.generate_result_txt()
        self.timer.stop()
        self.end_form = KEGE_END()
        self.end_form.show()
        self.end_form.exited.connect(self.close)

    def generate_result_txt(self):
        now = datetime.now()
        formatted_date = now.strftime("%d_%m_%Y")
        filename = f"{self.variant_name}fio{self.fio}.txt"
        text = f"{self.variant_name}\n{formatted_date}\n"
        otvets_data = {}
        for i in range(self.count_of_quest):
            ans_i = i + 1
            if ans_i in self.otvets.keys():
                otvets_data[ans_i] = self.otvets[ans_i]
            else:
                otvets_data[ans_i] = "_"

        for ans_id in otvets_data.keys():
            ans_data = otvets_data[ans_id]
            if type(ans_data) == str:
                text += f"{ans_id + 1}. {ans_data}\n"
            else:
                table_data = []
                for row in ans_data:
                    for el in row:
                        table_data.append(str(el))
                text += f"{ans_id}. {";".join(table_data)}\n"
        with open(filename, "w") as f:
            f.write(text)
            f.close()


def main(VARIANT_NAME):
    if not os.path.exists("temp"):
        with zipfile.ZipFile(f"{VARIANT_NAME}.tsk", "r") as z:
            z.extractall("temp")
    ex = KEGE(variant_name=VARIANT_NAME)
    return ex


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    files = os.listdir(os.getcwd())
    var_file_names = []
    for file in files:
        if file.split(".")[-1] in ["tsk"]:
            var_file_names.append(file.split(".")[0])
    if len(var_file_names) == 0:
        QtWidgets.QMessageBox.critical(
                        None, "Ошибка", "Не найден файл .tsk с заданиями")
        sys.exit()
    elif len(var_file_names) == 1:
        VNAME = var_file_names[0]
    else:
        VNAME = var_file_names[0]
    
    window = main(VNAME)
    code = app.exec()
    delete_temp()
    sys.exit(code)
