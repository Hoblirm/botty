import keyboard
from char.sorceress import Sorceress
from utils.custom_mouse import mouse
from logger import Logger
from utils.misc import wait, rotate_vec, unit_vector
import random
import time
from pather import Location
import numpy as np
from screen import convert_abs_to_monitor, grab, convert_screen_to_abs
from config import Config
import template_finder

class BlizzorbSorc(Sorceress):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Blizzorb Sorc")
        super().__init__(*args, **kwargs)
        #Nihlathak Bottom Right
        self._pather.offset_node(505, (50, 200))
        self._pather.offset_node(506, (40, -10))
        #Nihlathak Top Right
        self._pather.offset_node(510, (700, -55))
        self._pather.offset_node(511, (30, -25))
        #Nihlathak Top Left
        self._pather.offset_node(515, (-120, -100))
        self._pather.offset_node(517, (-18, -58))
        #Nihlathak Bottom Left
        self._pather.offset_node(500, (-150, 200))
        self._pather.offset_node(501, (10, -33))
        self._orb_cycle_duration = 1.0 + (self._action_frame/25.0)
        self._last_orb_cast = 0
        self._blizz_cycle_duration = 1.8 + (self._action_frame/25.0)
        self._last_blizz_cast = 0
    
    def _cast_blizzard(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["blizzard"]:
            raise ValueError("You did not set a hotkey for blizzard!")
        keyboard.send(self._skill_hotkeys["blizzard"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)

        #wait for blizzard cooldown
        now = time.time()
        while (now - self._last_blizz_cast) < self._blizz_cycle_duration:
            wait(0.04)
            now = time.time()
        self._last_blizz_cast = now

        mouse.press(button="right")
        wait(0.06, 0.08)
        mouse.release(button="right")
        wait(self._cast_duration-0.06)
        
    def _cast_frozen_orb(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        
        #wait for frozen orb cooldown
        now = time.time()
        while (now - self._last_orb_cast) < self._orb_cycle_duration:
            wait(0.04)
            now = time.time()
        self._last_orb_cast = now

        mouse.press(button="left")
        wait(0.06, 0.08)
        mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)
        wait(self._cast_duration-0.06)

    def _cast_glacial_spike(self, cast_pos_abs: tuple[float, float], spray: float = 10, times=1):
        if not self._skill_hotkeys["glacial_spike"]:
            raise ValueError("You did not set a hotkey for glacial spike!")
        keyboard.send(self._skill_hotkeys["glacial_spike"])
        for _ in range(times):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)
    
    def _cast_static_field(self, times=1):
        if self._skill_hotkeys["static_field"]:
            keyboard.send(self._skill_hotkeys["static_field"])
            for _ in range(times):
                mouse.click(button="right")
                wait(self._cast_duration)

    def _cast_blizzorb_spike_combo(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        self._cast_blizzard(cast_pos_abs,spray)
        self._cast_frozen_orb(cast_pos_abs,spray)
        self._cast_glacial_spike(cast_pos_abs,spray)
        self._cast_glacial_spike(cast_pos_abs,spray)
        self._cast_frozen_orb(cast_pos_abs,spray)
        
    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 0.9, pindle_pos_abs[1] * 0.9]
        start = time.time()
        while (time.time() - start) < Config().char["atk_len_pindle"]:
            self._cast_blizzorb_spike_combo(cast_pos_abs, spray=0)

        self._pather.traverse_nodes_fixed("pindle_end", self)
        return True

    def kill_eldritch(self) -> bool:
        eldritch_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eldritch_pos_abs[0] * 1.5, eldritch_pos_abs[1] * 1.5]

        start = time.time()
        self._cast_blizzorb_spike_combo(cast_pos_abs, spray=0)
        
        #Need to cast blizzard closer now that Eldritch moves up
        cast_pos_abs = [eldritch_pos_abs[0] * 1.3, eldritch_pos_abs[1] * 1.3]

        while (time.time() - start) < Config().char["atk_len_eldritch"]:
            self._cast_blizzorb_spike_combo(cast_pos_abs, spray=0)
        self._pather.traverse_nodes_fixed("eldritch_end", self)
        return True

    def kill_shenk(self) -> bool:
        # pos_m = convert_abs_to_monitor((100, 170))
        # self.pre_move()
        # self.move(pos_m, force_move=True)
        # #lower left posistion
        # self._pather.traverse_nodes([151], self, timeout=2.5, force_tp=False)
        # self._cast_static()
        # self._blizzard((-250, 100), spray=10)
        # self._ice_blast((60, 70), spray=60)
        # self._blizzard((400, 200), spray=10)
        # self._cast_static()
        # self._ice_blast((-300, 100), spray=60)
        # self._blizzard((185, 200), spray=10)
        # pos_m = convert_abs_to_monitor((-10, 10))
        # self.pre_move()
        # self.move(pos_m, force_move=True)
        # self._cast_static()
        # self._blizzard((-300, -270), spray=10)
        # self._ice_blast((-20, 30), spray=60)
        # wait(1.0)
        # #teledance 2
        # pos_m = convert_abs_to_monitor((150, -240))
        # self.pre_move()
        # self.move(pos_m, force_move=True)
        # #teledance attack 2
        # self._cast_static()
        # self._blizzard((450, -250), spray=10)
        # self._ice_blast((150, -100), spray=60)
        # self._blizzard((0, -250), spray=10)
        # wait(0.3)
        # #Shenk Kill
        # self._cast_static()
        # self._blizzard((100, -50), spray=10)
        # # Move to items
        # self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        return True


    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], grab())
        if nihlathak_pos_abs is not None:
            cast_pos_abs = np.array([nihlathak_pos_abs[0] * 1.0, nihlathak_pos_abs[1] * 1.0])
            start = time.time()
            while (time.time() - start) < Config().char["atk_len_nihlathak"]:
                self._blizzard(cast_pos_abs, spray=0)
                self._frozen_orb(cast_pos_abs, spray=0)
                self._frozen_orb(cast_pos_abs, spray=0)
        else:
            return False
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True

    def kill_summoner(self) -> bool:
        # Attack
        # cast_pos_abs = np.array([0, 0])
        # pos_m = convert_abs_to_monitor((-20, 20))
        # mouse.move(*pos_m, randomize=80, delay_factor=[0.5, 0.7])
        # for _ in range(int(Config().char["atk_len_arc"])):
        #     self._blizzard(cast_pos_abs, spray=11)
        #     self._ice_blast(cast_pos_abs, spray=11)
        # wait(self._cast_duration, self._cast_duration + 0.2)
        return True