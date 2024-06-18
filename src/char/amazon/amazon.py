import keyboard
from ui import skills
import time
import random
from utils.custom_mouse import mouse
from char import IChar, CharacterCapabilities
from pather import Pather
from logger import Logger
from config import Config
from utils.misc import wait
from screen import convert_abs_to_screen, convert_abs_to_monitor
from pather import Pather

class Amazon(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        Logger.info("Setting up Amazon")
        super().__init__(skill_hotkeys)
        self._pather = pather

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()


    def _cast_valkyrie(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["valkyrie"]:
            keyboard.send(self._skill_hotkeys["valkyrie"])
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)

            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)