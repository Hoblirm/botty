from enum import Enum
from numpy import ndarray
import cv2
import json
import keyboard
import os
import time
import uuid

from char import IChar
from config import Config
from d2r_image import processing as d2r_image
from d2r_image.data_models import GroundItemList, GroundItem, EnhancedJSONEncoder
from inventory import personal
from item import consumables
from item.consumables import ITEM_CONSUMABLES_MAP
from logger import Logger
from bnip.actions import should_pickup
from bnip.NTIPAliasType import NTIPAliasType as NTIP_TYPES
from screen import grab, convert_abs_to_monitor
from ui_manager import ScreenObjects, is_visible
from utils.custom_mouse import mouse
from utils.misc import wait


class PickedUpResult(Enum):
    TeleportedTo   = 0
    PickedUp       = 1
    PickedUpFailed = 3
    InventoryFull  = 4
    GoldFull       = 5

class PickIt:
    def __init__(self):
        self._cached_pickit_items = {} # * Cache the result of whether or not we should pick up the item. this should save some time
        self._prev_item_pickup_attempt = None
        self._fail_pickup_count = 0
        self._picked_up_items = []
        self._picked_up_item = False
        self.timeout = 20

    @staticmethod
    def _log_data(items: GroundItemList, img: ndarray, counter: int, _uuid: str):
        if Config().general["pickit_screenshots"]:
            cv2.imwrite(f"log/screenshots/pickit/{_uuid }_{counter}.png", img)
            with open(f"log/screenshots/pickit/{_uuid }_{counter}.json", 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, sort_keys=False, cls=EnhancedJSONEncoder, indent=2)

    @staticmethod
    def _locate_items() -> tuple[GroundItemList, ndarray]:
        img = grab()
        start = time.time()
        items = d2r_image.get_ground_loot(img).items.copy()
        Logger.debug(f"Read {len(items)} ground items in {round(time.time() - start, 3)} seconds")
        items = sorted(items, key=lambda item: item.Distance)
        return items, img

    def _reset_state(self):
        """Reset the pickit state"""
        self._prev_item_pickup_attempt = GroundItem()
        self._fail_pickup_count = 0
        self._picked_up_items = []
        self._picked_up_item = False

    @staticmethod
    def _ignore_gold(item: GroundItem):
        if personal.get_inventory_gold_full() and str(item.BaseItem["DisplayName"]).lower() == "gold":
            # Logger.debug("Gold is full, skip gold")
            return True
        return False

    @staticmethod
    def _ignore_consumable(item: GroundItem):
        # ignore item if it's a consumable AND there's no need for that consumable
        need_exists = True
        if item.Name.lower() in ITEM_CONSUMABLES_MAP:
            need_exists = consumables.get_needs(item.Name.lower()) > 0
        return (not need_exists)
    
    @staticmethod
    def _decrement_need_if_consumable(item: GroundItem):
        if item.Name.lower() in ITEM_CONSUMABLES_MAP:
            consumables.increment_need(item.Name.lower(), -1)
            return True
        return False

    @staticmethod
    def _yoink_item(item: GroundItem, char: IChar) -> PickedUpResult:
        if not char.pick_up_item((item.CenterMonitor['x'], item.CenterMonitor['y']), item_name=item.Name, distance=item.Distance):
            wait(0.16, 0.16) #wait 4 frames for items to refresh
            items, img = PickIt._locate_items()
            tele_success = False
            for i in items:
                if item.Name == i.Name:
                    tele_success = True
                    Logger.info(f"Teled to pickup item {i.Name} and now at distance {i.Distance}")
                    char.pick_up_item((i.CenterMonitor['x'], i.CenterMonitor['y']), item_name=i.Name, distance=i.Distance, force_run=True)
                    break
            if not tele_success:
                Logger.warning(f"Failed to scan item {i.Name} after tele.")
        return PickedUpResult.PickedUp

    def _pick_up_item(self, char: IChar, item: GroundItem) -> PickedUpResult:
        pickup_failed = False
        # gold moves when you try to pick it and are overburdened
        if (item.ID == self._prev_item_pickup_attempt.ID) and item.BaseItem["DisplayName"] == "Gold":
            self._fail_pickup_count += 1
            if is_visible(ScreenObjects.Overburdened):
                personal.set_inventory_gold_full(True)
                return PickedUpResult.GoldFull
            pickup_failed = self._fail_pickup_count >= 1
        # other items don't move, so should have same location
        if (item.UID == self._prev_item_pickup_attempt.UID):
            self._fail_pickup_count += 1
            wait(0.25, 0.35)
            if is_visible(ScreenObjects.Overburdened):
                return PickedUpResult.InventoryFull
            elif self._fail_pickup_count >= 1:
                # * +1 because we failed at picking it up once already, we just can't detect the first failure (unless it is due to full inventory)
                if char.capabilities.can_teleport_natively or char.capabilities.can_teleport_with_charges:
                    Logger.warning(f"Failed to pick up '{item.Name}' {self._fail_pickup_count + 1} times in a row, trying to teleport")
                    return self._yoink_item(item, char)
                pickup_failed = True

        if pickup_failed:
            Logger.warning(f"Failed to pick up '{item.Name}' {self._fail_pickup_count + 1} times in a row, moving on to the next item.")
            return PickedUpResult.PickedUpFailed

        self._prev_item_pickup_attempt = item
        return self._yoink_item(item, char)

    def pick_up_items(self, char: IChar) -> bool:
        """
            To be called everytime the bot wants to pick up items
            Pick up items that with a specified char
            :param char: The character used to pick up the item
            TODO :return: return a list of the items that were picked up
        """
        self._reset_state()
        keyboard.send(Config().char["show_items"])
        wait(0.16, 0.16) #wait 4 frames for items to refresh
        char._stationary = True #Character should start out stationary when pickup starts
        pickit_phase_start = time.time()

        items, img = self._locate_items()
        counter = 1
        _uuid = uuid.uuid4()
        self._log_data(items, img, counter, _uuid)
        item_count = 0
        while time.time() - pickit_phase_start < self.timeout:
            # If you previously up an item, get dropped item data again and reset the loop
            if self._picked_up_item:
                wait(0.16, 0.16) #wait 4 frames for items to refresh
                items, img = self._locate_items()
                counter += 1
                self._log_data(items, img, counter, _uuid)
                item_count=0
                if not items:
                    break
            elif item_count >= len(items):
                break
        
            # Otherwise continue to next item in the list
            item = items[item_count]

            pick_up_res=None
            pickup, raw_expression = (False, "")
            # Check if we already decided whether this item type should be picked
            if item.ID in self._cached_pickit_items:
                if self._cached_pickit_items[item.ID] and not (self._ignore_consumable(item) or self._ignore_gold(item)):
                    Logger.debug(f"Pick up expression: {raw_expression}")
                    Logger.info(f"Attempt to pick up {item.Name} at distance {item.Distance}")
                    pick_up_res = self._pick_up_item(char, item)
            else:
                item_dict = item.as_dict()
                # if the item shouldn't be ignored, check if it should be picked up
                if not (self._ignore_gold(item) or self._ignore_consumable(item)):
                    pickup, raw_expression = should_pickup(item_dict)
                    self._cached_pickit_items[item.ID] = pickup
                if pickup:
                    Logger.debug(f"Pick up expression: {raw_expression}")
                    Logger.info(f"Attempt to pick up {item.Name} at distance {item.Distance}")
                    pick_up_res = self._pick_up_item(char, item)
            match pick_up_res:
                case PickedUpResult.InventoryFull:
                    Logger.warning(f"Inventory is full, could not pick {item.Name}. Stop pickit") #TODO Create logic to handle inventory full
                    break
                case PickedUpResult.PickedUp:
                    self._decrement_need_if_consumable(item)
                    self._picked_up_items.append(item)
            self._picked_up_item = pick_up_res == PickedUpResult.PickedUp
            item_count+=1

        keyboard.send(Config().char["show_items"])
        return len(self._picked_up_items) >= 1


if __name__ == "__main__":
    import os
    from config import Config
    from char.sorceress import LightSorc
    from char.paladin import Hammerdin
    from pather import Pather
    import keyboard
    from logger import Logger
    from screen import start_detecting_window, stop_detecting_window

    keyboard.add_hotkey('f12', lambda: Logger.info('Force Exit (f12)') or stop_detecting_window() or os._exit(1))
    start_detecting_window()
    print("Move to d2r window and press f11")
    keyboard.wait("f11")

    pather = Pather()
    pickit = PickIt()
    char = Hammerdin(Config().hammerdin, pather, pickit)

    char.discover_capabilities()

    print(pickit.pick_up_items(char))
