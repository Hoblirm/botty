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

    def _move_to(self, abs_move: tuple[int, int]):
        pos_m = convert_abs_to_monitor(abs_move)
        self.pre_move()
        self.move(pos_m, force_move=True)

    def _cast_apocalypse(self, cast_pos_abs: tuple[float, float]):
        if not self._skill_hotkeys["apocalypse"]:
            raise ValueError("You did not set a hotkey for apocalypse!")
        keyboard.send(self._skill_hotkeys["apocalypse"])
        cast_pos_monitor = convert_abs_to_monitor(cast_pos_abs)
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
        
    def _cast_flame_wave(self, cast_pos_abs: tuple[float, float]):
        if not self._skill_hotkeys["flame_wave"]:
            raise ValueError("You did not set a hotkey for flame wave!")
        keyboard.send(self._skill_hotkeys["flame_wave"])
        cast_pos_monitor = convert_abs_to_monitor(cast_pos_abs)
        mouse.move(*cast_pos_monitor)
        
        #wait for flame wave cooldown
        now = time.time()
        while (now - self._last_flame_wave_cast) < self._flame_wave_cycle_duration:
            wait(0.04)
            now = time.time()
        self._last_flame_wave_cast = now

        mouse.press(button="right")
        wait(0.06, 0.08)
        mouse.release(button="right")
        wait(self._cast_duration-0.06)

    def _cast_ring_of_fire(self):
        if self._skill_hotkeys["ring_of_fire"]:    
            keyboard.send(self._skill_hotkeys["ring_of_fire"])
            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)

    def _cast_chaos_combo(self, cast_pos_abs: tuple[float, float], skip_ring_of_fire=False):
        self._cast_apocalypse(cast_pos_abs)
        self._cast_flame_wave(cast_pos_abs)
        if not skip_ring_of_fire:
            self._cast_ring_of_fire()
            self._cast_ring_of_fire()
        self._cast_flame_wave(cast_pos_abs)

    def _cast_deathmark_combo(self, cast_pos_abs: tuple[float, float], skip_ring_of_fire=False):
        self._cast_deathmark(cast_pos_abs)
        self._cast_chaos_combo(cast_pos_abs, skip_ring_of_fire)

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        start = time.time()

        self._cast_deathmark(cast_pos_abs)
        self._cast_lethargy(cast_pos_abs)
        while (time.time() - start) < Config().char["atk_len_pindle"]:
            self._cast_chaos_combo(cast_pos_abs, True)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=False)
        return True
    
    def kill_council(self) -> bool:
        start = time.time()
        while (time.time() - start) < Config().char["atk_len_trav"]:
            self._cast_chaos_combo((-325, -180))
            self._cast_chaos_combo((30, -30))
        self._move_to((300, -275))
        start = time.time()
        while (time.time() - start) < Config().char["atk_len_trav"]:
            self._cast_chaos_combo((0, -10))
            self._cast_chaos_combo((-200, -90))
        self._move_to((-500, 230))
        return True
        