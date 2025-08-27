from faulthandler import is_enabled
from simulate.types import PeakList
import dearpygui.dearpygui as dpg
from graphics import WaterSettings

class Water:
    def __init__(self, frequency : float = 0.0, intensity : float = 1.0, hhw : float = 1.0, water_enable = False):
        self.frequency = frequency
        self.intensity = intensity
        self.hhw = hhw
        self.water_enable = water_enable
        self._set_peaklist(self.frequency, self.intensity)

    # ---------------------------------------------------------------------------- #
    #                              Getters and Setters                             #
    # ---------------------------------------------------------------------------- #

    # --------------------------------- frequency -------------------------------- #

    @property
    def frequency(self) -> float:
        if hasattr(self, '_frequency'):
            return self._frequency
        else:
            return 1.0
    
    @frequency.setter
    def frequency(self, value) -> None:
        try:
            from main import ContextStatus
            self._frequency : float = float(value)
            if ContextStatus.is_enabled() and dpg.does_item_exist(f"{WaterSettings.water_frequency_tag}_value"):
                dpg.set_value(f"{WaterSettings.water_frequency_tag}_value", float(value))
            self._set_peaklist(self._frequency, self.intensity)
        except TypeError:
            raise TypeError("Invalid value for water frequency! Must be string or real number")

    # --------------------------------- intensity -------------------------------- #

    @property
    def intensity(self) -> float:
        if hasattr(self, '_intensity'):
            return self._intensity
        else:
            return 1.0
    
    @intensity.setter
    def intensity(self, value) -> None:
        try:
            from main import ContextStatus
            self._intensity : float = float(value)
            if ContextStatus.is_enabled() and dpg.does_item_exist(f"{WaterSettings.water_intensity_tag}_value"):
                dpg.set_value(f"{WaterSettings.water_intensity_tag}_value", float(value))
            self._set_peaklist(self.frequency, self._intensity)
        except TypeError:
            raise TypeError("Invalid value for water intensity! Must be a string or a real number")
    
    # ------------------------------------ hhw ----------------------------------- #

    @property
    def hhw(self) -> float:
        if hasattr(self, '_hhw'):
            return self._hhw
        else:
            return 1.0
        
    @hhw.setter
    def hhw(self, value) -> None:
        try:
            from main import ContextStatus
            self._hhw : float = float(value)
            if ContextStatus.is_enabled() and dpg.does_item_exist(f"{WaterSettings.water_hhw_tag}_value"):
                dpg.set_value(f"{WaterSettings.water_hhw_tag}_value", float(value))
        except TypeError:
            raise TypeError("Invalid value for water half-height width! Must be a string or real number")
        
    # -------------------------------- is_enabled -------------------------------- #

    @property
    def water_enable(self) -> bool:
        return self._is_enabled
    
    @water_enable.setter
    def water_enable(self, value) -> None:
        from main import ContextStatus
        self._is_enabled : bool = bool(value)
        if ContextStatus.is_enabled() and dpg.does_item_exist(f"{WaterSettings.water_enable_tag}_value"):
            dpg.set_value(f"{WaterSettings.water_enable_tag}_value", bool(value))

    # --------------------------------- peaklist --------------------------------- #

    @property
    def peaklist(self) -> PeakList:
        return self._peaklist
    
    def _set_peaklist(self, frequency : float, intensity : float) -> None:
        self._peaklist : PeakList = [(frequency, intensity, -1)]
    
    # ---------------------------------------------------------------------------- #
    #                                Main Functions                                #
    # ---------------------------------------------------------------------------- #

    def enable(self) -> None:
        pass

    def disable(self) -> None:
        pass

    def toggle(self) -> None:
        if self.water_enable:
            self.disable()
        else:
            self.enable()