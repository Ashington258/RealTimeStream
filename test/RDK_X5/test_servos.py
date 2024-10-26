#!/usr/bin/env python3
import sys
import signal
import Hobot.GPIO as GPIO
import time


def signal_handler(signal, frame):
    sys.exit(0)


def ServosInit(output_pin, frequency=50, initial_pulse_width_us=1500):
    """
    初始化舵机的 PWM 设置。

    参数:
    - output_pin: 输出的 GPIO 管脚
    - frequency: PWM 频率，默认为 50Hz
    - initial_pulse_width_us: 初始脉宽，单位为微秒，默认为 1500 微秒
    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    pwm = GPIO.PWM(output_pin, frequency)

    # 设置初始频率和脉宽
    set_servo_pwm(pwm, frequency, initial_pulse_width_us)
    pwm.start(0)  # 开始时占空比为 0，后续可通过 `set_servo_pwm` 调整

    return pwm


def set_servo_pwm(pwm, frequency, pulse_width_us):
    """
    设置舵机的 PWM 信号，脉宽为 500us 到 2500us。

    参数:
    - pwm: GPIO.PWM 实例
    - frequency: PWM 频率，单位为 Hz，通常为 50Hz
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
    output_pin = 32  # 使用的 PWM 管脚

    # 初始化舵机
    frequency = 50  # 舵机的标准频率
    initial_pulse_width_us = 1500  # 初始脉宽 (中位)
    pwm = ServosInit(output_pin, frequency, initial_pulse_width_us)

    print("Servo PWM running. Press CTRL+C to exit.")
    try:
        pulse_width_us = initial_pulse_width_us
        while True:
            # 动态调整脉宽（模拟舵机转动）
            time.sleep(0.5)

            # 调整脉宽
            pulse_width_us += 100  # 每次增加 100 微秒
            if pulse_width_us > 2500:  # 限制脉宽范围为 500 到 2500 微秒
                pulse_width_us = 500

            # 调用函数设置新的脉宽
            set_servo_pwm(pwm, frequency, pulse_width_us)
    finally:
        pwm.stop()
        GPIO.cleanup()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    main()
