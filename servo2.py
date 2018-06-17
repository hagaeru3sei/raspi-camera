# -*- coding: utf-8 -*-
import RPi.GPIO as GPIO
import threading
from time import sleep

# BCM
gp_out_servo1 = 12
gp_out_servo2 = 13


class Servo(object):

    servo1 = None
    servo2 = None
    start_value = 5
    pwm_hz = 100
    pulse_interval = pwm_hz / 10
    min_duty = 2.5
    is_in_operation = False
    operation_interval_sec = 0.007

    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(gp_out_servo1, GPIO.OUT)
        GPIO.setup(gp_out_servo2, GPIO.OUT)
        self.servo1 = GPIO.PWM(gp_out_servo1, self.pwm_hz)
        self.servo2 = GPIO.PWM(gp_out_servo2, self.pwm_hz)

    def _duty(self, angle) -> float:
        return angle / self.pulse_interval + self.min_duty

    def generate(self):
        self.is_in_operation = True
        # servo 1
        self.servo1.start(self.start_value)
        for i in reversed(range(40, 121)):
            self.servo1.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)
        for i in range(40, 170):
            self.servo1.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)
        for i in reversed(range(40, 170)):
            self.servo1.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)
        for i in range(40, 121):
            self.servo1.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)

        self.servo1.stop()

        # servo 2
        self.servo2.start(self.start_value)
        for i in reversed(range(40, 131)):
            self.servo2.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)
        for i in range(40, 180):
            self.servo2.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)
        for i in reversed(range(40, 180)):
            self.servo2.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)
        for i in range(40, 131):
            self.servo2.ChangeDutyCycle(self._duty(i))
            sleep(self.operation_interval_sec)

        self.servo2.stop()
        self.is_in_operation = False

    def __del__(self):
        if self.servo1 is not None:
            self.servo1.stop()
        if self.servo2 is not None:
            self.servo2.stop()
        GPIO.cleanup()


def main():
    servo = Servo()
    threading.Thread(target=servo.generate).start()

    while servo.is_in_operation:
        sleep(0.1)

    return 0


if __name__ == "__main__":
    main()
