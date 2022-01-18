import threading
import time
import os
from time import sleep
from gpiozero import LED
import logging
import sys

STATE_FILE = "/tmp/projector.state"
GPIO_UP = 6
GPIO_STOP = 26
GPIO_DOWN = 13

class MockDriver:
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def down(self):
        with open(STATE_FILE, "w") as f:
                self._logger.info("Driver: Unfolding")
                f.write("RUNNING")
                sleep(53)
                f.seek(0)
                f.truncate()
                f.write("UNFOLDED")
                self._logger.info("Driver: Unfolded")

    def up(self):
        with open(STATE_FILE, "w") as f:
                self._logger.info("Driver: folding")
                f.write("RUNNING")               
                f.seek(0)
                f.truncate()
                f.write("FOLDED")
                self._logger.info("Driver: folded")

class GPIODriver:

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def down(self):
        with open(STATE_FILE, "w") as f:
                self._logger.info("Driver: Unfolding")
                f.write("RUNNING")
                start = LED(GPIO_DOWN)
                start.on()
                sleep(0.1)
                start.off()
                sleep(53)
                stop.on()
                sleep(0.1)
                stop.off()
                f.seek(0)
                f.truncate()
                f.write("UNFOLDED")
                self._logger.info("Driver: Unfolded")

    def up(self):
        with open(STATE_FILE, "w") as f:
                self._logger.info("Driver: folding")
                f.write("RUNNING")
                start = LED(GPIO_UP)
                start.on()
                sleep(0.1)
                start.off()                
                f.seek(0)
                f.truncate()
                f.write("FOLDED")
                self._logger.info("Driver: folded")

class ProjectorDriver:

    def __init__(self, driver):
        self._logger = logging.getLogger(__name__)
        self._driver = driver

    def state(self):
        try:
            with open(STATE_FILE, "r") as f:
                state = f.read()
        except FileNotFoundError:
            state = None
        self._logger.debug("state: " + str(state))
        return state

    def ready(self):
        return self.state() != "RUNNING"

    def reset(self):
        if os.path.isfile(STATE_FILE):
            os.remove(STATE_FILE)

    def unfold(self):
        if not self.state() or self.state() == "FOLDED":
            self._logger.info("start unfolding")
            thread = threading.Thread(target=self._driver.down)
            thread.start()
        else:
            self._logger.error("unfold: illegal state")
            raise ValueError("unfold: illegal state")  

    def fold(self):
        if not self.state() or self.state() == "UNFOLDED":
            self._logger.info("start folding")
            thread = threading.Thread(target=self._driver.up)
            thread.start()
        else: 
            self._logger.error("fold: illegal state")
            raise ValueError("fold: illegal state") 

if __name__ == "__main__":
    formatter = logging.Formatter('%(name)s - %(message)s')
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    driver = MockDriver()
    projector = ProjectorDriver(driver)
   
    driver._logger.setLevel(logging.DEBUG)
    driver._logger.addHandler(handler)
    projector._logger.setLevel(logging.DEBUG)
    projector._logger.addHandler(handler)
    
    print("STATE:" + str(projector.state()))
    projector.unfold()
    sleep(5)
    print("STATE:" + str(projector.state()))
    projector.fold()
    sleep(1)
    print("STATE:" + str(projector.state()))
