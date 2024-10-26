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

def set_servo_pwm(pwm, frequency, pulse_width_us):
    """
    设置舵机的PWM信号，脉宽为 500us 到 2500us。
    
    参数:
    - pwm: GPIO.PWM 实例
    - frequency: PWM频率，单位为 Hz，通常为 50Hz
    - pulse_width_us: 脉宽，单位为微秒，范围通常是 500~2500 微秒
    """
    pwm.ChangeFrequency(frequency)
    
    # 计算占空比：duty_cycle = (pulse_width_us / period_us) * 100
    period_us = 1_000_000 / frequency  # 50Hz时，周期为 20,000us
    duty_cycle = (pulse_width_us / period_us) * 100
    
    # 确保 duty_cycle 在 0 到 100 之间
    duty_cycle = max(0, min(duty_cycle, 100))
    
    pwm.ChangeDutyCycle(duty_cycle)

def main():
    GPIO.setmode(GPIO.BOARD)
    
    # 初始化 PWM
    frequency = 100  # 舵机的标准频率为 50Hz
    pulse_width_us = 1500  # 初始脉宽为 1500 微秒 (舵机中位)
    p = GPIO.PWM(output_pin, frequency)
    
    # 设置初始脉宽和频率
    set_servo_pwm(p, frequency, pulse_width_us)
    p.start(0)  # 开始时占空比为0，后续将通过 `set_servo_pwm` 调整

    print("Servo PWM running. Press CTRL+C to exit.")
    try:
        while True:
            # 动态调整脉宽（模拟舵机转动）
            time.sleep(0.5)
            
            # 调整脉宽
            pulse_width_us += 100  # 每次增加 100 微秒
            if pulse_width_us > 2500:  # 限制脉宽范围为 500 到 2500 微秒
                pulse_width_us = 500
            
            # 调用函数设置新的脉宽
            set_servo_pwm(p, frequency, pulse_width_us)
    finally:
        p.stop()
        GPIO.cleanup()

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main()
