"""
Support for Lutron Caseta lights.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/light.lutron_caseta/
"""
import asyncio
import logging
import math
import time

from homeassistant.components.light import (
    ATTR_BRIGHTNESS, SUPPORT_BRIGHTNESS, SUPPORT_TRANSITION, ATTR_TRANSITION, Light, DOMAIN)
from homeassistant.components.light.lutron import (
    to_hass_level, to_lutron_level)
from ..lutron_caseta import (
    LUTRON_CASETA_SMARTBRIDGE, LUTRON_CASETA_LIP_ENABLED, LutronCasetaDevice)

_LOGGER = logging.getLogger(__name__)

DEPENDENCIES = ['lutron_caseta']

def to_lutron_time(seconds):
    """
    Convert the given transition time to Lutron's format.
    SS.ss, SS, MM:SS, or HH:MM:SS
    Fractional seconds will be rounded down to the nearest quarter second,
    4 hours is the maximum
    """
    return time.strftime('%H:%M:%S', time.gmtime(seconds))


# pylint: disable=unused-argument
@asyncio.coroutine
def async_setup_platform(hass, config, async_add_devices, discovery_info=None):
    """Set up the Lutron Caseta lights."""
    devs = []
    bridge = hass.data[LUTRON_CASETA_SMARTBRIDGE]
    lip_enabled = hass.data[LUTRON_CASETA_LIP_ENABLED]
    light_devices = bridge.get_devices_by_domain(DOMAIN)
    for light_device in light_devices:
        dev = LutronCasetaLight(light_device, bridge, lip_enabled)
        devs.append(dev)

    async_add_devices(devs, True)


class LutronCasetaLight(LutronCasetaDevice, Light):
    """Representation of a Lutron Light, including dimmable."""

    @property
    def supported_features(self):
        """Flag supported features."""
        return (SUPPORT_BRIGHTNESS | SUPPORT_TRANSITION)

    @property
    def brightness(self):
        """Return the brightness of the light."""
        return to_hass_level(self._state["current_state"])

    @asyncio.coroutine
    def async_turn_on(self, **kwargs):
        """Turn the light on."""
        if ATTR_BRIGHTNESS in kwargs:
            brightness = kwargs[ATTR_BRIGHTNESS]
        else:
            brightness = 255

        """If a transition time was provided (AND the bridge supports LIP), fade the light on."""
        if ATTR_TRANSITION in kwargs and self._lip_enabled:
            transition = kwargs[ATTR_TRANSITION];
            self._smartbridge.fade(self._device_id,
                                   to_lutron_level(brightness),
                                   to_lutron_time(transition))
        else:
            self._smartbridge.set_value(self._device_id,
                                    to_lutron_level(brightness))

    @asyncio.coroutine
    def async_turn_off(self, **kwargs):
        """Turn the light off."""
        if ATTR_TRANSITION in kwargs and self._lip_enabled:
            """If a transition time was provided (AND the bridge supports LIP), fade the light off."""
            transition = kwargs[ATTR_TRANSITION];
            self._smartbridge.fade(self._device_id, 0,
                                   to_lutron_time(transition))
        else:
            self._smartbridge.set_value(self._device_id, 0)

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._state["current_state"] > 0

    @asyncio.coroutine
    def async_update(self):
        """Call when forcing a refresh of the device."""
        self._state = self._smartbridge.get_device_by_id(self._device_id)
        _LOGGER.debug(self._state)
