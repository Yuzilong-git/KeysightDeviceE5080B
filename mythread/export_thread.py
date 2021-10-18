# -*- encoding: utf-8 -*-
"""
@File    : export_thread.py
@Time    : 2021/10/11 16:13
@Author  : Coco
"""

from threading import Thread
from PyQt5.QtCore import QThread, pyqtSignal
from utils.file_operate import write_data


class MyThread(Thread):
    def __init__(self, func, args):
        super(MyThread, self).__init__()
        self.result = None
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)
        # print(self.result)

    def get_result(self):
        try:
            return self.result
        except Exception as e:
            print(e)


class ExportThread(QThread):
    signal = pyqtSignal()

    def __init__(self, win_data_dict, file, header):
        super(ExportThread, self).__init__()
        self.win_data_dict = win_data_dict
        self.file = file
        self.header = header

    def run(self):
        max_row_len = max(i for i in [len(self.win_data_dict[i]) for i in self.win_data_dict])
        write_data(self.file, [i for i in range(1, max_row_len + 1)], 1, [item for item in self.header])
        write_data(self.file, self.win_data_dict[0], 2)
        for i in range(len(self.win_data_dict) - 1):
            write_data(self.file, self.win_data_dict[i + 1], i + 3)
        self.signal.emit()
