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
from pather import Pather, Location
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

    def cast_buffs(self, casting_delay: float):               
        if self._skill_hotkeys["psychic_ward"]:
            keyboard.send(self._skill_hotkeys["psychic_ward"])
            wait(0.04)
            mouse.click(button="right")
            wait(casting_delay)
        
    def cast_town_buffs(self, curr_loc: Location):
        #Determine where to move mouse for summoning/consume based on location.
        cast_pos_monitor = None
        if curr_loc == Location.A3_TOWN_START:
            cast_pos_monitor = convert_abs_to_monitor((260,120))
        elif curr_loc == Location.A5_TOWN_START:
            cast_pos_monitor = convert_abs_to_monitor((-340,-60))
        else:
            Logger.warning(f"Unimplemented town location {curr_loc} and skipping town buffs")
            return
        wait(0.08)
        mouse.move(*cast_pos_monitor)

        if self._skill_hotkeys["summon_demon"]:
            keyboard.send(self._skill_hotkeys["summon_demon"])
            wait(0.04)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["consume"]:
            keyboard.send(self._skill_hotkeys["consume"])
            wait(0.04)
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["summon_demon_2"]:
            keyboard.send(self._skill_hotkeys["summon_demon_2"])
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