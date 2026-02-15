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

            #Static field can fail to cast if we right click on a wall.  We move mouse to 
            #center to prevent this.
            cast_pos_monitor = convert_abs_to_monitor((0, 0))
            mouse.move(*cast_pos_monitor)

            for _ in range(times):
                mouse.press(button="right")
                wait(0.06, 0.08)
                mouse.release(button="right")
                wait(self._cast_duration-0.06)

    def _cast_blizzorb_spike_combo(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        self._cast_blizzard(cast_pos_abs,spray)
        self._cast_frozen_orb(cast_pos_abs,spray)
        self._cast_glacial_spike(cast_pos_abs,spray, times=2)
        self._cast_frozen_orb(cast_pos_abs,spray)
    
    def _cast_blizzorb_whirlwind_combo(self, spray: float = 10):
        self._cast_blizzard([0, 0],spray)
        self._cast_frozen_orb([40, -40],spray)
        self._cast_static_field(times=2)
        self._cast_frozen_orb([-40,40],spray)
        self._cast_blizzard([0, 0],spray)
        self._cast_frozen_orb([-40,-40],spray)
        self._cast_static_field(times=2)
        self._cast_frozen_orb([40,40],spray)

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
        cast_pos_abs = [eldritch_pos_abs[0] * 1.00, eldritch_pos_abs[1] * 1.00]
        self._pather.traverse_nodes_fixed([(675, 30)], self)

        start = time.time()
        while (time.time() - start) < Config().char["atk_len_eldritch"]:
            self._cast_blizzard([40,-100],spray=0)
            self._cast_frozen_orb([80,-200],spray=0)
            self._cast_static_field(times=3)
            self._cast_frozen_orb([80,-200],spray=0)
        #self._cast_blizzorb_spike_combo(cast_pos_abs, spray=0)
        
        #Need to cast blizzard closer now that Eldritch approaches
        #cast_pos_abs = [eldritch_pos_abs[0] * 1.3, eldritch_pos_abs[1] * 1.3]

        #while (time.time() - start) < Config().char["atk_len_eldritch"]:
        #    self._cast_blizzorb_spike_combo(cast_pos_abs, spray=0)
        #self._pather.traverse_nodes_fixed("eldritch_end", self)
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.5, shenk_pos_abs[1] * 1.5]

        start = time.time()

        #First, cast blizzard once we are in range
        self._cast_blizzard(cast_pos_abs, spray=0)

        #Next, tele next to shenk to put orb and static in range
        pos_m = convert_abs_to_monitor((shenk_pos_abs[0] * 1.1, shenk_pos_abs[1] * 1.1))
        self.pre_move(wait_tp=True)
        self.move(pos_m, force_move=True)
        
        #Adjust cast position now that we are next to shenk and cast orb/static
        cast_pos_abs = [shenk_pos_abs[0] * 0.45, (shenk_pos_abs[1] * 0.45)-50]
        self._cast_frozen_orb(cast_pos_abs, spray=0)
        self._cast_static_field(times=3)

        #Continue blizzorb combo until attack length expires
        while (time.time() - start) < Config().char["atk_len_shenk"]:
            self._cast_blizzorb_spike_combo(cast_pos_abs, spray=0)
            
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], grab())
        if nihlathak_pos_abs is not None:
            cast_pos_abs = np.array([nihlathak_pos_abs[0] * 1.0, nihlathak_pos_abs[1] * 1.0])
            start = time.time()

            #First, cast blizzard once we are in range
            self._cast_blizzard(cast_pos_abs, spray=0)

            #Next, tele next to nihlathak to put orb and static in range
            pos_m = convert_abs_to_monitor((nihlathak_pos_abs[0] * 0.6, nihlathak_pos_abs[1] * 0.6))
            self.pre_move(wait_tp=True)
            self.move(pos_m, force_move=True)

            #Adjust cast position now that we are next to nihlathak and cast orb/static
            cast_pos_abs = [nihlathak_pos_abs[0] * 0.4, nihlathak_pos_abs[1] * 0.4]
            self._cast_frozen_orb(cast_pos_abs, spray=0)
            self._cast_static_field(times=3)

            #Continue blizzorb combo until attack length expires
            while (time.time() - start) < Config().char["atk_len_nihlathak"]:
                self._cast_blizzorb_spike_combo(cast_pos_abs, spray=0)
            self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
            return True
        else:
            return False
    
    def kill_council(self) -> bool:
        def clear_inside(use_static: bool):
            self._pather.traverse_nodes([228,229], self, timeout=2.2, do_pre_move=False, force_tp=True, use_tp_charge=True)
            if use_static:
                self._cast_static_field(2)
            self._cast_blizzorb_spike_combo([-80,-60])

        def clear_outside(use_static: bool):
            self._pather.traverse_nodes_fixed([(430, 642)], self)
            if use_static:
                self._cast_static_field(2)
            self._cast_blizzorb_spike_combo([-80,-60])

        start = time.time()

        clear_inside(True)
        clear_outside(True)

        while (time.time() - start) < Config().char["atk_len_trav"]:
            clear_inside(False)
            clear_outside(False)

        return True
    
    def kill_summoner(self) -> bool:
        #Set cast position right below alter
        cast_pos_abs = [0, 20]
        start = time.time()
        while (time.time() - start) < Config().char["atk_len_arc"]:
            self._cast_blizzorb_whirlwind_combo(cast_pos_abs, spray=0)
        return True
    
    def kill_cs_trash(self, location:str) -> bool:
        #Set cast position right below alter
        start = time.time()
        while (time.time() - start) < Config().char["atk_len_cs_trashmobs"]:
            self._cast_blizzorb_whirlwind_combo(spray=0)
        return True
    
    def kill_vizier(self, seal_layout:str) -> bool:
        #Set cast position right below alter
        start = time.time()
        while (time.time() - start) < Config().char["atk_len_diablo_vizier"]:
            self._cast_blizzorb_whirlwind_combo(spray=0)
        return True
        