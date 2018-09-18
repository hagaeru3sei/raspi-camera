#!/usr/bin/env python3
import datetime
import math
import os
import picamera
import sys
import signal
import time
import threading
import wiringpi as pi


pid = os.getpid()


class ButtonObserver(object):
    """ タクトスイッチ監視
    """

    pir_pin = 27

    def __init__(self):
        pi.wiringPiSetupGpio()
        pi.pinMode(self.pir_pin, pi.INPUT)

    def _execute(self, callback):
        while True:
            if pi.digitalRead(self.pir_pin) == pi.HIGH:
                callback()
            time.sleep(0.2)
        
    def observe(self, callback):
        threading.Thread(target=self._execute, args=(callback,)).start()


class Camera(object):

    ext_image = 'jpg'
    resolution = (3280, 2464,)
    data_dir = './images'

    def capture(self):
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        timestamp = math.ceil(datetime.datetime.now().timestamp())
        with picamera.PiCamera() as camera:
            camera.resolution = (self.resolution[0], self.resolution[1],)
            camera.rotation = 270
            camera.ISO = 400
            camera.contrast = 20
            camera.brightness = 65
            camera.saturation = -100
            camera.exposure_compensation = 5
            camera.meter_mode = 'spot'
            camera.start_preview()
            camera.capture('%s/capure-%s-%s.%s' % (self.data_dir, timestamp, current_time, self.ext_image,))


def signal_handler(signalnum, frame):
    sys.stderr.write("Killing pid %d\n" % (pid,))
    sys.stderr.write("signal number: %s. frame: %s\n" % (signalnum, frame,))
    os.kill(pid, signal.SIGKILL)
    sys.exit(1)


def main():

    # signal handler
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl-C
    signal.signal(signal.SIGTERM, signal_handler)  # kill -term [PID]
    signal.signal(signal.SIGHUP, signal_handler)  # kill -HUP [PID]
    signal.signal(signal.SIGQUIT, signal_handler)  # Quit

    camera = Camera()
    button = ButtonObserver()
    button.observe(camera.capture)

    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()

