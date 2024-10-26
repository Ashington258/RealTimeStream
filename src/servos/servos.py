# servo_control.py
import sys
import signal
import Hobot.GPIO as GPIO
import time

def signal_handler(signal, frame):
    sys.exit(0)

def ServosInit(output_pin, frequency=50, initial_pulse_width_us=1500):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    pwm = GPIO.PWM(output_pin, frequency)
    pwm.start(0)
    # 立即设置一个初始脉宽，确保进入有效信号状态
    set_servo_pwm(pwm, frequency, initial_pulse_width_us)
    return pwm

def set_servo_pwm(pwm, frequency, pulse_width_us):
    pwm.ChangeFrequency(frequency)
    period_us = 1_000_000 / frequency
    duty_cycle = (pulse_width_us / period_us) * 100
    duty_cycle = max(0, min(duty_cycle, 100))
    pwm.ChangeDutyCycle(duty_cycle)

def cleanup(pwm):
    pwm.stop()
    GPIO.cleanup()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    pwm = ServosInit(output_pin=32)
    print("Servo PWM running. Press CTRL+C to exit.")
    try:
        # 延迟操作，模拟舵机工作过程
        time.sleep(3)
    finally:
        cleanup(pwm)
