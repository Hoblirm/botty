import random
import keyboard
import time
import numpy as np

from health_manager import get_panel_check_paused, set_panel_check_paused
from inventory.personal import inspect_items
from screen import convert_abs_to_monitor, convert_screen_to_abs, grab, convert_abs_to_screen
from utils.custom_mouse import mouse
from char.amazon import Amazon
from logger import Logger
from config import Config
from utils.misc import wait
from pather import Location
from target_detect import get_visible_targets, TargetInfo, log_targets

class Javazon(Amazon):
    def __init__(self, *args, **kwargs):
        Logger.info("Setting up Javazon")
        super().__init__(*args, **kwargs)

    def _cast_lightning_fury(self, cast_pos_abs: tuple[float, float], spray: float = 10, duration: float = 0.3):
        if not self._skill_hotkeys["lightning_fury"]:
            raise ValueError("You did not set a hotkey for lightning_fury!")
        keyboard.send(self._skill_hotkeys["lightning_fury"])
        
        #Get mouse in initial target logcation
        x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
        y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
        cast_pos_monitor = convert_abs_to_monitor((x, y))
        mouse.move(*cast_pos_monitor)
        
        #We just hold down right mouse button to ensure we get full attack speed.
        mouse.press(button="right")
        now = start = time.time()
        while (now - start) < duration:
            x = cast_pos_abs[0] + (random.random() * 2 * spray - spray)
            y = cast_pos_abs[1] + (random.random() * 2 * spray - spray)
            cast_pos_monitor = convert_abs_to_monitor((x, y))
            mouse.move(*cast_pos_monitor)
            wait(0.03, 0.36)
            now = time.time()
        mouse.release(button="right")

        #wait 14 frames (14/25) which is slowest attack speed to ensure amazon is ready
        wait(0.56)

    def kill_pindle(self) -> bool:
        atk_len_dur = float(Config().char["atk_len_pindle"])
        pindle_pos_abs = convert_screen_to_abs(Config().path["pindle_end"][0])

        cast_pos_abs = [pindle_pos_abs[0] * 0.80, pindle_pos_abs[1] * 0.80]
        self._cast_valkyrie(cast_pos_abs=cast_pos_abs)
        self._cast_lightning_fury(cast_pos_abs=cast_pos_abs, duration=atk_len_dur)

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("pindle_end", self)
        else:
            #Walk just close enough to pindle's position to see items.  That way we leave sooner if there is nothing to grab
            x_m, y_m = convert_abs_to_monitor([pindle_pos_abs[0] * 0.65, pindle_pos_abs[1] * 0.65])
            self.move((x_m, y_m), force_move=True)
        return True

    def kill_eldritch(self) -> bool:
        eldritch_pos_abs = convert_screen_to_abs(Config().path["eldritch_end"][0])
        cast_pos_abs = [eldritch_pos_abs[0] * 1.5, eldritch_pos_abs[1] * 1.5]

        self._cast_valkyrie(cast_pos_abs=cast_pos_abs)
        self._cast_lightning_fury(cast_pos_abs=cast_pos_abs, duration=Config().char["atk_len_eldritch"])
        
        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("eldritch_end", self)
        else:
            x_m, y_m = convert_abs_to_monitor([eldritch_pos_abs[0] * 1.0, eldritch_pos_abs[1] * 1.0])
            self.move((x_m, y_m), force_move=True)
        return True

    def kill_shenk(self) -> bool:
        shenk_pos_abs = convert_screen_to_abs(Config().path["shenk_end"][0])
        cast_pos_abs = [shenk_pos_abs[0] * 1.5, shenk_pos_abs[1] * 1.5]

        self._cast_valkyrie(cast_pos_abs=cast_pos_abs)
        self._cast_lightning_fury(cast_pos_abs=cast_pos_abs, duration=Config().char["atk_len_shenk"])

        if self.capabilities.can_teleport_natively:
            self._pather.traverse_nodes_fixed("shenk_end", self)
        else:
            x_m, y_m = convert_abs_to_monitor([shenk_pos_abs[0] * 1.0, shenk_pos_abs[1] * 1.0])
            self.move((x_m, y_m), force_move=True)
            
        return True
    

   