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

class FireLock(Warlock):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up FireLock")
        super().__init__(*args, **kwargs)
        self._flame_wave_cycle_duration = 1.0 + (self._action_frame/25.0)
        self._last_flame_wave_cast = 0
        self._apocalypse_cycle_duration = 1.8 + (self._action_frame/25.0)
        self._last_apocalypse_cast = 0

    def _cast_apocalypse(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["apocalypse"]:
            raise ValueError("You did not set a hotkey for apocalypse!")
        keyboard.send(self._skill_hotkeys["apocalypse"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)

        #wait for apocalypse cooldown
        now = time.time()
        while (now - self._last_apocalypse_cast) < self._apocalypse_cycle_duration:
            wait(0.04)
            now = time.time()
        self._last_apocalypse_cast = now

        mouse.press(button="right")
        wait(0.06, 0.08)
        mouse.release(button="right")
        wait(self._cast_duration-0.06)
        
    def _cast_flame_wave(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        
        #wait for flame wave cooldown
        now = time.time()
        while (now - self._last_flame_wave_cast) < self._flame_wave_cycle_duration:
            wait(0.04)
            now = time.time()
        self._last_flame_wave_cast = now

        mouse.press(button="left")
        wait(0.06, 0.08)
        mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)
        wait(self._cast_duration-0.06)

    def _cast_apocalypse_flame_combo(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        self._cast_apocalypse(cast_pos_abs,spray)
        self._cast_flame_wave(cast_pos_abs,spray)
        self._cast_flame_wave(cast_pos_abs,spray)

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        start = time.time()

        self._cast_deathmark(cast_pos_abs)
        self._cast_lethargy(cast_pos_abs)
        while (time.time() - start) < Config().char["atk_len_pindle"]:
            self._cast_apocalypse_flame_combo(cast_pos_abs, spray=0)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=False)
        return True