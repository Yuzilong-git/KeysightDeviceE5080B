# -*- encoding: utf-8 -*-
"""
@File    : visa_thread.py
@Time    : 2021/10/9 18:16
@Author  : Coco
"""
from PyQt5.QtCore import QThread, pyqtSignal


class GetDataThread(QThread):
    signal = pyqtSignal(object)

    def __init__(self, device, s_select_list_setting, format_list_setting, sweep_data, window_info):
        super(GetDataThread, self).__init__()
        self.device = device
        self.s_select_list_setting = s_select_list_setting
        self.format_list_setting = format_list_setting
        self.sweep_data = sweep_data
        self.window_info = window_info

    def run(self):
        self.device.create_window(self.s_select_list_setting, self.format_list_setting, self.sweep_data)
        plot_data = self.device.get_plot_data([i + 1 for i in list(self.window_info.keys())])
        self.signal.emit(plot_data)
