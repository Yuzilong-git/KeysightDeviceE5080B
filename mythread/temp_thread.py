# -*- encoding: utf-8 -*-
"""
@File    : temp_thread.py
@Time    : 2021/10/15 11:12
@Author  : Coco
"""
import time

from PyQt5.QtCore import QThread, pyqtSignal


class WaitTargetTemp(QThread):
    signal = pyqtSignal()
    temp_signal = pyqtSignal(str)

    def __init__(self, temp_device):
        super(WaitTargetTemp, self).__init__()
        self.temp_device = temp_device
        self.target_temp = 0
        self.read_temp_flag = True
        self.capture_temp_flag = False
        self.set_temp_flag = False

    def run(self):
        # 等待温度到具体数值再执行之后代码，否则等待温度到达目标温度
        while self.read_temp_flag:
            current_temp = self.temp_device.read_current_temp()
            if self.set_temp_flag:
                self.temp_device.set_target_temp(self.target_temp)
                self.set_temp_flag = False
                if not self.temp_device.read_mode():
                    self.temp_device.set_run_mode()
            if self.capture_temp_flag:
                if current_temp == self.target_temp:
                    self.signal.emit()
            self.temp_signal.emit(str(current_temp))
            time.sleep(1)
