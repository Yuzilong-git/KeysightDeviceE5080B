# -*- encoding: utf-8 -*-
"""
@File    : temp_driver.py
@Time    : 2021/10/12 14:55
@Author  : Coco
"""
import time

import serial  # 导入模块
from utils.check_status import check_temp_addr


class TempDevice:
    def __init__(self):
        port = check_temp_addr()
        bps = 9600
        timeout = None
        self.ser = serial.Serial(port, bps, timeout=timeout, bytesize=8, parity=serial.PARITY_ODD, stopbits=1)
        # print("串口详情参数：", self.ser)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            orig = super(TempDevice, cls)
            cls._instance = orig.__new__(cls)
        return cls._instance

    # 发送
    def send_data(self, command):
        self.ser.write(command.encode("utf-8"))  # 写数据

    # 循环读
    def read_data(self):
        time.sleep(0.3)
        buffer = self.ser.inWaiting()
        print("self.ser.inWaiting()", buffer)
        data_info = self.ser.read(buffer)
        print("data_info", data_info)
        return data_info.decode('utf-8')

    def read_current_temp(self):
        self.send_data('%01#RDD0005100051**\r\n')
        recv_data = self.read_data().strip()
        print(recv_data, len(recv_data))
        if len(recv_data) == 12:
            current_temp = recv_data[6:10]
            print(current_temp)
            current_temp_hex = int(current_temp[-2:] + current_temp[-4:-2], 16)
            current_temp = current_temp_hex / 10 if current_temp_hex <= 32767 else (current_temp_hex - 65536) / 10
            return current_temp

    def set_target_temp(self, target_temp):
        target_temp_hex = hex(int(target_temp * 10)) if target_temp >= 0 else hex(int(target_temp * 10 + 65536)).encode(
            'utf-8')
        target_temp_hex = target_temp_hex[2:].zfill(4)
        target_temp_final = (target_temp_hex[2:] + target_temp_hex[0:2]).upper()
        self.send_data('%01#WDD0165201652{}**\r\n'.format(target_temp_final))
        time.sleep(0.3)
        self.ser.flushOutput()

    def set_run_mode(self):
        self.send_data("%01#WCSR00611**\r\n")
        time.sleep(0.3)
        self.ser.flushOutput()

    def set_stop_mode(self):
        self.send_data("%01#WCSR00610**\r\n")

    def read_mode(self):
        self.send_data('%01#RCSR100E**\r\n')
        current_mode = self.read_data().strip()
        if current_mode == "%01$WD13":
            current_mode = self.read_data().strip()
        return int(current_mode[-3])

    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     self.ser.close()  # 关闭串口
    def close(self):
        self.ser.close()


if __name__ == '__main__':
    device = TempDevice()
    print(device.read_current_temp())
    # device.set_target_temp(39)
    # device.set_run_mode()
    print(device.read_mode())
    # device.send_data(r"%01#WCSR00611**\r\n")
    # print(type('%01#WCSR00611**\r\n'.encode()))
    """
    开机操作              %01#WCSR00611**\r\n
    关机操作              %01#WCSR00610**\r\n
    开启程序模式           %01#WCSR001A1**\r\n
    读取运行状态           %01#RCSR100E**\r\n
    读取试验箱当前温度      %01#RDD0005100051**\r\n
    设置试验箱目标温度      %01#WDD0165201652 CDAB **\r\n
    选择程序模式温度控制模式  %01#WCSR24910**\r\n
    """
