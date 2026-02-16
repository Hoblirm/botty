import random
import keyboard
import time
import numpy as np

from health_manager import get_panel_check_paused, set_panel_check_paused
from inventory.personal import inspect_items
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab, convert_abs_to_screen
from utils.custom_mouse import mouse
from char.warlock import Warlock
from logger import Logger
from config import Config
from utils.misc import wait
from pather import Location
from target_detect import get_visible_targets, TargetInfo, log_targets

class EchoLock(Warlock):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up EchoLock")
        super().__init__(*args, **kwargs)

    def pre_buff(self):
        super().pre_buff()
        if self._skill_hotkeys["hex_bane"]:
            keyboard.send(self._skill_hotkeys["hex_bane"])
            mouse.click(button="right")
            wait(self._cast_duration)
        if self._skill_hotkeys["eldritch_blast"]:
            keyboard.send(self._skill_hotkeys["eldritch_blast"])
            mouse.click(button="right")
            wait(self._cast_duration)

    def _cast_echo_blast(self):
        n_move = (0, -10)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        if self._skill_hotkeys["ring_of_fire"]:
            keyboard.send(self._skill_hotkeys["ring_of_fire"])
            mouse.click(button="right")
            wait(Config().char["casting_frames"]*0.04)
        if self._skill_hotkeys["lethargy"]:
            keyboard.send(self._skill_hotkeys["lethargy"])
            mouse.click(button="right")
            wait(Config().char["casting_frames"]*0.04)
        n_move = (40, 30)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        keyboard.send(self._skill_hotkeys["echo_strike"])
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        n_move = (-40, -50)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        n_move = (-40, 30)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        n_move = (40, -50)
        pos_n = convert_abs_to_monitor(n_move)
        mouse.move(*pos_n)
        mouse.click(button="right")

    def _tele_and_echo(self, abs_move: tuple[int, int]):
        wait(Config().char["casting_frames"]*0.02)
        pos_m = convert_abs_to_monitor(abs_move)
        mouse.move(*pos_m)
        wait(Config().char["casting_frames"]*0.02)
        keyboard.send(Config().char["teleport"])
        mouse.click(button="right")
        wait(Config().char["casting_frames"]*0.04)
        self._cast_echo_blast()


    def kill_council(self) -> bool:
        if Config().char["teleport"]:
            self._cast_echo_blast()
            self._tele_and_echo((40, -10))
            self._tele_and_echo((0, -10))
            self._tele_and_echo((300, -275))
            self._tele_and_echo((-150, -90))
            self._tele_and_echo((150, 90))
            self._tele_and_echo((-150, -110))
            self._tele_and_echo((150, 90))
            self._tele_and_echo((-150, -110))
            self._tele_and_echo((150, 90))
            self._tele_and_echo((-200, 150))
            self._tele_and_echo((0, -10))
            self._tele_and_echo((0, -10))
            self._tele_and_echo((0, -10))
            wait(0.40)
            keyboard.send(Config().char["teleport"])
        return True
