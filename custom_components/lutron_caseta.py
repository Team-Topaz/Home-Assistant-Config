"""
Component for interacting with a Lutron Caseta system.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/lutron_caseta/
"""
import asyncio
import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import discovery
from homeassistant.helpers.entity import Entity

REQUIREMENTS = ['https://github.com/chelzwa/pylutron-caseta/archive/0.0.16.zip#pylutron-caseta==0.0.16']

_LOGGER = logging.getLogger(__name__)

LUTRON_CASETA_SMARTBRIDGE = 'lutron_smartbridge'
LUTRON_CASETA_LIP_ENABLED = 'lutron_lip_enabled'

DOMAIN = 'lutron_caseta'

CONF_KEYFILE = 'keyfile'
CONF_CERTFILE = 'certfile'
CONF_CA_CERTS = 'ca_certs'
CONF_LIP_ENABLED = 'lip_enabled'

DEFAULT_ENABLE_LIP = False
DEFAULT_LIP_PORT = 23
DEFAULT_LIP_USERNAME = 'lutron'
DEFAULT_LIP_PASSWORD = 'integration'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_KEYFILE): cv.string,
        vol.Required(CONF_CERTFILE): cv.string,
        vol.Required(CONF_CA_CERTS): cv.string,
        vol.Optional(CONF_LIP_ENABLED,
                default=DEFAULT_ENABLE_LIP): cv.boolean,
        vol.Optional(CONF_PORT,
                default=DEFAULT_LIP_PORT): cv.string,
        vol.Optional(CONF_USERNAME,
                default=DEFAULT_LIP_USERNAME): cv.string,
        vol.Optional(CONF_PASSWORD,
                default=DEFAULT_LIP_PASSWORD): cv.string
    })
}, extra=vol.ALLOW_EXTRA)

LUTRON_CASETA_COMPONENTS = [
    'light', 'switch', 'cover', 'scene'
]


@asyncio.coroutine
def async_setup(hass, base_config):
    """Set up the Lutron component."""
    from pylutron_caseta.smartbridge import Smartbridge

    config = base_config.get(DOMAIN)
    keyfile = hass.config.path(config[CONF_KEYFILE])
    certfile = hass.config.path(config[CONF_CERTFILE])
    ca_certs = hass.config.path(config[CONF_CA_CERTS])

    bridge = Smartbridge.create_tls(hostname=config[CONF_HOST],
                                    keyfile=keyfile,
                                    certfile=certfile,
                                    ca_certs=ca_certs)

    hass.data[LUTRON_CASETA_SMARTBRIDGE] = bridge
    yield from bridge.connect()
    if not hass.data[LUTRON_CASETA_SMARTBRIDGE].is_connected():
        _LOGGER.error("Unable to connect to Lutron smartbridge at %s",
                      config[CONF_HOST])
        return False

    _LOGGER.info("Connected to Lutron smartbridge at %s", config[CONF_HOST])

    hass.data[LUTRON_CASETA_LIP_ENABLED] = config[CONF_LIP_ENABLED]
    if config[CONF_LIP_ENABLED]:
        bridge.connect_lip(config[CONF_HOST],
                    config[CONF_PORT],
                    config[CONF_USERNAME],
                    config[CONF_PASSWORD])

    for component in LUTRON_CASETA_COMPONENTS:
        hass.async_add_job(discovery.async_load_platform(hass, component,
                                                         DOMAIN, {}, config))

    return True


class LutronCasetaDevice(Entity):
    """Common base class for all Lutron Caseta devices."""

    def __init__(self, device, bridge, lip_enabled):
        """Set up the base class.

        [:param]device the device metadata
        [:param]bridge the smartbridge object
        """
        self._device_id = device["device_id"]
        self._device_type = device["type"]
        self._device_name = device["name"]
        self._device_zone = device["zone"]
        self._state = None
        self._smartbridge = bridge
        self._lip_enabled = lip_enabled

    @asyncio.coroutine
    def async_added_to_hass(self):
        """Register callbacks."""
        self._smartbridge.add_subscriber(self._device_id,
                                         self.async_schedule_update_ha_state)

    @property
    def name(self):
        """Return the name of the device."""
        return self._device_name

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attr = {
            'Device ID': self._device_id,
            'Zone ID': self._device_zone,
        }
        return attr

    @property
    def should_poll(self):
        """No polling needed."""
        return False
