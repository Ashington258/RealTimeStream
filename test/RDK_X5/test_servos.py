#!/usr/bin/env python3
import sys
import signal
import Hobot.GPIO as GPIO
import time

def signal_handler(signal, frame):
    sys.exit(0)

# 支持PWM的管脚: 32 和 33，使用PWM时确保该管脚未被其他功能占用
output_pin = 32
GPIO.setwarnings(False)
def Servos_Init(output_pin, frequency, pulse_width_us):
    """
    初始化舵机的PWM设置。
    
    参数:
    - output_pin: PWM输出引脚编号。
    - frequency: PWM信号的频率。
    - pulse_width_us: 脉冲宽度，单位为微秒。
    
    返回:
    - p: PWM控制对象。
    """
    p = GPIO.PWM(output_pin, frequency)  # 创建PWM对象并设置频率
    p.start(0)  # 开始时占空比为0
    set_servo_pwm(p, frequency, pulse_width_us)  # 设置舵机的PWM参数
    return p

def set_servo_pwm(pwm, frequency, pulse_width_us):
    """设置舵机的PWM信号，脉宽为500us到2500us。
    
    参数:
    pwm: PWM对象，用于控制舵机。
    frequency: PWM信号的频率。
    pulse_width_us: PWM信号的脉宽，单位为微秒。
    """
    pwm.ChangeFrequency(frequency)  # 设置PWM信号的频率
    period_us = 1_000_000 / frequency  # 计算PWM信号的周期，单位为微秒
    duty_cycle = (pulse_width_us / period_us) * 100  # 计算占空比
    duty_cycle = max(0, min(duty_cycle, 100))  # 确保占空比在0到100之间
    pwm.ChangeDutyCycle(duty_cycle)  # 设置PWM信号的占空比


def main():
    GPIO.setmode(GPIO.BOARD)
    
    frequency = 50  # 舵机的标准频率
    pulse_width_us = 1500  # 初始脉宽

    # 初始化舵机
    p = Servos_Init(output_pin, frequency, pulse_width_us)

    print("Servo PWM running. Press CTRL+C to exit.")
    try:
        while True: 
            time.sleep(0.01)
            pulse_width_us += 10  # 每次增加10微秒
            if pulse_width_us > 2500:  # 限制脉宽范围为500到2500微秒
                pulse_width_us = 500
            set_servo_pwm(p, frequency, pulse_width_us)
    finally:
        p.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
