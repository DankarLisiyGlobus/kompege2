from kege_login import Ui_Form
from PyQt6 import QtCore, QtWidgets, QtGui
import sqlite3
import os
import bcrypt

# Кросс-платформенный код


class KEGE_LOGIN(QtWidgets.QWidget, Ui_Form):
    logged_in = QtCore.pyqtSignal()

    def __init__(self, variant_name: str):
        super().__init__()
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon("logo.svg"))
        self.variant_name = variant_name
        files = os.listdir("temp")
        self.DB_PATH = ""
        for file in files:
            if file.split(".")[-1] in ["db", "sqlite", "database"]:
                self.DB_PATH = "temp/" + file
        self.login_but.clicked.connect(self.login)
        self.fio = "Иванов Иван Иванович"

        self.shortcut_login = QtGui.QShortcut(QtGui.QKeySequence(
            "Enter"), self).activated.connect(self.login)
        self._center()

    def _center(self):
        screen = self.screen() or QtGui.QGuiApplication.primaryScreen()
        geo = self.frameGeometry()
        geo.moveCenter(screen.availableGeometry().center())
        self.move(geo.topLeft())

    def login(self):
        fio_text = self.fio_lineEdit.text()
        if fio_text == "":
            QtWidgets.QMessageBox.critical(None, "Ошибка входа", "Введите ФИО")
            return
        self.fio = fio_text
        passw_text = self.codeLine.text()
        con = sqlite3.connect(self.DB_PATH)
        cursor = con.cursor()
        cursor.execute("SELECT secrkey_hash from Variants")
        passw_hash_db = cursor.fetchone()[0]
        con.close()
        # Взял из базы данных хеш($2b$12$D4mt85LDOSi2/Rriy/Aa0OIhX22a8KBJF/sXcWJ/QCCwxUbgsT0vm),спросил у ии, что это за такой хеш, нашел в интернете как им пользоваться.
        if bcrypt.checkpw(passw_text.encode("utf-8"), passw_hash_db.encode("utf-8")):
            QtWidgets.QMessageBox.information(
                None, "Успешный вход", "Удачи на экзамене! Псоле закрытия данного сообщения, начнется отсчет времени на выполнение экзамена.")
            self.logged_in.emit()
            self.close()

        else:
            QtWidgets.QMessageBox.critical(
                None, "Ошибка входа", "Неверный код доступа")
