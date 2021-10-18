# -*- encoding: utf-8 -*-
"""
@File    : check_status.py
@Time    : 2021/10/11 16:43
@Author  : Coco
"""

import serial.tools.list_ports
import pyvisa
import configparser


def check_visa_addr():
    config = configparser.ConfigParser()
    config.read('config/my.ini', encoding='utf-8')
    # config.read('config/my.ini', encoding='utf-8')
    origin_addr = config.get('regular', 'visa_addr')
    return origin_addr


def check_temp_addr():
    config = configparser.ConfigParser()
    # config.read('../config/my.ini', encoding='utf-8')
    config.read('config/my.ini', encoding='utf-8')
    origin_addr = config.get('regular', 'temp_addr')
    return origin_addr


def check_status(addr):
    return_data = 0
    rm = pyvisa.ResourceManager()
    try:
        inst = rm.open_resource(addr)
        return_data = 1
        inst.close()
    except pyvisa.errors.VisaIOError:
        return_data = 0
    finally:
        return return_data


def check_temp_status(port):
    port_list = list(serial.tools.list_ports.comports())
    useful_port = []
    for i in port_list:
        useful_port.append(str(i)[:4])
    if port in useful_port:
        return True


if __name__ == '__main__':
    check_temp_status('COM9')
