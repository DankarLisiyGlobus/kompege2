from end import Ui_Form
from PyQt6 import QtCore, QtWidgets, QtGui


class KEGE_END(QtWidgets.QWidget, Ui_Form):
    exited = QtCore.pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.stop)
        self._center()

    def _center(self):
        screen = self.screen() or QtGui.QGuiApplication.primaryScreen()
        geo = self.frameGeometry()
        geo.moveCenter(screen.availableGeometry().center())
        self.move(geo.topLeft())

    def stop(self):
        self.exited.emit()
        self.close()
