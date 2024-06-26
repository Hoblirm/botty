import keyboard
from ui import skills
from utils.custom_mouse import mouse
from char import IChar
from pather import Pather
from logger import Logger
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab
from config import Config
from utils.misc import wait, rotate_vec, unit_vector
import time
import random
from pather import Location, Pather
import numpy as np


class Trapsin(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        Logger.info("Setting up Trapsin")
        super().__init__(skill_hotkeys)
        self._pather = pather

    def pre_buff(self):
        if Config().char["cta_available"]:
            self._pre_buff_cta()
        if self._skill_hotkeys["fade"]:
            keyboard.send(self._skill_hotkeys["fade"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(self._cast_duration)

    def pre_move(self, wait_tp: bool = False):
        super().pre_move(wait_tp=wait_tp)
        if self._skill_hotkeys["burst_of_speed"]:
            self._cast_burst_of_speed()

    def _left_attack(self, cast_pos_abs: tuple[float, float], spray: int = 10):
        keyboard.send(Config().char["stand_still"], do_release=False)
        if self._skill_hotkeys["skill_left"]:
            keyboard.send(self._skill_hotkeys["skill_left"])
        for _ in range(4):
            x = cast_pos_abs[0] + (random.random() * 2*spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2*spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            mouse.press(button="left")
            wait(0.2, 0.3)
            mouse.release(button="left")
        keyboard.send(Config().char["stand_still"], do_press=False)

    def _right_attack(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        keyboard.send(self._skill_hotkeys["lightning_sentry"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        def atk(num: int):
            for _ in range(num):
                mouse.press(button="right")
                wait(0.20)
                mouse.release(button="right")
                wait(0.15)
        atk(4)
        keyboard.send(self._skill_hotkeys["death_sentry"])
        atk(1)
    
    def _cast_shadow_warrior(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["shadow_warrior"]:
            keyboard.send(self._skill_hotkeys["shadow_warrior"])
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)

            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)

    def _cast_mind_blast(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if self._skill_hotkeys["mind_blast"]:
            keyboard.send(self._skill_hotkeys["mind_blast"])
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)

            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)
    
    def _cast_burst_of_speed(self):
        if self._skill_hotkeys["burst_of_speed"]:
            keyboard.send(self._skill_hotkeys["burst_of_speed"])

            mouse.press(button="right")
            wait(0.06, 0.08)
            mouse.release(button="right")
            wait(self._cast_duration-0.06)

    def _cast_fire_blast(self, cast_pos_abs: tuple[float, float], spray: float = 10, duration: float = 0.3):
        keyboard.send(Config().char["stand_still"], do_release=False)
        
        #Get mouse in initial target logcation
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        
        #We just hold down left mouse button to ensure we get full attack speed.
        mouse.press(button="left")
        now = start = time.time()
        while (now - start) < duration:
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            wait(0.06, 0.08)
            now = time.time()
        mouse.release(button="left")

        keyboard.send(Config().char["stand_still"], do_press=False)
        wait(self._attack_duration-0.06)

    def _cast_lightning_sentry(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["lightning_sentry"]:
            Logger.error("Lightning sentry hotkey not assigned.  Required for trapsin!")
        keyboard.send(self._skill_hotkeys["lightning_sentry"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)

        mouse.press(button="right")
        wait(0.06, 0.08)
        mouse.release(button="right")
        wait(self._attack_duration-0.06)

    def _cast_death_sentry(self, cast_pos_abs: tuple[float, float], spray: float = 10):
        if not self._skill_hotkeys["death_sentry"]:
            Logger.error("Death sentry hotkey not assigned.  Required for trapsin!")
        keyboard.send(self._skill_hotkeys["death_sentry"])
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)

        mouse.press(button="right")
        wait(0.06, 0.08)
        mouse.release(button="right")
        wait(self._attack_duration-0.06)

    
    def kill_pindle(self) -> bool:
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])
        cast_pos_abs = [pindle_pos_abs[0] * 1.2, pindle_pos_abs[1] * 1.2]
        trap_cast_pos_abs = [pindle_pos_abs[0] * 0.45, pindle_pos_abs[1] * 0.40]
        start = time.time()
        self._cast_mind_blast(cast_pos_abs=cast_pos_abs)
        cast_pos_abs = [pindle_pos_abs[0] * 0.8, pindle_pos_abs[1] * 0.8]
        self._cast_shadow_warrior(cast_pos_abs=cast_pos_abs)
        for _ in range(4):
            self._cast_lightning_sentry(cast_pos_abs=trap_cast_pos_abs, spray=5.0)
        self._cast_death_sentry(cast_pos_abs=trap_cast_pos_abs, spray=5.0)
        
        
        trap_cast_pos_abs = [pindle_pos_abs[0] * 0.50, pindle_pos_abs[1] * 0.50]
        time_remaining = Config().char["atk_len_pindle"] - (time.time() - start)
        self._cast_fire_blast(cast_pos_abs=cast_pos_abs, duration=time_remaining)
        
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            #Walk just close enough to pindle's position to see items.  That way we leave sooner if there is nothing to grab
            x_m, y_m = convert_abs_to_monitor([pindle_pos_abs[0] * 0.65, pindle_pos_abs[1] * 0.65])
            self.move((x_m, y_m), force_move=True)
        return False

    def kill_eldritch(self) -> bool:
        eldritch_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eldritch_pos_abs[0] * 1.5, eldritch_pos_abs[1] * 1.5]
        trap_cast_pos_abs = [eldritch_pos_abs[0] * 0.70, eldritch_pos_abs[1] * 0.70]

        start = time.time()
        self._cast_shadow_warrior(cast_pos_abs=cast_pos_abs)
        for _ in range(4):
            self._cast_lightning_sentry(cast_pos_abs=trap_cast_pos_abs)
        self._cast_death_sentry(cast_pos_abs=trap_cast_pos_abs)

        time_remaining = Config().char["atk_len_eldritch"] - (time.time() - start)
        self._cast_fire_blast(cast_pos_abs=cast_pos_abs, duration=time_remaining)
        
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            x_m, y_m = convert_abs_to_monitor([eldritch_pos_abs[0] * 1.0, eldritch_pos_abs[1] * 1.0])
            self.move((x_m, y_m), force_move=True)
        return True

    def kill_shenk(self) -> bool:
        atk_len = max(1, int(Config().char["atk_len_shenk"] / 2))
        shenk_pos_abs = self._pather.find_abs_node_pos(149, grab())
        if shenk_pos_abs is None:
            shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 0.9, shenk_pos_abs[1] * 0.9]
        for _ in range(atk_len):
            self._right_attack(cast_pos_abs, 90)
            self._left_attack(cast_pos_abs, 90)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes((Location.A5_SHENK_SAFE_DIST, Location.A5_SHENK_END), self, timeout=1.4, force_tp=True)
        return True

    def kill_nihlathak(self, end_nodes: list[int]) -> bool:
        # Find nilhlatak position
        atk_len = max(1, int(Config().char["atk_len_nihlathak"] / 2))
        for i in range(atk_len):
            nihlathak_pos_abs = self._pather.find_abs_node_pos(end_nodes[-1], grab())
            if nihlathak_pos_abs is None:
                return False
            cast_pos_abs = np.array([nihlathak_pos_abs[0] * 0.9, nihlathak_pos_abs[1] * 0.9])
            self._left_attack(cast_pos_abs, 90)
            self._right_attack(cast_pos_abs, 90)
            # Do some tele "dancing" after each sequence
            if i < atk_len - 1:
                rot_deg = random.randint(-10, 10) if i % 2 == 0 else random.randint(170, 190)
                tele_pos_abs = unit_vector(rotate_vec(cast_pos_abs, rot_deg)) * 100
                pos_m = convert_abs_to_monitor(tele_pos_abs)
                self.pre_move()
                self.move(pos_m)
        # Move to items
        wait(self._cast_duration, self._cast_duration + 0.2)
        self._pather.traverse_nodes(end_nodes, self, timeout=0.8)
        return True


if __name__ == "__main__":
    import os
    import keyboard
    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from char import Trapsin
    pather = Pather()
    char = Trapsin(Config().trapsin, Config().char, pather)