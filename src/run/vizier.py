import cv2
import time
from char.i_char import IChar
from config import Config
from logger import Logger
from pather import Location, Pather
from item.pickit import PickIt
import template_finder
from town.town_manager import TownManager, A4
from utils.misc import wait
from utils.custom_mouse import mouse
from screen import convert_abs_to_monitor, grab
from ui_manager import detect_screen_object, ScreenObjects
from ui import skills, loading, waypoint
from inventory import belt, personal

class Vizier:

    name = "run_vizier"

    def __init__(
        self,
        pather: Pather,
        town_manager: TownManager,
        char: IChar,
        pickit: PickIt,
        runs: list[str]
    ):
        self._pather = pather
        self._town_manager = town_manager
        self._char = char
        self._pickit = pickit
        self._picked_up_items = False
        self.used_tps = 0
        self._curr_loc: bool | Location = Location.A4_TOWN_START
        self._runs = runs

    def approach(self, start_loc: Location) -> bool | Location:

        Logger.info("Run Vizer")
        Logger.debug("settings for trash =" + str(Config().char["kill_cs_trash"]))
        Logger.debug("settings for mob_detection =" + str(Config().char["cs_mob_detect"]))
        if not self._char.capabilities.can_teleport_natively:
            raise ValueError("Vizer requires teleport")
        if not self._town_manager.open_wp(start_loc):
            return False
        wait(0.4)
        waypoint.use_wp("River of Flame")
        return Location.A4_DIABLO_WP

    # OPEN SEALS
    def _sealdance(self, seal_opentemplates: list[str], seal_closedtemplates: list[str], seal_layout: str, seal_node: str) -> bool:
        i = 0
        while i < 8:
            Logger.debug(seal_layout + ": trying to open (try #" + str(i+1)+")")
            self._char.select_by_template(seal_closedtemplates, threshold=0.5, timeout=0.1, telekinesis=True)
            wait(i*0.5)
            found = template_finder.search_and_wait(seal_opentemplates, threshold=0.7, timeout=0.1).valid
            if found:
                Logger.info(seal_layout +": is open - "+'\033[92m'+" open"+'\033[0m')
                break
            else:
                Logger.debug(seal_layout +": is closed - "+'\033[91m'+" closed"+'\033[0m')
                pos_m = convert_abs_to_monitor((0, 0))
                mouse.move(*pos_m, randomize=[90, 160])
                wait(0.3)
                if i >= 1:
                    Logger.debug(seal_layout + ": failed " + str(i+2) + " times, trying to kill trash now")
                    Logger.debug("Sealdance: Kill trash at location: sealdance")
                    self._char.kill_cs_trash("sealdance")
                    wait(i*0.5)
                    if not self._pather.traverse_nodes(seal_node, self._char): return False
                else:
                    direction = 1 if i % 2 == 0 else -1
                    x_m, y_m = convert_abs_to_monitor([50 * direction, direction])
                    self._char.move((x_m, y_m), force_move=True)
                i += 1
        if Config().general["info_screenshots"] and not found: cv2.imwrite(f"./log/screenshots/info/info_failed_seal_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        return found


    # LOOP TO PENTAGRAM
    def _loop_pentagram(self, path) -> bool:
        found = False
        templates = ["DIA_NEW_PENT_TP", "DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2"]
        for _ in range(3):
            found = template_finder.search_and_wait(templates, threshold=0.83, timeout=0.3, suppress_debug=True).valid
            if not found: self._pather.traverse_nodes_fixed(path, self._char)
            else: break
        if not found:
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_failed_loop_pentagram_" + path + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            return False
        return True


    #CLEAR CS TRASH
    def _entrance_hall(self) -> bool:
        Logger.info("CS Trash: Starting to clear Trash")
        Logger.debug("CS Trash: clearing first hall 1/2 - location: entrance_hall_01")
        self._char.kill_cs_trash("entrance_hall_01")
        Logger.debug("CS Trash: clearing first hall 1/2 - location: entrance_hall_02")
        self._char.kill_cs_trash("entrance_hall_02")

        if not self._pather.traverse_nodes([605], self._char): return False
        templates = ["DIABLO_ENTRANCE_53", "DIABLO_ENTRANCE_51","DIABLO_ENTRANCE_50", "DIABLO_ENTRANCE_52", "DIABLO_ENTRANCE_54", "DIABLO_ENTRANCE_55"]
        if template_finder.search_and_wait(templates, threshold=0.8, timeout=0.1).valid:
            Logger.debug("CS Trash (A): Layout_check step 1/2: Layout A templates found")
            templates = ["DIABLO_ENTRANCE2_55", "DIABLO_ENTRANCE2_50", "DIABLO_ENTRANCE2_51", "DIABLO_ENTRANCE2_52","DIABLO_ENTRANCE2_53","DIABLO_ENTRANCE2_54","DIABLO_ENTRANCE2_15","DIABLO_ENTRANCE2_56"]
            if not template_finder.search_and_wait(templates, threshold=0.8, timeout=0.5).valid:
                Logger.debug("CS Trash (A): Layout_check step 2/2: Layout B templates NOT found - "+'\033[95m'+"all fine, proceeding with Layout A"+'\033[0m')
                entrance1_layout = "CS Trash (A):"
                #if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + entrance1_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                Logger.debug(entrance1_layout + " clearing second hall (1/3) location: entrance1_01")
                self._char.kill_cs_trash("entrance1_01")
                Logger.debug(entrance1_layout + " clearing second hall (2/3) location: entrance1_02")
                self._char.kill_cs_trash("entrance1_02")
                Logger.debug(entrance1_layout + " clearing second hall (3/3) location: entrance1_03")
                self._char.kill_cs_trash("entrance1_03")
                Logger.debug(entrance1_layout + " clearing third hall (1/1) location: entrance1_04")
                self._char.kill_cs_trash("entrance1_04")
                return True
            else:
                Logger.warning("CS Trash (A): Layout_check failed to determine the right Layout, "+'\033[91m'+"trying to loop to pentagram to save the run"+'\033[0m')
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_entrance_a_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return True

        else:
            Logger.debug("CS Trash (B): Layout_check step 1/2: Layout A templates NOT found")
            templates = ["DIABLO_ENTRANCE2_55", "DIABLO_ENTRANCE2_50", "DIABLO_ENTRANCE2_51", "DIABLO_ENTRANCE2_52","DIABLO_ENTRANCE2_53","DIABLO_ENTRANCE2_54","DIABLO_ENTRANCE2_15","DIABLO_ENTRANCE2_56"]
            if  template_finder.search_and_wait(templates, threshold=0.8, timeout=0.1).valid:
                Logger.debug("CS Trash (B): Layout_check step 2/2: Layout B templates found - "+'\033[96m'+"all fine, proceeding with Layout B"+'\033[0m')
                entrance2_layout = "CS Trash (B):"
                #if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + entrance2_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                Logger.debug(entrance2_layout + " clearing second hall (1/3) - location: entrance2_01")
                self._char.kill_cs_trash("entrance2_01")
                Logger.debug(entrance2_layout + " clearing second hall (2/3) - location: entrance2_02")
                self._char.kill_cs_trash("entrance2_02")
                Logger.debug(entrance2_layout + " clearing second hall (3/3) - location: entrance2_03")
                self._char.kill_cs_trash("entrance2_03")
                Logger.debug(entrance2_layout + " clearing third hall (1/1) - location: entrance2_04")
                self._char.kill_cs_trash("entrance2_04")
                return True
            else:
                Logger.warning("CS Trash (B): Layout_check failed to determine the right Layout, "+'\033[91m'+"trying to loop to pentagram to save the run"+'\033[0m')
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_entrance_b_failed_layoutcheck_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return True

    #GET FROM WP TO PENTAGRAM (clear_trash=0)
    def _river_of_flames(self) -> bool:
        if not self._pather.traverse_nodes([600], self._char): return False
        Logger.debug("ROF: Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_pentagram_1", self._char)
        self._pather.traverse_nodes_fixed("diablo_wp_pentagram_2", self._char)
        Logger.debug("ROF: Teleporting directly to PENTAGRAM")
        found = False
        templates = ["DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2"]
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = template_finder.search_and_wait(templates, threshold=0.8, timeout=0.1, suppress_debug=True).valid
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_pentagram_loop", self._char)
        if not found:
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_failed_pent_loop_no_trash_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            return False
        return True


    #GET FROM WP TO CS ENTRANCE (clear_trash=1)
    def _river_of_flames_trash(self) -> bool:
        if not self._pather.traverse_nodes([600], self._char): return False
        Logger.debug("ROF: Calibrated at WAYPOINT")
        self._pather.traverse_nodes_fixed("diablo_wp_entrance", self._char)
        Logger.debug("Kill trash at location: rof_01")
        self._char.kill_cs_trash("rof_01")
        Logger.debug("ROF: Teleporting to CS ENTRANCE")
        found = False
        templates = ["DIABLO_CS_ENTRANCE_0", "DIABLO_CS_ENTRANCE_2", "DIABLO_CS_ENTRANCE_3"]
        start_time = time.time()
        while not found and time.time() - start_time < 10:
            found = template_finder.search_and_wait(templates, threshold=0.8, timeout=0.1, suppress_debug=True).valid
            if not found:
                self._pather.traverse_nodes_fixed("diablo_wp_entrance_loop", self._char)
        if not found:
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_failed_cs_entrance_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            return False
        Logger.debug("Kill trash at location: rof_02")
        self._char.kill_cs_trash("rof_02")
        Logger.debug("CS Trash: Calibrated at CS ENTRANCE")
        if not self._entrance_hall(): return False
        Logger.debug("CS Trash: looping to PENTAGRAM")
        if not self._loop_pentagram("diablo_wp_pentagram_loop"): return False
        found = False
        templates = ["DIA_NEW_PENT_TP", "DIA_NEW_PENT_0", "DIA_NEW_PENT_1", "DIA_NEW_PENT_2"]
        start_time = time.time()
        while not found and time.time() - start_time < 15:
            found = template_finder.search_and_wait(templates, threshold=0.83, timeout=0.1, suppress_debug=True).valid
            if not found: self._pather.traverse_nodes_fixed("diablo_wp_pentagram_loop", self._char)
        if not found:
            if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_failed_loop_pentagram_diablo_wp_pentagram_loop_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
            return False
        return True


    #ARRIVE AT PENTAGRAM AFTER LOOP
    def _cs_pentagram(self) -> bool:
        if not self._pather.traverse_nodes([602], self._char, threshold=0.80): return False
        Logger.info("CS: Calibrated at PENTAGRAM")
        return True
    
    def _trash_seals(self) -> bool:
        #Assume we are already at the pentagram
        self._pather.traverse_nodes_fixed("dia_trash_a", self._char)
        Logger.debug("CS TRASH: A Pent to LC")
        self._char.kill_cs_trash("dia_trash_a")
        #if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_Trash_A_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        Logger.debug("CS TRASH: A looping to PENTAGRAM")
        if not self._loop_pentagram("dia_a1l_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.debug("CS TRASH: A calibrated at PENTAGRAM")

        self._pather.traverse_nodes_fixed("dia_trash_b", self._char)
        Logger.debug("CS TRASH: B Pent to LC")
        self._char.kill_cs_trash("dia_trash_b")
        #if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_Trash_B_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        Logger.debug("CS TRASH: B looping to PENTAGRAM")
        if not self._loop_pentagram("dia_b1s_home_loop"): return False
        if not self._pather.traverse_nodes([602], self._char): return False
        Logger.debug("CS TRASH: B calibrated at PENTAGRAM")


    #CHECK SEAL LAYOUT
    def _layoutcheck(self, sealname:str, boss:str, static_layoutcheck:str, trash_location:str , calibration_node:str, calibration_threshold:str, confirmation_node:str, templates_primary:list[str], templates_confirmation:list[str]):
        match sealname:
            case "A":
                seal_layout1:str = "A1-L"
                seal_layout2:str = "A2-Y"
                params_seal1 = seal_layout1, [614], [615], [611], "dia_a1l_home", "dia_a1l_home_loop", [602], ["DIA_A1L2_14_OPEN"], ["DIA_A1L2_14_CLOSED", "DIA_A1L2_14_CLOSED_DARK", "DIA_A1L2_14_MOUSEOVER"], ["DIA_A1L2_5_OPEN"], ["DIA_A1L2_5_CLOSED","DIA_A1L2_5_MOUSEOVER"]
                params_seal2 = seal_layout2, [625], [626], [622], "dia_a2y_home", "dia_a2y_home_loop", [602], ["DIA_A2Y4_29_OPEN"], ["DIA_A2Y4_29_CLOSED", "DIA_A2Y4_29_MOUSEOVER"], ["DIA_A2Y4_36_OPEN"], ["DIA_A2Y4_36_CLOSED", "DIA_A2Y4_36_MOUSEOVER"]
                threshold_primary=0.8
                threshold_confirmation=0.85
                threshold_confirmation2=0.8
                confirmation_node2=None
            case _:
                Logger.warning(sealname + ": something is wrong - cannot check layouts: Aborting run.")
                return False

        self._pather.traverse_nodes_fixed(static_layoutcheck, self._char)
        self._char.kill_cs_trash(trash_location)
        Logger.debug(f"{sealname}: Checking Layout for "f"{boss}")
        if not calibration_node == None:
            if not self._pather.traverse_nodes(calibration_node, self._char, threshold=calibration_threshold,): return False
        #if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_LC_" + sealname + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        #check1 using primary templates
        if not template_finder.search_and_wait(templates_primary, threshold =threshold_primary, timeout=0.1).valid:
            Logger.debug(f"{seal_layout1}: Layout_check step 1/2 - templates NOT found for "f"{seal_layout2}")
            if not template_finder.search_and_wait(templates_confirmation, threshold=threshold_confirmation, timeout=0.1).valid:
                Logger.warning(f"{seal_layout2}: Layout_check failure - could not determine the seal Layout at" f"{sealname} ("f"{boss}) - "+'\033[91m'+"aborting run"+'\033[0m')
                if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout1 + "_LC_fail" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
                return False
            else:
                Logger.info(f"{seal_layout1}: Layout_check step 2/2 - templates found for "f"{seal_layout1} - "+'\033[93m'+"all fine, proceeding with "f"{seal_layout1}"+'\033[0m')
                if not self._seal(*params_seal1): return False
        else:
            Logger.debug(f"{seal_layout2}: Layout_check step 1/2 - templates found for {seal_layout1}")
            if not self._seal(*params_seal2): return False
        return True


#CLEAR SEAL
    def _seal(self, seal_layout:str, node_seal1:str, node_seal2:str, node_calibrate_to_pent:str, static_pent:str, static_loop_pent:str, node_calibrate_at_pent:str, seal1_opentemplates:list[str], seal1_closedtemplates:list[str], seal2_opentemplates:list[str], seal2_closedtemplates:list[str], ) -> bool:
        #if Config().general["info_screenshots"]: cv2.imwrite(f"./log/screenshots/info/info_" + seal_layout + "_" + time.strftime("%Y%m%d_%H%M%S") + ".png", grab())
        Logger.info(seal_layout +": Starting to clear Seal")
        ### CLEAR TRASH ###
        ##Logger.debug(seal_layout + "_01: Kill trash")
        ##self._char.kill_cs_trash(seal_layout + "_01")
        ### APPROACH SEAL ###
        if not node_seal1 == None:
            Logger.debug(seal_layout + "_seal1: Kill trash")
            if not self._pather.traverse_nodes(node_seal1, self._char, timeout = 2): 
                self._char.kill_cs_trash(seal_layout + "_seal1")
                if not self._pather.traverse_nodes(node_seal1, self._char): return False
            if not self._sealdance(seal1_opentemplates, seal1_closedtemplates, seal_layout + ": Seal1", node_seal1): return False
        else:
            Logger.debug(seal_layout + ": No Fake Seal for this layout, skipping")
        Logger.debug(seal_layout + "_seal2: Kill trash")
        self._char.kill_cs_trash(seal_layout + "_seal2")
        if not self._pather.traverse_nodes(node_seal2, self._char): return False
        if not self._sealdance(seal2_opentemplates, seal2_closedtemplates, seal_layout + ": Seal2", node_seal2): return False
        ### KILL BOSS ###
        match seal_layout:
            case "A1-L" | "A2-Y":
                Logger.debug(seal_layout + ": Kill Boss A (Vizier)")
                self._char.kill_vizier(seal_layout)
            case _:
                Logger.warning(seal_layout + ": Error - no Boss known here - aborting run")
                return False
        return True


    def battle(self, do_pre_buff: bool) -> bool | tuple[Location, bool]:
        self._picked_up_items = False
        self.used_tps = 0
        if do_pre_buff: self._char.pre_buff()

        #Skip to pentagram ignoring trash at enterance until clearing enterance can be made more reliable
        if not self._river_of_flames(): return False

        #Should be near pentagram, calibrate with pentagram node
        if not self._cs_pentagram(): return False

        #Clear trash around pentagram
        if Config().char["kill_cs_trash"]: self._trash_seals()

        # After clearing trash around pentagram, attack and recalibrate at pentagram node and finally rebuff.
        if Config().char["kill_cs_trash"]: self._char.kill_cs_trash("pent_before_a")
        if not self._pather.traverse_nodes([602], self._char): return False
        if Config().char["kill_cs_trash"] and do_pre_buff: self._char.pre_buff()

        #Perform layout check and clear Vizier seal
        if not self._layoutcheck("A", "Vizier", "dia_a_layout", "layoutcheck_a", [610620], 0.81 , None, ["DIA_A2Y_LAYOUTCHECK0", "DIA_A2Y_LAYOUTCHECK1", "DIA_A2Y_LAYOUTCHECK2", "DIA_A2Y_LAYOUTCHECK4", "DIA_A2Y_LAYOUTCHECK5", "DIA_A2Y_LAYOUTCHECK6"], ["DIA_A1L_LAYOUTCHECK0", "DIA_A1L_LAYOUTCHECK4", "DIA_A1L_LAYOUTCHECK4LEFT", "DIA_A1L_LAYOUTCHECK1", "DIA_A1L_LAYOUTCHECK2", "DIA_A1L_LAYOUTCHECK3","DIA_A1L_LAYOUTCHECK4RIGHT","DIA_A1L_LAYOUTCHECK5"]): return False

        return (Location.A4_DIABLO_A_LAYOUTCHECK, self._picked_up_items)

if __name__ == "__main__":
    import keyboard
    from game_stats import GameStats
    import os
    keyboard.add_hotkey('f12', lambda: os._exit(1))
    keyboard.wait("f11")
    from config import Config
    from bot import Bot
    game_stats = GameStats()
    bot = Bot(game_stats)
