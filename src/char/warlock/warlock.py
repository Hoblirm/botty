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
#import cv2 #for Diablo
from item.pickit import PickIt #for Diablo

class Warlock(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather, pickit: PickIt):
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._pickit = pickit
        self._picked_up_items = False
        self._last_click_cast = 0
        self._action_frame = 9
        if Config().char["casting_frames"] == 15 or Config().char["casting_frames"] == 14:
            self._action_frame = 8
        elif Config().char["casting_frames"] == 13 or Config().char["casting_frames"] == 12:
            self._action_frame = 7
        elif Config().char["casting_frames"] == 11 or Config().char["casting_frames"] == 10:
            self._action_frame = 6
        elif Config().char["casting_frames"] == 9:
            self._action_frame = 5

    def pre_buff(self):
        n_move = (0, -10)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        if Config().char["cta_available"]:
            self._pre_buff_cta()
                                
        if self._skill_hotkeys["psychic_ward"]:
            keyboard.send(self._skill_hotkeys["psychic_ward"])
            wait(0.04)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["summon_demon"]:
            keyboard.send(self._skill_hotkeys["summon_demon"])
            wait(0.04)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["summon_demon2"]:
            keyboard.send(self._skill_hotkeys["summon_demon2"])
            wait(0.04)
            mouse.click(button="right")
            wait(self._cast_duration)

    def _cast_deathmark(self, cast_pos_abs: tuple[float, float]):
        if self._skill_hotkeys["deathmark"]:
            keyboard.send(self._skill_hotkeys["deathmark"])
            cast_pos_monitor = convert_abs_to_monitor((cast_pos_abs[0], cast_pos_abs[1]))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)

    def _cast_lethargy(self, cast_pos_abs: tuple[float, float]):
        if self._skill_hotkeys["lethargy"]:
            keyboard.send(self._skill_hotkeys["lethargy"])
            cast_pos_monitor = convert_abs_to_monitor((cast_pos_abs[0], cast_pos_abs[1]))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)