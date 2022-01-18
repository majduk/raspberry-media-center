from __future__ import annotations
from cgitb import handler
from cmath import e
from importlib import resources

import logging

import http.client
import sys
from logging import handlers
from typing import OrderedDict
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_PORT, CONF_RESOURCES
from homeassistant.core import HomeAssistant
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

DOMAIN = "http_switch"

_LOGGER = logging.getLogger(__name__)


DEFAULT_NAME = "httpswitch"
DEFAULT_PORT = 8080
DEFAULT_RESOURCES={}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Required(CONF_RESOURCES, default=DEFAULT_RESOURCES): cv.match_all,
    }
)


def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Read in all of our configuration, and initialize the loopback switch."""
    name = config.get(CONF_NAME)
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    resources = config.get(CONF_RESOURCES)
    hass.data.setdefault(DOMAIN, {})

    for resource, handlers in resources.items():
        add_entities([HttpResource(host, port, resource, handlers)], True)


class HttpResource(SwitchEntity):

    def __init__(self, host, port, resource, handlers):
        self._name = resource
        self._handlers = {}
        self._enabled = False
        for h in ["turn_on", "turn_off", "update"]:
            if h in handlers:
                self._handlers[h] = RemoteHandler(h, host, port, resource, handlers[h])
            else:
                self._handlers[h] = DummyHandler(h)

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
        self._handlers[sys._getframe().f_code.co_name].call()
        self._enabled = True
        return True

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._handlers[sys._getframe().f_code.co_name].call()
        self._enabled = False
        return True

    def update(self):
        """Refresh state in case an alternate process modified this data."""
        try:
            self._handlers[sys._getframe().f_code.co_name].call()
        except:
            _LOGGER.warning("Exception when updating state")
            return False
        return True


class DummyHandler:

    def __init__(self, name):
        self._name = name

    def call(self):
        _LOGGER.debug("Dummy Handler %s called", self._name)
        return True


class RemoteHandler:

    def __init__(self, name, host, port, path, cfg):
        self._name = name
        self._host = host
        self._port = port
        self._path = path
        self._cfg = cfg

    def call(self):
        _LOGGER.debug("Remote Handler %s called: %s %s %s %s", self._name, self._host, self._port, self._path, self._cfg)
        connection = http.client.HTTPConnection("%s:%s" %(self._host, self._port))
        connection.request("GET", "/%s/%s" % (self._path, self._cfg))
        response = connection.getresponse()
        connection.close()
        _LOGGER.debug("Remote response %s %s", response.getcode(), response.read().decode())
        return response.getcode() == 200