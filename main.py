from kege import Ui_MainWindow
from PyQt6 import QtCore, QtGui, QtWidgets
import sys
import sqlite3
import os
import zipfile
import io

DOWNLOAD_FOLDER = "home/dankar/Загрузки"

class KEGE(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, variant_name:str, fio:str):
        super().__init__()
        self.setupUi(self)
        self.variant_name = variant_name
        self.fio = fio
        self.fio_label.setText(self.fio)
        with zipfile.ZipFile(f"variants/{self.variant_name}.tsk", "r") as z:
            z.extractall("temp")
        self.DB_PATH = "temp/" + variant_name + ".db"
        self.generate_answers()
        self.tableWidget.hide()
        self.cur_ans_name = "Info"
        self.set_content_answer("Info")

    def generate_answers(self):
        con = sqlite3.connect(self.DB_PATH)
        cursor = con.cursor()
        cursor.execute("SELECT count_of_quest from Variants")
        self.count_of_quest = cursor.fetchone()[0]
        cursor.execute("SELECT max_time_min from Variants")
        self.max_time_min = cursor.fetchone()[0]
        cursor.execute("SELECT ID, number, question, files, rows_in_answ, col_in_answ from Questions")
        self.answers = cursor.fetchall()
        con.close()


        for ans_i in range(self.count_of_quest + 1):
            but = QtWidgets.QPushButton(self.answers[ans_i][1])
            but.setStyleSheet("color:black")
            but.clicked.connect(self.set_content_answer_with_sender)
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
        cursor.execute("SELECT ID from Questions WHERE number = ?", (ans_name,))
        ans_i = cursor.fetchone()[0] - 1
        con.close()
        table_sx, table_sy = self.answers[ans_i][4], self.answers[ans_i][5]
        if table_sx == 1 and table_sy == 1:
            self.tableWidget.hide()
            self.result_lineEdit.setDisabled(False)
            final_width = self.size().width() - self.answers_area.size().width() - 50
        elif table_sx == None and table_sy == None:
            self.tableWidget.hide()
            self.result_lineEdit.setDisabled(False)
            final_width = self.size().width() - self.answers_area.size().width() - 50
        else:
            self.tableWidget.show()
            self.result_lineEdit.setDisabled(True)
            final_width = self.size().width() - self.answers_area.size().width() - self.tableWidget.size().width() - 50
            table_widget_size = self.size().width() , self. dvd
            self.set_table_size(table_sx, table_sy)

        file_name = "temp/ans_images/" + ans_name + ".png"
        pixmap = QtGui.QPixmap(file_name)
        width, height = pixmap.size().width(), pixmap.size().height()
        
        ratio = final_width / width
        pixmap = pixmap.scaled(final_width, int(height * ratio))
        self.label.setPixmap(pixmap)
        self.set_files_to_download(ans_i)
        self.cur_ans_name = ans_name
    
    def set_table_size(self, sx:int, sy:int):
        self.tableWidget.clear()  # Очищаем от того, что было, даже если ничего не было
        self.tableWidget.setRowCount(sy)  # Задаём количество строчек
        self.tableWidget.setColumnCount(sx) # и столбцов (считаем, что в разных строчках одинаковое количество столбцов)
        self.tableWidget.setHorizontalHeaderLabels(map(lambda x: str(x), range(sx)))  # В первой строке файла — вертикальные заголовки
        self.tableWidget.setVerticalHeaderLabels(map(lambda x: str(x), range(sy)))  # В первой строке файла — вертикальные заголовки

        # Умная ширина колонок
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(True)

    def set_files_to_download(self, ans_i):
        while self.files_lay.count():
            item = self.files_lay.takeAt(0)
            item.widget().deleteLater()
        if self.answers[ans_i][3] == None or self.answers[ans_i][3] == "" or self.answers[ans_i][3] == " ":
            return
        list_of_files = self.answers[ans_i][3].split(";")
        for file in list_of_files:
            but = QtWidgets.QPushButton("📥" + file)
            but.setStyleSheet("QPushButton {color: #fff975;font-size: 14px;border-radius: 5px;background-color: #7590ff;padding: 4px 4px;}QPushButton:hover {background-color: #a8b9ff;}QPushButton:pressed {background-color: #dbe2ff;}")
            but.clicked.connect(lambda _, _file = file: self.download_file(_file))
            self.files_lay.addWidget(but)

    def download_file(self, filename:str):
        print(f"Перемещение в папку загрузок файла {filename}")


    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_content_answer(self.cur_ans_name)


try:
    if __name__ == '__main__':
        app = QtWidgets.QApplication(sys.argv)
        ex = KEGE(variant_name = "04_04_2025_2noint", fio = "Иванов Иван Иванович")
        ex.show()
        app.exec()
finally:
    os.system('rm -rf -- "temp"')
    #sys.exit()