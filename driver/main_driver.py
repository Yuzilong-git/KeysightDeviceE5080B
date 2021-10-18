# -*- encoding: utf-8 -*-
"""
@File    : main_driver.py
@Time    : 2021/10/9 18:12
@Author  : Coco
"""
import sys

import pyvisa

import matplotlib.pyplot as plt
from PyQt5.QtCore import Qt
import serial
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox, QApplication, QTableWidgetItem, QAction, QFileDialog, QWidget, QHBoxLayout, \
    QDesktopWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from utils.check_status import check_visa_addr, check_status, check_temp_addr, check_temp_status
from gui.main_gui import MainWindow
from mythread.export_thread import ExportThread
from driver.visa_driver import Device
from driver.temp_driver import TempDevice
from mythread.visa_thread import GetDataThread
from mythread.temp_thread import WaitTargetTemp


class MainAction(MainWindow):
    def __init__(self):
        super(MainAction, self).__init__()
        self.center()
        self._bind_actions()
        self.window_info = {0: ['S11', 'MLOGarithmic', 'black'], 1: ['S12', 'MLINear', 'blue'],
                            2: ['S21', 'PHASe', 'green'], 3: ['S22', 'SWR', 'orange']}
        self.table_header = ['Frequency', 'MLOGarithmic', 'MLINear', 'PHASe', 'SWR']
        self.sweep_data = [100000, 26500000, 13200000, 201]
        self.plot_data = {0: [1, 2, 3, 4, 5], 1: [2, 3, 4, 5, 6], 2: [3, 4, 5, 6, 7], 3: [4, 5, 6, 7, 8],
                          4: [5, 6, 7, 8, 9]}
        self.ax_list = []
        self.canvas_list = []
        self.s_select_list_setting = ['S11', 'S12', 'S21', 'S22']
        self.color_list_setting = ['black', 'blue', 'green', 'orange']
        self.format_list_setting = ['MLOGarithmic', 'MLINear', 'PHASe', 'SWR']
        self.start_action = QAction(QIcon('icon/start.png'), 'Start', self)
        self.start_action.setShortcut('Ctrl+S')
        self.export_action = QAction(QIcon('icon/export_excel.png'), 'Export', self)
        self.export_action.setShortcut('Ctrl+E')
        self.start_action.triggered.connect(self._start_action)
        self.start_action.setEnabled(False)
        self.export_action.triggered.connect(self._export)
        self.toolbar.addAction(self.start_action)
        self.toolbar.addAction(self.export_action)
        self._init()

    def _bind_actions(self):
        self.pb_save.clicked.connect(self._save_setting_1)
        self.pb_clear.clicked.connect(self._clear_confirm)
        self.pb_default.clicked.connect(self._clear_setting)
        self.pb_save_setting.clicked.connect(self._save_sweep_setting)
        self.pb_marker.clicked.connect(self._make_marker)
        self.pb_default_parameter_1.clicked.connect(self._set_parameter_1)
        self.pb_default_parameter_2.clicked.connect(self._set_parameter_2)
        self.pb_default_parameter_3.clicked.connect(self._set_parameter_3)
        self.pb_default_parameter_4.clicked.connect(self._set_parameter_4)
        self.static_temp_mode.triggered.connect(self._temp_static)
        self.set_temp_mode.triggered.connect(self._temp_set)
        self.pb_temp.clicked.connect(self._save_temp)

    def _init(self):
        self.mode = 0
        self.temp_used = 0
        # 导出按钮开始不可用
        self.export_action.setEnabled(False)

        # windows选择部分
        self.chb_window_1.setChecked(True)
        self.cb_s_select_1.setCurrentIndex(0)
        self.cb_format_1.setCurrentIndex(0)
        self.cb_color_1.setCurrentIndex(0)
        self.chb_window_2.setChecked(True)
        self.cb_s_select_2.setCurrentIndex(1)
        self.cb_format_2.setCurrentIndex(1)
        self.cb_color_2.setCurrentIndex(1)
        self.chb_window_3.setChecked(True)
        self.cb_s_select_3.setCurrentIndex(2)
        self.cb_format_3.setCurrentIndex(2)
        self.cb_color_3.setCurrentIndex(2)
        self.chb_window_4.setChecked(True)
        self.cb_s_select_4.setCurrentIndex(3)
        self.cb_format_4.setCurrentIndex(3)
        self.cb_color_4.setCurrentIndex(3)

        # marker部分
        self.pb_marker.setEnabled(False)  # 获取数据之前不可选

        # 扫描设置部分
        self.le_start_freq.setText('100')
        self.le_stop_freq.setText('26.5')
        self.le_center_freq.setText('13.2')
        self.le_point.setText('201')
        self.cb_stop_unit.setCurrentIndex(2)
        self.cb_center_unit.setCurrentIndex(2)

        # 表格部分
        self.table_widget.setColumnCount(5)
        self.table_widget.setHorizontalHeaderLabels(self.table_header)

        # 设备初始化
        try:
            self.device = Device()
            self.device.set_external_mode()
            self.device.preset()
            self._create_plot()
            self._start_action()
        except pyvisa.errors.VisaIOError:
            QMessageBox.critical(self, "错误", "仪表连接失败")

    # 保存设置按钮
    def _save_setting_1(self):
        # 看点的窗口是否连续
        self.window_info = {}  # 先清空这个
        # 每次保存设置前，将窗口列表置空
        self.table_header.clear()
        self.s_select_list_setting.clear()
        self.format_list_setting.clear()
        self.color_list_setting.clear()
        self.table_header.append('Frequency')
        # 保存窗口列表信息
        for num, chb in enumerate(self.chb_list):
            if chb.isChecked():
                self.window_info[num] = [self.s_list[self.cb_s_list[num].currentIndex()],
                                         self.format_list[self.cb_format_list[num].currentIndex()],
                                         self.color_list[self.cb_color_list[num].currentIndex()]]
                self.s_select_list_setting.append(self.window_info[num][0])
                self.table_header.append(self.window_info[num][1])
                self.format_list_setting.append(self.window_info[num][1])
                self.color_list_setting.append(self.window_info[num][2])
        # 判断是否连续
        a_list = [i for i in range(len(list(self.window_info.keys())))]
        origin_list = list(self.window_info.keys())
        if len(self.format_list_setting) != len(set(self.format_list_setting)):
            QMessageBox.critical(self, "错误", "存在重复格式，请重试！")
            return
        for i in range(len(a_list)):
            if a_list[i] != origin_list[i]:
                QMessageBox.critical(self, "错误", "窗口选择不连续\n请重试！")
                return
        self.start_action.setEnabled(True)
        self._create_plot()

        # 表格表头更新
        self.table_widget.setColumnCount(0)
        self.table_widget.setColumnCount(len(self.table_header))
        self.table_widget.setHorizontalHeaderLabels(self.table_header)
        QMessageBox.information(self, "信息", "保存窗口设置成功！")

    # 创建绘图窗口
    def _create_plot(self):
        self._clear_plot()
        # print(self.window_info)
        self._new_plot()

    # 清空图像绘制窗口
    def _clear_plot(self):
        if self.gl_plot_list:
            for plot_canvas in self.gl_plot_list:
                self.gl_plot.removeWidget(plot_canvas)
                plot_canvas.deleteLater()
            plt.cla()
            plt.close("all")
            self.gl_plot_list.clear()
            self.ax_list.clear()
            self.canvas_list.clear()

    # 确认清除
    def _clear_confirm(self):
        reply = QMessageBox.question(self, '提示', "是否要清空图像？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self._clear_plot()

    # 清除输入框参数
    def _clear_setting(self):
        for le_widget in self.le_list:
            le_widget.setText('')
        self.cb_start_unit.setCurrentIndex(0)
        self.cb_stop_unit.setCurrentIndex(2)
        self.cb_center_unit.setCurrentIndex(2)

    # 设置扫描参数
    def _save_sweep_setting(self):
        # 获取用户输入的数据，进行数据单位的换算，看数据是否合法，修改扫描数据信息
        start_freq = self.le_start_freq.text()
        stop_freq = self.le_stop_freq.text()
        center_freq = self.le_center_freq.text()
        points_data = self.le_point.text()
        # 检测是否输入
        if start_freq == '' or stop_freq == '' or center_freq == '' or points_data == '':
            QMessageBox.critical(self, "错误", "存在未输入参数")
            return
        # 获取输入单位
        start_unit = self.cb_start_unit.currentIndex()
        stop_unit = self.cb_stop_unit.currentIndex()
        center_unit = self.cb_center_unit.currentIndex()
        # 频率单位换算
        start_freq_pow = pow(1000, int(start_unit) + 1)
        start_freq = float(start_freq) * start_freq_pow
        stop_freq_pow = pow(1000, int(stop_unit) + 1)
        stop_freq = float(stop_freq) * stop_freq_pow
        center_freq_pow = pow(1000, int(center_unit) + 1)
        center_freq = float(center_freq) * center_freq_pow
        points_data = int(points_data)
        # 输入值范围合法性校验
        if start_freq < 100000 or stop_freq < 100000:
            QMessageBox.critical(self, "错误", "起始频率或截止频率输入值过低")
            return
        if start_freq > 26500000000 or stop_freq > 26500000000:
            QMessageBox.critical(self, '错误', "起始频率或截止频率输入值过高")
            return
        if start_freq >= stop_freq:
            QMessageBox.critical(self, '错误', "起始频率应小于截止频率")
            return
        if center_freq > stop_freq or center_freq < start_freq:
            QMessageBox.critical(self, '错误', "中频带宽应介于起始频率与截止频率之间")
            return
        if points_data < 0 or points_data > 10000:
            QMessageBox.critical(self, '错误', "扫描点数输入不合法")
            return
        # 数据监测成功，修改扫描数据值
        self.sweep_data = [start_freq, stop_freq, center_freq, points_data]
        QMessageBox.information(self, "信息", "保存扫描设置成功！")

    # 开始按钮事件
    def _start_action(self):
        self.status = check_status(check_visa_addr()) and check_temp_status(check_temp_addr())
        if self.status:
            self.device = Device()
            self.statusbar.showMessage("仪表通讯正常！")
            # 按钮置灰
            self.start_action.setEnabled(False)
            QApplication.processEvents()
            # 判断是否为变温模式,如果是变温模式
            if self.mode:
                self.wait_target_temp_thread.capture_temp_flag = True

            # 常温模式
            # 画图
            else:
                self._start_plot_thread()
        else:
            self.statusbar.showMessage("仪表连接失败！")
            QMessageBox.critical(self, "错误", "仪表未连接，请检查仪表状态！")

    # 开启变温线程
    def _start_temp_thread(self):
        self.wait_target_temp_thread = WaitTargetTemp(self.temp_device)
        # self.wait_target_temp_thread = WaitTargetTemp(1, 2)
        self.wait_target_temp_thread.signal.connect(self._start_plot_thread)
        self.wait_target_temp_thread.temp_signal.connect(self._set_text)
        self.wait_target_temp_thread.start()

    # 开始绘制线程--变温模式下达到温度槽函数
    def _start_plot_thread(self):
        if self.mode:
            self.wait_target_temp_thread.capture_temp_flag = False
        self.get_data_thread = GetDataThread(self.device, self.s_select_list_setting, self.format_list_setting,
                                             self.sweep_data, self.window_info)
        self.get_data_thread.signal.connect(self._recv_plot_fill)
        self.get_data_thread.start()

    # 导出功能
    def _export(self):
        try:
            file, ok = QFileDialog.getSaveFileName(self, "文件保存", "D://pycharmproject//E5080BNA//data//untitled",
                                                   "Microsoft Excel 工作表 (*.xlsx);;Picture Files (*.jpg)")
            if file.endswith('xlsx'):
                export_thread = ExportThread(self.plot_data, file, self.table_header)
                export_thread.signal.connect(self.box)
                export_thread.start()
                export_thread.wait()
            if file.endswith('jpg'):
                for i in range(len(self.window_info)):
                    file_name = file.split('.')[-2] + '_' + self.format_list_setting[i] + '.jpg'
                    plt.figure(i + 1)  # 移动指针
                    plt.savefig(file_name)
                self.box()
        except FileNotFoundError:
            pass

    # 设置当前温度槽函数
    def _set_text(self, current_temp):
        self.le_current_temp.setText(current_temp)

    # 弹窗槽函数
    def box(self):
        QMessageBox.information(self, "信息", "保存成功！")

    # 读数，获取读到的数据，存到全局变量中，确定哪个画布画哪个图，设置横纵坐标，正式画图
    def _recv_plot_fill(self, recv_data_dict):
        self.plot_data = recv_data_dict
        try:
            # 画图
            for i in range(len(self.window_info)):
                self.ax_list[i].cla()
                self.ax_list[i].set_title(self.format_list_setting[i])
                self.ax_list[i].plot(self.plot_data[0], self.plot_data[i + 1], color=self.color_list_setting[i])
                self.canvas_list[i].draw()
            # 填表格（获取读到的表头信息，重新绘制表头，确定数据长度，正式填表）
            self.table_widget.setRowCount(len(self.plot_data[0]))
            self.table_widget.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
            for i in range(len(self.plot_data)):
                for j in range(len(self.plot_data[i])):
                    table_item = QTableWidgetItem(str(self.plot_data[i][j]))
                    self.table_widget.setItem(j, i, table_item)
            # 将设置marker的按钮还原可用
            self.pb_marker.setEnabled(True)
            # 设置导出按钮还原可用
            self.export_action.setEnabled(True)
        except AttributeError or IndexError:
            QMessageBox.critical(self, "错误", "窗口参数未设置，请重试！")
            return
        finally:
            # 按钮还原
            self.start_action.setEnabled(True)

    # 标记功能
    def _make_marker(self):
        # 获取数据值
        win_index = self.cb_window.currentIndex()
        if win_index not in self.window_info.keys():
            QMessageBox.critical(self, "错误", "窗口选择有误，该窗口不存在！")
            return
        x_value = float(self.le_x_value.text()) * 1000
        # 去列表中寻找相距最近的x，及对应的y
        x_data = min(self.plot_data[0], key=lambda x: abs(x - x_value))
        y_data = self.plot_data[win_index + 1][self.plot_data[0].index(x_data)]
        # 文本框中显示x，y的真实坐标
        self.le_true_x_value.setText(str(x_data / 1000))
        self.le_y_value.setText(str(round(y_data, 6)))

        # 在图中标点
        self.ax_list[win_index].plot(x_data, y_data, 'o')
        self.canvas_list[win_index].draw()

    # 常用参数1
    def _set_parameter_1(self):
        self.le_start_freq.setText('100')
        self.le_stop_freq.setText('20')
        self.le_center_freq.setText('9.995')
        self.le_point.setText('100')
        self.cb_start_unit.setCurrentIndex(0)
        self.cb_stop_unit.setCurrentIndex(2)
        self.cb_center_unit.setCurrentIndex(2)

    # 常用参数2
    def _set_parameter_2(self):
        self.le_start_freq.setText('500')
        self.le_stop_freq.setText('10')
        self.le_center_freq.setText('4.75')
        self.le_point.setText('500')
        self.cb_start_unit.setCurrentIndex(0)
        self.cb_stop_unit.setCurrentIndex(2)
        self.cb_center_unit.setCurrentIndex(2)

    # 常用参数3
    def _set_parameter_3(self):
        self.le_start_freq.setText('100')
        self.le_stop_freq.setText('10')
        self.le_center_freq.setText('4.95')
        self.le_point.setText('300')
        self.cb_start_unit.setCurrentIndex(0)
        self.cb_stop_unit.setCurrentIndex(2)
        self.cb_center_unit.setCurrentIndex(2)

    # 常用参数4
    def _set_parameter_4(self):
        self.le_start_freq.setText('200')
        self.le_stop_freq.setText('5')
        self.le_center_freq.setText('2.4')
        self.le_point.setText('200')
        self.cb_start_unit.setCurrentIndex(0)
        self.cb_stop_unit.setCurrentIndex(2)
        self.cb_center_unit.setCurrentIndex(2)

    # 创建绘图画布，坐标轴
    def _new_plot(self):
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
        self.figure_1.subplots_adjust(right=0.96, left=0.15, bottom=0.2, top=0.9)
        self.ax_1 = self.figure_1.add_subplot(111)
        self.canvas_1 = FigureCanvas(self.figure_1)
        self.figure_2 = plt.figure()
        self.figure_2.subplots_adjust(right=0.96, left=0.15, bottom=0.2, top=0.9)
        self.canvas_2 = FigureCanvas(self.figure_2)
        self.ax_2 = self.figure_2.add_subplot(111)
        self.figure_3 = plt.figure()
        self.figure_3.subplots_adjust(right=0.96, left=0.15, bottom=0.2, top=0.9)
        self.canvas_3 = FigureCanvas(self.figure_3)
        self.ax_3 = self.figure_3.add_subplot(111)
        self.figure_4 = plt.figure()
        self.figure_4.subplots_adjust(right=0.96, left=0.15, bottom=0.2, top=0.9)
        self.canvas_4 = FigureCanvas(self.figure_4)
        self.ax_4 = self.figure_4.add_subplot(111)
        self.hl_plot_1.addWidget(self.canvas_1)
        self.hl_plot_2.addWidget(self.canvas_2)
        self.hl_plot_3.addWidget(self.canvas_3)
        self.hl_plot_4.addWidget(self.canvas_4)

        if len(self.window_info) == 1:
            self.gl_plot.addWidget(self.plot_1, 0, 0)
            self.gl_plot_list.append(self.plot_1)
            self.ax_list.append(self.ax_1)
            self.canvas_list.append(self.canvas_1)
        elif len(self.window_info) == 2:
            self.gl_plot.addWidget(self.plot_1, 0, 0)
            self.gl_plot.addWidget(self.plot_2, 1, 0)
            self.gl_plot_list.append(self.plot_1)
            self.gl_plot_list.append(self.plot_2)
            self.ax_list.append(self.ax_1)
            self.ax_list.append(self.ax_2)
            self.canvas_list.append(self.canvas_1)
            self.canvas_list.append(self.canvas_2)
            self.ax_1.set_xlabel("FREQ")
            self.ax_1.set_ylabel(self.format_list_setting[0])
            self.ax_2.set_xlabel("FREQ")
            self.ax_2.set_ylabel(self.format_list_setting[1])
        elif len(self.window_info) == 3:
            self.gl_plot.addWidget(self.plot_1, 0, 0)
            self.gl_plot.addWidget(self.plot_2, 0, 1)
            self.gl_plot.addWidget(self.plot_3, 1, 0, 1, 2)
            self.gl_plot_list.append(self.plot_1)
            self.gl_plot_list.append(self.plot_2)
            self.gl_plot_list.append(self.plot_3)
            self.ax_list.append(self.ax_1)
            self.ax_list.append(self.ax_2)
            self.ax_list.append(self.ax_3)
            self.canvas_list.append(self.canvas_1)
            self.canvas_list.append(self.canvas_2)
            self.canvas_list.append(self.canvas_3)
            self.ax_1.set_xlabel("FREQ")
            self.ax_1.set_ylabel(self.format_list_setting[0])
            self.ax_2.set_xlabel("FREQ")
            self.ax_2.set_ylabel(self.format_list_setting[1])
            self.ax_3.set_xlabel("FREQ")
            self.ax_3.set_ylabel(self.format_list_setting[2])
        elif len(self.window_info) == 4:
            self.gl_plot.addWidget(self.plot_1, 0, 0)
            self.gl_plot.addWidget(self.plot_2, 0, 1)
            self.gl_plot.addWidget(self.plot_3, 1, 0)
            self.gl_plot.addWidget(self.plot_4, 1, 1)
            self.gl_plot_list.append(self.plot_1)
            self.gl_plot_list.append(self.plot_2)
            self.gl_plot_list.append(self.plot_3)
            self.gl_plot_list.append(self.plot_4)
            self.ax_list.append(self.ax_1)
            self.ax_list.append(self.ax_2)
            self.ax_list.append(self.ax_3)
            self.ax_list.append(self.ax_4)
            self.canvas_list.append(self.canvas_1)
            self.canvas_list.append(self.canvas_2)
            self.canvas_list.append(self.canvas_3)
            self.canvas_list.append(self.canvas_4)
            self.ax_1.set_xlabel("FREQ")
            self.ax_1.set_ylabel(self.format_list_setting[0])
            self.ax_2.set_xlabel("FREQ")
            self.ax_2.set_ylabel(self.format_list_setting[1])
            self.ax_3.set_xlabel("FREQ")
            self.ax_3.set_ylabel(self.format_list_setting[2])
            self.ax_4.set_xlabel("FREQ")
            self.ax_4.set_ylabel(self.format_list_setting[3])

    # 常温模式
    def _temp_static(self):
        # 本来是选中的就直接跳出
        self.mode = 0
        if not self.static_temp_mode.isChecked():
            self.static_temp_mode.setChecked(True)
            return
        self.gb_temp.setVisible(False)
        self.set_temp_mode.setChecked(False)
        QMessageBox.information(self, "信息", "模式切换成功！")
        if self.temp_used:
            self.wait_target_temp_thread.read_temp_flag = False
            self.temp_device.close()

    # 变温模式
    def _temp_set(self):
        try:
            self.temp_device = TempDevice()
        except serial.serialutil.SerialException:
            self.set_temp_mode.setChecked(False)
            QMessageBox.critical(self, "错误", "温箱设备初始化失败，请检查后重试！")
            return

        self.mode = 1
        self.temp_used = 1
        if not self.set_temp_mode.isChecked():
            self.set_temp_mode.setChecked(True)
            return
        self.static_temp_mode.setChecked(False)
        self.gb_temp.setVisible(True)
        # self.le_current_temp.setText(str(self.temp_device.read_current_temp()))
        self._start_temp_thread()
        QMessageBox.information(self, "信息", "模式切换成功！")

    # 保存温度按钮事件
    def _save_temp(self):
        temp_data = self.le_temp.text()
        if temp_data == '':
            QMessageBox.critical(self, "错误", "输入值为空，请重试!")
            return
        if float(temp_data) > 400:
            QMessageBox.critical(self, "错误", "温度值过高，请重试!")
            return
        if float(temp_data) < 20:
            QMessageBox.critical(self, "错误", "温度值过低，请重试!")
            return
        reply = QMessageBox.question(self, '提示', "是否设置目标温度为{}°C ？".format(temp_data), QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.target_temp = float(temp_data)
            self.wait_target_temp_thread.target_temp = self.target_temp
            self.wait_target_temp_thread.set_temp_flag = True

    # 重写关闭事件
    def closeEvent(self, event):
        reply = QMessageBox.question(self, '提示', "是否要退出程序？", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.temp_used:
                self.temp_device.set_stop_mode()
            event.accept()
        else:
            event.ignore()

    # 定位窗口在屏幕中心
    def center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2,
                  (screen.height() - size.height()) / 2 - 30)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainAction()
    window.show()
    sys.exit(app.exec_())
