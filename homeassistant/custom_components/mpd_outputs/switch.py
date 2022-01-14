from __future__ import annotations
from http import client
from distutils.util import strtobool

import logging

import voluptuous as vol
import mpd
from mpd import MPDClient

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DOMAIN = "mpd_outputs"

_LOGGER = logging.getLogger(__name__)

DEFAULT_PORT = 6600

IGNORED_SWITCH_WARN = "Switch is already in the desired state. Ignoring."

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Read in all of our configuration, and initialize."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)

    hass.data.setdefault(DOMAIN, {})
    server_id = str.format("{0}:{1}", host, port)

    if server_id in hass.data[DOMAIN]:
        client = hass.data[DOMAIN][server_id]
    else:
        client = MPDClient()
        hass.data[DOMAIN][server_id] = client
    client.connect(host,port)
    for output in client.outputs():
        add_entities([MpdOutputSwitch(client, host, port, **output)], True)


class MpdOutputSwitch(SwitchEntity):

    def __init__(self, client, host, port, outputname, outputid, outputenabled, **kvargs):
        self._module_idx = outputid
        self._name = outputname
        self._client = client
        self._host = host
        self._port = port
        self._enabled = bool(strtobool(outputenabled))

    @property
    def available(self):
        return True

    @property
    def name(self):
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self):
        """Return true if device is on."""
        return self._enabled

    def turn_on(self, **kwargs):
        """Turn the device on."""
        if not self._enabled:
            self._client.enableoutput(self._module_idx)
        else:
            _LOGGER.warning(IGNORED_SWITCH_WARN)

    def turn_off(self, **kwargs):
        """Turn the device off."""
        if self._enabled:
            self._client.disableoutput(self._module_idx)
        else:
            _LOGGER.warning(IGNORED_SWITCH_WARN)

    def update(self):
        """Refresh state in case an alternate process modified this data."""
        try:
            for output in self._client.outputs():
                if output["outputname"] == self._name:
                    self._enabled = bool(strtobool(output["outputenabled"]))
        except mpd.base.ConnectionError:
            if self._module_idx == "1":
                self._client.connect(self._host, self._port)

