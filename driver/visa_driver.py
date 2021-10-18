# -*- encoding: utf-8 -*-
"""
@File    : visa_driver.py
@Time    : 2021/10/11 16:43
@Author  : Coco
"""
import time
import pyvisa

from utils.check_status import check_visa_addr


# pyvisa.log_to_screen()


class Device:
    def __init__(self):
        self.rm = pyvisa.ResourceManager()
        self.inst = self.rm.open_resource(check_visa_addr())
        self.inst.timeout = 10000
        self.set_external_mode()

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(Device, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    def set_external_mode(self):
        self.inst.write('TRIG:SOUR EXT')

    # 切换内部模式
    def set_internal_mode(self):
        self.inst.write("TRIG:SOUR IMM")
        # self.set_external_mode()

    def del_window(self):
        for i in range(1, 5):
            self.inst.write('display:window{}:state off'.format(i))

    def set_format_attr(self, window_num, attr_type):
        self.inst.write('calculate:measure{}:format {}'.format(window_num, attr_type))

    def preset(self):
        self.inst.write('SYST:PRES')

    def set_Meas(self, window_num, measure_mode):
        self.inst.write(':CALCulate:MEASure{}:PARameter {}'.format(window_num, measure_mode))

    def single_sweep(self, num):
        self.inst.write('sense{}:sweep:mode single'.format(num))
        self.inst.write('display:MEAS{}:y:scale:auto'.format(num))

    def get_y_data(self, win_num):
        origin_data_str = self.inst.query("CALCulate:MEAS{}:DATA:FDATA?".format(win_num))
        origin_data_list = origin_data_str.strip().split(',')
        final_data_list = [float(item) for item in origin_data_list]
        # print("y{} 值".format(win_num), final_data_list, len(final_data_list), end='\n')
        return final_data_list

    def get_x_data(self):
        try:
            origin_data_str = self.inst.query("sense:x:values?")
            origin_data_list = origin_data_str.strip().split(',')
            final_data_list = [float(item) for item in origin_data_list]
            # print("x 值", final_data_list, len(final_data_list))
            return final_data_list
        except pyvisa.errors.VisaIOError:
            return

    def set_s_mode(self, win_num, s_mode):
        self.inst.write('CALCulate{0}:PARameter:DEFine:EXT Meas{0},"{1}"'.format(win_num, s_mode))

    def create_window(self, s_select_list, format_list, sweep_parameter):
        # 把窗口都清空、重新开窗口、设置s参数、将win trace喂给s参数
        self.inst.write('CALC:PAR:DEL:ALL')
        self.del_window()
        for i in range(len(s_select_list)):
            self.inst.write('display:window{}:state on'.format(i + 1))  # 开窗口
            time.sleep(0.2)
            self.set_s_mode(i + 1, s_select_list[i])  # 设置s 参数
            time.sleep(0.2)
            self.inst.write('DISPlay:WINDow{0}:TRACe{0}:FEED Meas{0}'.format(i + 1))  # 喂
            time.sleep(0.2)
            self.set_sweep_parameter(sweep_parameter, i + 1)
            self.set_internal_mode()
            self.set_format_attr(i + 1, format_list[i])
            self.single_sweep(i + 1)

    def set_sweep_parameter(self, sweep_parameter, win_num):
        start_freq, end_freq, center_freq, sweep_points = sweep_parameter
        self.inst.write('SENS{}:FREQ:STAR {}'.format(win_num, start_freq))
        self.inst.write('SENS{}:FREQ:STOP {}'.format(win_num, end_freq))
        self.inst.write('SENS{}:FREQ:CENT {}'.format(win_num, center_freq))
        self.inst.write('SENS{}:SWE:POIN {}'.format(win_num, sweep_points))

    def get_plot_data(self, *args):
        origin_data = {0: self.get_x_data()}
        for y in args[0]:
            origin_data[y] = self.get_y_data(y)
        return origin_data


if __name__ == '__main__':
    s_select_list_setting = ['S11', 'S12', 'S21', 'S22']
    format_list_setting = ['MLOGarithmic', 'MLINear', 'PHASe', 'SWR']
    sweep_data = [100000, 26500000, 13200000, 201]
    my_device = Device()
    my_device.create_window(s_select_list_setting, format_list_setting, sweep_data)
    # final_dict = my_device.get_plot_data([1, 2, 3, 4])
    # print(final_dict)
    # my_device.set_s_mode(2, 'S21')
    # my_device.
