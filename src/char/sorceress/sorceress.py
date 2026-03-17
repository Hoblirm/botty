import keyboard
from typing import Callable
from utils.custom_mouse import mouse
from char import IChar
import template_finder
from pather import Pather
from screen import grab
from utils.misc import wait
import time
from pather import Pather
from config import Config
from ui_manager import ScreenObjects, is_visible
from screen import convert_abs_to_monitor

class Sorceress(IChar):
    def __init__(self, skill_hotkeys: dict, pather: Pather):
        super().__init__(skill_hotkeys)
        self._pather = pather
        self._action_frame = 7
        if Config().char["casting_frames"] == 11 or Config().char["casting_frames"] == 10:
            self._action_frame = 6
        elif Config().char["casting_frames"] == 9 or Config().char["casting_frames"] == 8:
            self._action_frame = 5
        elif Config().char["casting_frames"] == 7:
            self._action_frame = 4
        self._action_duration = self._action_frame * 0.04

    def pick_up_item(self, pos: tuple[float, float], item_name: str = None, distance: int = 0, force_run: bool = False):
        if (distance < 600) and self._skill_hotkeys["telekinesis"] and any(x in item_name for x in ['Potion', 'GOLD', 'Scroll of', 'Chest']):
            keyboard.send(self._skill_hotkeys["telekinesis"])
            mouse.move(pos[0], pos[1])
            wait(0.1, 0.1)
            mouse.click(button="right")
            wait(self._cast_duration,self._cast_duration)  
            self._stationary = True #We used telekinesis so we should be guaranteed stationary now
            return True
        else:
            return super().pick_up_item(pos, item_name, distance, force_run)

    def select_by_template(
        self,
        template_type:  str | list[str],
        success_func: Callable = None,
        timeout: float = 8,
        threshold: float = 0.68,
        telekinesis: bool = False
    ) -> bool:
        # In case telekinesis is False or hotkey is not set, just call the base implementation
        if not self._skill_hotkeys["telekinesis"] or not telekinesis:
            return super().select_by_template(template_type, success_func, timeout, threshold)
        if type(template_type) == list and "A5_STASH" in template_type:
            # sometimes waypoint is opened and stash not found because of that, check for that
            if is_visible(ScreenObjects.WaypointLabel):
                keyboard.send("esc")
        start = time.time()
        while timeout is None or (time.time() - start) < timeout:
            template_match = template_finder.search(template_type, grab(), threshold=threshold)
            if template_match.valid:
                keyboard.send(self._skill_hotkeys["telekinesis"])
                wait(0.1, 0.2)
                mouse.move(*template_match.center_monitor)
                wait(0.2, 0.3)
                mouse.click(button="right")
                # check the successfunction for 2 sec, if not found, try again
                check_success_start = time.time()
                while time.time() - check_success_start < 2:
                    if success_func is None or success_func():
                        return True
        # In case telekinesis fails, try again with the base implementation
        return super().select_by_template(template_type, success_func, timeout, threshold)

    def cast_buffs(self, casting_delay: float):
        if self._skill_hotkeys["energy_shield"]:
            keyboard.send(self._skill_hotkeys["energy_shield"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(casting_delay)
        if self._skill_hotkeys["thunder_storm"]:
            keyboard.send(self._skill_hotkeys["thunder_storm"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(casting_delay)
        if self._skill_hotkeys["frozen_armor"]:
            keyboard.send(self._skill_hotkeys["frozen_armor"])
            wait(0.1, 0.13)
            mouse.click(button="right")
            wait(casting_delay)

    def _cast_static(self, duration: float = 1.4):
        if self._skill_hotkeys["static_field"]:
            keyboard.send(self._skill_hotkeys["static_field"])

            #Static field can fail to cast if we right click on a wall.  We move mouse to 
            #center to prevent this.
            cast_pos_monitor = convert_abs_to_monitor((0, 0))
            mouse.move(*cast_pos_monitor)

            start = time.time()
            while time.time() - start < duration:
                mouse.click(button="right")
                wait(self._cast_duration)
