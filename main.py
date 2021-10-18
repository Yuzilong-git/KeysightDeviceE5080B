# -*- encoding: utf-8 -*-
"""
@File    : main.py
@Time    : 2021/10/9 18:16
@Author  : Coco
"""
import sys

from PyQt5.QtGui import QIcon, QFont

from driver.main_driver import MainAction

from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainAction()
    window.setWindowIcon(QIcon("icon/demo1.png"))
    f = QFont("Arial", 10)
    app.setFont(f)
    window.show()
    sys.exit(app.exec_())
