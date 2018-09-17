import sys
import os
import signal
import time
import datetime
import math
import picamera
import threading
import wiringpi as pi


pid = os.getpid()


class InfraredObserver(object):
    """ 赤外線監視
    """

    pir_pin = 23

    def __init__(self):
        pi.wiringPiSetupGpio()
        pi.pinMode(self.pir_pin, pi.INPUT)

    def _execute(self, callback):
        while True:
            if pi.digitalRead(self.pir_pin) == pi.HIGH:
                callback()
            time.sleep(1)
        
    def observe(self, callback):
        threading.Thread(target=self._execute, args=(callback,)).start()


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
            # チャタリング防止
            time.sleep(0.2)

    def observe(self, callback):
        threading.Thread(target=self._execute, args=(callback,)).start()


class Camera(object):

    is_recording = False    
    ext_movie = 'h264'
    ext_image = 'jpg'
    resolution = (1920, 1080,)
    movie_capture_sec = 60
    data_dir = './data'

    def __init__(self):
        pass

    def capture(self) -> None:
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        timestamp = math.ceil(datetime.datetime.now().timestamp())
        with picamera.PiCamera() as camera:
            camera.resolution = (self.resolution[0], self.resolution[1],)
            camera.start_preview()
            camera.capture('%s/capure-%s-%s.%s' % (self.data_dir, timestamp, current_time, self.ext_image,))
            camera.stop_preview()

    def caputure_movie(self) -> None:
        if self.is_recording:
            print('Recording...')
            return None
        current_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        timestamp = math.ceil(datetime.datetime.now().timestamp())
        print('Start capturing the movie.')
        self.is_recording = True
        with picamera.PiCamera() as camera:
            camera.resolution = (self.resolution[0], self.resolution[1],)
            camera.start_preview()
            camera.start_recording('%s/capure-%s-%s.%s' % (self.data_dir, timestamp, current_time, self.ext_movie,))
            camera.wait_recording(self.movie_capture_sec)
            camera.stop_recording()
            camera.stop_preview()
        self.is_recording = False
        print('Stop capturing the movie.')


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
    infrared = InfraredObserver()
    infrared.observe(camera.caputure_movie)
    button = ButtonObserver()
    button.observe(camera.capture)

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
