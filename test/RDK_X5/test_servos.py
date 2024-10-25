#!/usr/bin/env python3
import sys
import signal
import Hobot.GPIO as GPIO
import time

class Servo:
    def __init__(self, pin, frequency=50, min_pulse=500, max_pulse=2500):
        """
        初始化舵机控制接口。
        :param pin: PWM控制的GPIO引脚
        :param frequency: PWM频率（默认为50Hz）
        :param min_pulse: 最小脉宽（单位为us，默认为500us）
        :param max_pulse: 最大脉宽（单位为us，默认为2500us）
        """
        self.pin = pin
        self.frequency = frequency
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.pwm = None
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        
        self.pwm = GPIO.PWM(self.pin, self.frequency)
        self.pwm.start(0)

    def set_pulse(self, pulse):
        """
        设置舵机的脉宽。
        :param pulse: 目标脉宽（单位为us）
        """
        if pulse < self.min_pulse or pulse > self.max_pulse:
            raise ValueError("Pulse width out of range")
        duty_cycle = (pulse / 20000.0) * 100  # 计算占空比，周期为20ms
        self.pwm.ChangeDutyCycle(duty_cycle)

    def cleanup(self):
        """
        停止PWM并清理GPIO。
        """
        if self.pwm:
            self.pwm.stop()
        GPIO.cleanup()

# 例子代码，用于演示Servo类的使用
def signal_handler(signal, frame):
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    # 创建一个Servo对象，连接到引脚33
    servo = Servo(pin=33)

    try:
        print("Moving servo to min position (500us)")
        servo.set_pulse(500)
        time.sleep(1)
        
        print("Moving servo to mid position (1500us)")
        servo.set_pulse(1500)
        time.sleep(1)

        print("Moving servo to max position (2500us)")
        servo.set_pulse(2500)
        time.sleep(1)

        # 持续循环模拟舵机逐步移动
        pulse = 500
        incr = 50
        while True:
            servo.set_pulse(pulse)
            time.sleep(0.1)
            pulse += incr
            if pulse >= 2500 or pulse <= 500:
                incr = -incr

    finally:
        servo.cleanup()

if __name__ == '__main__':
    main()
