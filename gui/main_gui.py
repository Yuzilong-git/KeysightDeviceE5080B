# -*- encoding: utf-8 -*-
"""
@File    : main_gui.py
@Time    : 2021/10/9 18:23
@Author  : Coco
"""
import ctypes
import sys

import matplotlib.pyplot as plt
from QCandyUi import CandyWindow
from PyQt5.QtGui import QDoubleValidator, QIcon, QPixmap
from PyQt5.QtCore import Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QPushButton, QLineEdit, QHBoxLayout, QVBoxLayout, \
    QGridLayout, QMainWindow, QComboBox, QHeaderView, QTableWidget, QAbstractItemView, QToolBar, QMenuBar, QStatusBar, \
    QGroupBox, QCheckBox

ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("   KEYSIGHT   E5080B")
        self.resize(1450, 948)
        with open('QSS/origin.qss', 'r', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        self.s_list = ['S11', 'S12', 'S21', 'S22']
        self.format_list = ['MLOGarithmic', 'MLINear', 'PHASe', 'SWR', 'REAL', 'IMAGinary', 'GDELay']
        self.color_list = ['black', 'blue', 'green', 'orange', 'red']
        self.unit_list = ['KHz', 'MHz', 'GHz']
        self._setupUI()

    def _setupUI(self):
        # 菜单栏
        self.menu = QMenuBar()
        self.setMenuBar(self.menu)
        self.menu.addMenu("文件")
        self.menu.addMenu("设备")
        self.temp = self.menu.addMenu("温度")
        self.menu.addMenu("关于")
        self.static_temp_mode = self.temp.addAction("常温模式")
        self.static_temp_mode.setCheckable(True)
        self.static_temp_mode.setChecked(True)
        self.set_temp_mode = self.temp.addAction("变温模式")
        self.set_temp_mode.setCheckable(True)

        # 工具栏
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)

        # 状态栏
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        # 中心窗口控件
        self.main_widget = QWidget()
        # 中心窗口中采用水平布局
        self.hl_content = QHBoxLayout(self.main_widget)

        # 左侧区域
        self.left_widget = QWidget()
        self.vl_left = QVBoxLayout(self.left_widget)

        # 画图区域
        self.plot_widget = QWidget()
        self.plot_1 = QWidget()
        self.hl_plot_1 = QHBoxLayout(self.plot_1)
        self.plot_2 = QWidget()
        self.hl_plot_2 = QHBoxLayout(self.plot_2)
        self.plot_3 = QWidget()
        self.hl_plot_3 = QHBoxLayout(self.plot_3)
        self.plot_4 = QWidget()
        self.hl_plot_4 = QHBoxLayout(self.plot_4)
        self.figure_1 = plt.figure()
        self.canvas_1 = FigureCanvas(self.figure_1)
        self.figure_2 = plt.figure()
        self.canvas_2 = FigureCanvas(self.figure_2)
        self.figure_3 = plt.figure()
        self.canvas_3 = FigureCanvas(self.figure_3)
        self.figure_4 = plt.figure()
        self.canvas_4 = FigureCanvas(self.figure_4)
        self.hl_plot_1.addWidget(self.canvas_1)
        self.hl_plot_2.addWidget(self.canvas_2)
        self.hl_plot_3.addWidget(self.canvas_3)
        self.hl_plot_4.addWidget(self.canvas_4)
        # 设置布局
        self.gl_plot = QGridLayout(self.plot_widget)
        self.gl_plot.addWidget(self.plot_1, 0, 0)
        self.gl_plot.addWidget(self.plot_2, 0, 1)
        self.gl_plot.addWidget(self.plot_3, 1, 0)
        self.gl_plot.addWidget(self.plot_4, 1, 1)
        self.gl_plot_list = [self.plot_1, self.plot_2, self.plot_3, self.plot_4]

        # 表格区域
        self.table_widget = QTableWidget()
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # 将画图和表格区域添加到左侧中
        self.vl_left.addWidget(self.plot_widget)
        self.vl_left.addWidget(self.table_widget)
        self.vl_left.setStretch(0, 9)
        self.vl_left.setStretch(1, 5)

        # 参数设置区域
        self.setting_widget = QWidget()
        self.vl_setting = QVBoxLayout(self.setting_widget)

        # 窗口设置部分
        self.gb_window_setting = QGroupBox("windows setting")
        self.gl_window_setting = QGridLayout(self.gb_window_setting)
        self.gl_window_setting.setHorizontalSpacing(15)
        self.gl_window_setting.setVerticalSpacing(20)
        self.chb_window_1 = QCheckBox("Window 1:")
        self.cb_s_select_1 = QComboBox()
        self.cb_s_select_1.addItems(self.s_list)
        self.cb_format_1 = QComboBox()
        self.cb_format_1.addItems(self.format_list)
        self.cb_color_1 = QComboBox()
        self.cb_color_1.addItems(self.color_list)

        self.chb_window_2 = QCheckBox("Window 2:")
        self.cb_s_select_2 = QComboBox()
        self.cb_s_select_2.addItems(self.s_list)
        self.cb_format_2 = QComboBox()
        self.cb_format_2.addItems(self.format_list)
        self.cb_color_2 = QComboBox()
        self.cb_color_2.addItems(self.color_list)

        self.chb_window_3 = QCheckBox("Window 3:")
        self.cb_s_select_3 = QComboBox()
        self.cb_s_select_3.addItems(self.s_list)
        self.cb_format_3 = QComboBox()
        self.cb_format_3.addItems(self.format_list)
        self.cb_color_3 = QComboBox()
        self.cb_color_3.addItems(self.color_list)

        self.chb_window_4 = QCheckBox("Window 4:")
        self.cb_s_select_4 = QComboBox()
        self.cb_s_select_4.addItems(self.s_list)
        self.cb_format_4 = QComboBox()
        self.cb_format_4.addItems(self.format_list)
        self.cb_color_4 = QComboBox()
        self.cb_color_4.addItems(self.color_list)

        self.pb_save = QPushButton("保存设置")
        self.pb_clear = QPushButton("清除图像")
        self.chb_list = [self.chb_window_1, self.chb_window_2, self.chb_window_3, self.chb_window_4]
        self.cb_s_list = [self.cb_s_select_1, self.cb_s_select_2, self.cb_s_select_3, self.cb_s_select_4]
        self.cb_format_list = [self.cb_format_1, self.cb_format_2, self.cb_format_3, self.cb_format_4]
        self.cb_color_list = [self.cb_color_1, self.cb_color_2, self.cb_color_3, self.cb_color_4]

        self.gl_window_setting.addWidget(self.chb_window_1, 0, 0)
        self.gl_window_setting.addWidget(self.cb_s_select_1, 0, 1)
        self.gl_window_setting.addWidget(self.cb_format_1, 0, 2)
        self.gl_window_setting.addWidget(self.cb_color_1, 0, 3)
        self.gl_window_setting.addWidget(self.chb_window_2, 1, 0)
        self.gl_window_setting.addWidget(self.cb_s_select_2, 1, 1)
        self.gl_window_setting.addWidget(self.cb_format_2, 1, 2)
        self.gl_window_setting.addWidget(self.cb_color_2, 1, 3)
        self.gl_window_setting.addWidget(self.chb_window_3, 2, 0)
        self.gl_window_setting.addWidget(self.cb_s_select_3, 2, 1)
        self.gl_window_setting.addWidget(self.cb_format_3, 2, 2)
        self.gl_window_setting.addWidget(self.cb_color_3, 2, 3)
        self.gl_window_setting.addWidget(self.chb_window_4, 3, 0)
        self.gl_window_setting.addWidget(self.cb_s_select_4, 3, 1)
        self.gl_window_setting.addWidget(self.cb_format_4, 3, 2)
        self.gl_window_setting.addWidget(self.cb_color_4, 3, 3)
        self.gl_window_setting.addWidget(self.pb_save, 4, 0, 1, 2)
        self.gl_window_setting.addWidget(self.pb_clear, 4, 2, 1, 2)

        # marker部分
        self.gb_marker = QGroupBox("Make Marker")
        self.gl_marker = QGridLayout(self.gb_marker)
        self.gl_marker.setHorizontalSpacing(15)
        self.gl_marker.setVerticalSpacing(20)
        self.lb_window = QLabel("Window:")
        self.cb_window = QComboBox()
        self.cb_window.addItems(['Window1', 'Window2', 'Window3', 'Window4'])
        self.lb_true_x_value = QLabel("True X Value:")
        self.le_true_x_value = QLineEdit()
        self.le_true_x_value.setEnabled(False)
        self.lb_x_value = QLabel("X_Value : ")
        self.le_x_value = QLineEdit()
        self.le_x_value.setPlaceholderText("        KHz")
        self.le_x_value.setValidator(QDoubleValidator())
        self.pb_marker = QPushButton("确认")
        self.lb_y_value = QLabel("Y_Value : ")
        self.le_y_value = QLineEdit()
        self.le_y_value.setEnabled(False)

        self.gl_marker.addWidget(self.lb_window, 0, 0)
        self.gl_marker.addWidget(self.cb_window, 0, 1)
        self.gl_marker.addWidget(self.lb_true_x_value, 0, 3)
        self.gl_marker.addWidget(self.le_true_x_value, 0, 4)
        self.gl_marker.addWidget(self.lb_x_value, 1, 0)
        self.gl_marker.addWidget(self.le_x_value, 1, 1)
        self.gl_marker.addWidget(self.pb_marker, 1, 2)
        self.gl_marker.addWidget(self.lb_y_value, 1, 3)
        self.gl_marker.addWidget(self.le_y_value, 1, 4)

        # 扫描频率、点数设置部分
        self.gb_sweep = QGroupBox("Sweep Setting")
        self.gl_sweep = QGridLayout(self.gb_sweep)
        self.gl_sweep.setHorizontalSpacing(15)
        self.gl_sweep.setVerticalSpacing(20)

        self.lb_start_freq = QLabel("起始频率：")
        self.le_start_freq = QLineEdit()
        self.le_start_freq.setValidator(QDoubleValidator())
        self.cb_start_unit = QComboBox()
        self.cb_start_unit.addItems(self.unit_list)
        self.pb_default_parameter_1 = QPushButton("配置1:100KHz,20GHz,100")

        self.lb_stop_freq = QLabel("截止频率：")
        self.le_stop_freq = QLineEdit()
        self.le_stop_freq.setValidator(QDoubleValidator())
        self.cb_stop_unit = QComboBox()
        self.cb_stop_unit.addItems(self.unit_list)
        self.pb_default_parameter_2 = QPushButton("配置2:500KHz,10GHz,500")

        self.lb_center_freq = QLabel("中值频率：")
        self.le_center_freq = QLineEdit()
        self.le_center_freq.setValidator(QDoubleValidator())
        self.cb_center_unit = QComboBox()
        self.cb_center_unit.addItems(self.unit_list)
        self.pb_default_parameter_3 = QPushButton("配置3:100KHz,10GHz,300")

        self.lb_point = QLabel("扫描点数：")
        self.le_point = QLineEdit()
        self.le_point.setValidator(QDoubleValidator())
        self.cb_point_unit = QComboBox()
        self.cb_point_unit.setEnabled(False)
        self.pb_default_parameter_4 = QPushButton("配置4:200KHz,5GHz,200")

        self.pb_save_setting = QPushButton("保存设置")
        self.pb_default = QPushButton("清空设置")

        self.le_list = [self.le_start_freq, self.le_stop_freq, self.le_center_freq, self.le_point]

        self.gl_sweep.addWidget(self.lb_start_freq, 0, 0)
        self.gl_sweep.addWidget(self.le_start_freq, 0, 1)
        self.gl_sweep.addWidget(self.cb_start_unit, 0, 2)
        self.gl_sweep.addWidget(self.pb_default_parameter_1, 0, 3)
        self.gl_sweep.addWidget(self.lb_stop_freq, 1, 0)
        self.gl_sweep.addWidget(self.le_stop_freq, 1, 1)
        self.gl_sweep.addWidget(self.cb_stop_unit, 1, 2)
        self.gl_sweep.addWidget(self.pb_default_parameter_2, 1, 3)
        self.gl_sweep.addWidget(self.lb_center_freq, 2, 0)
        self.gl_sweep.addWidget(self.le_center_freq, 2, 1)
        self.gl_sweep.addWidget(self.cb_center_unit, 2, 2)
        self.gl_sweep.addWidget(self.pb_default_parameter_3, 2, 3)
        self.gl_sweep.addWidget(self.lb_point, 3, 0)
        self.gl_sweep.addWidget(self.le_point, 3, 1)
        self.gl_sweep.addWidget(self.cb_point_unit, 3, 2)
        self.gl_sweep.addWidget(self.pb_default_parameter_4, 3, 3)
        self.gl_sweep.addWidget(self.pb_save_setting, 4, 0, 1, 2)
        self.gl_sweep.addWidget(self.pb_default, 4, 2, 1, 2)

        # 控温模块
        self.gb_temp = QGroupBox("Temp Setting")
        self.gl_temp = QGridLayout(self.gb_temp)
        self.gl_temp.setHorizontalSpacing(15)
        self.gl_temp.setVerticalSpacing(20)

        self.lb_temp = QLabel("Set Temp:")
        self.le_temp = QLineEdit()
        self.le_temp.setValidator(QDoubleValidator())
        self.pb_temp = QPushButton("保存温度")
        self.lb_current_temp = QLabel("Current Temp:")
        self.le_current_temp = QLineEdit()
        self.le_current_temp.setEnabled(False)
        self.gl_temp.addWidget(self.lb_temp, 0, 0)
        self.gl_temp.addWidget(self.le_temp, 0, 1)
        self.gl_temp.addWidget(self.pb_temp, 0, 2)
        self.gl_temp.addWidget(self.lb_current_temp, 0, 3)
        self.gl_temp.addWidget(self.le_current_temp, 0, 4)

        self.vl_setting.addWidget(self.gb_temp)
        self.vl_setting.addWidget(self.gb_window_setting)
        self.vl_setting.addWidget(self.gb_marker)
        self.vl_setting.addWidget(self.gb_sweep)
        self.gb_temp.setVisible(False)
        self.vl_setting.setStretch(1, 2)
        self.vl_setting.setStretch(2, 1)
        self.vl_setting.setStretch(3, 2)

        # 将各区域加入到中心窗口中
        self.hl_content.addWidget(self.left_widget)
        self.hl_content.addWidget(self.setting_widget)
        self.hl_content.setStretch(0, 2)
        self.hl_content.setStretch(1, 1)

        # 设置中心窗口控件
        self.setCentralWidget(self.main_widget)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window = CandyWindow.createWindow(window, 'blue')
    window.show()
    sys.exit(app.exec_())
