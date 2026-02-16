import keyboard
import random
import time

from char import CharacterCapabilities
from char.warlock import Warlock
from config import Config
from logger import Logger
from pather import Location
from pather import Pather
from pather import Pather, Location
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from target_detect import get_visible_targets
from ui import skills
from utils.custom_mouse import mouse
from utils.misc import wait

class AbyssLock(Warlock):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up AbyssLock")
        super().__init__(*args, **kwargs)
        self._miasma_chain_cycle_duration = 1.2 + (self._action_frame/25.0)
        self._last_miasma_chain_cast = 0
        self._abyss_cycle_duration = 2.0 + (self._action_frame/25.0)
        self._last_abyss_cast = 0

    def _cast_abyss(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["abyss"]:
            raise ValueError("You did not set a hotkey for abyss!")
        keyboard.send(self._skill_hotkeys["abyss"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)

        #wait for abyss cooldown
        now = time.time()
        while (now - self._last_abyss_cast) < self._abyss_cycle_duration:
            wait(0.04)
            now = time.time()
        self._last_abyss_cast = now

        mouse.press(button="right")
        wait(0.06, 0.08)
        mouse.release(button="right")
        wait(self._cast_duration-0.06)
        
    def _cast_miasma_chain(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["miasma_chain"]:
            raise ValueError("You did not set a hotkey for miasma chain!")
        keyboard.send(self._skill_hotkeys["miasma_chain"])
        
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        
        #wait for miasma chain cooldown
        now = time.time()
        while (now - self._last_miasma_chain_cast) < self._miasma_chain_cycle_duration:
            wait(0.04)
            now = time.time()
        self._last_miasma_chain_cast = now

        mouse.press(button="right")
        wait(0.06, 0.08)
        mouse.release(button="right")
        wait(self._cast_duration-0.06)

    def _cast_miasma_bolt(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        mouse.press(button="left")
        wait(0.06, 0.08)
        mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)
        wait(self._cast_duration-0.06)

    def _cast_abyss_miasma_combo(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        self._cast_abyss(cast_pos_abs,spray)
        self._cast_miasma_chain(cast_pos_abs,spray)
        self._cast_miasma_bolt(cast_pos_abs,spray)
        self._cast_miasma_chain(cast_pos_abs,spray)
        self._cast_miasma_bolt(cast_pos_abs,spray)

    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 1.0, pindle_pos_abs[1] * 1.0]
        start = time.time()

        self._cast_deathmark(cast_pos_abs)
        self._cast_lethargy(cast_pos_abs)
        while (time.time() - start) < Config().char["atk_len_pindle"]:
            self._cast_abyss_miasma_combo(cast_pos_abs, spray=0)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            self._pather.traverse_nodes((Location.A5_PINDLE_SAFE_DIST, Location.A5_PINDLE_END), self, timeout=1.0, do_pre_move=False)
        return True
    