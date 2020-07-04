"""Support for Rhondda Cynon Taf Bin Collection."""
from datetime import timedelta
import logging

import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import ATTR_ATTRIBUTION
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from .rctbc import Rctbc

_LOGGER = logging.getLogger(__name__)

ATTR_NUMBER = "House Number"
ATTR_POSTCODE = "Post Code"
ATTR_RECYCLING = "Weekly Recycling"
ATTR_WASTE = "Fortnightly Waste Bin"
ATTR_CALCOL = "Calendar Colour"
ATTR_WASTE_DATE = "Next Waste Bin Collection"
ATTR_NEXT_COLLECTION = "Next Collection"

CONF_NUMBER = "number"
CONF_POSTCODE = "postcode"

ICON = "mdi:delete-empty"

SCAN_INTERVAL = timedelta(hours=6)

ATTRIBUTION = "Data provided by Rhondda Cynon Taf Borough Council"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {vol.Required(CONF_NUMBER): cv.string, vol.Optional(CONF_POSTCODE): cv.string}
)


async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    """Add entities from a config_entry."""
    number = config_entry.data[CONF_NUMBER]
    postcode = config_entry.data[CONF_POSTCODE]

    data = RctbcBinCollectionData(number, postcode)
    async_add_entities([RctbcBinCollectionSensor(number, postcode, data)], True)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Rhondda Cynon Taf Bin Collection sensor."""
    number = config.get(CONF_NUMBER)
    postcode = config.get(CONF_POSTCODE)

    data = RctbcBinCollectionData(number, postcode)
    add_entities([RctbcBinCollectionSensor(number, postcode, data)], True)


class RctbcBinCollectionSensor(Entity):
    """Implementation of an RCTBC Bin Collection sensor."""

    def __init__(self, number, postcode, data):
        """Initialize the sensor."""
        self._number = number
        self._postcode = postcode
        self.data = data
        self._name = f"RCTBC Bin Collection {number} {postcode}"
        self._state = None
        self._bin_data = {}

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self._bin_data:
            return {
                ATTR_NUMBER: self._number,
                ATTR_POSTCODE: self._postcode,
                ATTR_RECYCLING: self._bin_data[ATTR_RECYCLING],
                ATTR_WASTE: self._bin_data[ATTR_WASTE],
                ATTR_CALCOL: self._bin_data[ATTR_CALCOL],
                ATTR_WASTE_DATE: self._bin_data[ATTR_WASTE_DATE],
                ATTR_NEXT_COLLECTION: self._bin_data[ATTR_NEXT_COLLECTION],
                ATTR_ATTRIBUTION: ATTRIBUTION,
            }

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return ICON

    def update(self):
        """Get the latest data and update the states."""
        self.data.update()
        self._bin_data = self.data.bin_data
        if self._bin_data:
            self._state = self._bin_data[ATTR_NEXT_COLLECTION]
        else:
            self._state = None


class RctbcBinCollectionData:
    """The Class for handling the data retrieval."""

    def __init__(self, number, postcode):
        """Initialize the data object."""
        self.number = number
        self.postcode = postcode
        self.bin_data = self._empty_bin_data()

    def update(self):
        """Get the latest data from RCTBC."""
        rctbc = Rctbc(self.number, self.postcode)
        rctbc.update()

        if rctbc.data["recycling"] != "Unknown":
            self.info = []
            self.bin_data = {
                ATTR_NUMBER: self.number,
                ATTR_POSTCODE: self.postcode,
                ATTR_RECYCLING: rctbc.data["recycling"],
                ATTR_WASTE: rctbc.data["waste"],
                ATTR_CALCOL: rctbc.data["calcol"],
                ATTR_WASTE_DATE: rctbc.data["wasteDate"],
                ATTR_NEXT_COLLECTION: rctbc.data["nextCollection"],
                ATTR_ATTRIBUTION: ATTRIBUTION,
            }

            if not self.info:
                self.info = self._empty_bin_data()
        else:
            self.info = self._empty_bin_data()
            _LOGGER.warning("Unable to retrieve bin collection data.")

    def _empty_bin_data(self):
        return {
            ATTR_NUMBER: self.number,
            ATTR_POSTCODE: self.postcode,
            ATTR_RECYCLING: "",
            ATTR_WASTE: "",
            ATTR_CALCOL: "",
            ATTR_WASTE_DATE: "",
            ATTR_NEXT_COLLECTION: "",
            ATTR_ATTRIBUTION: ATTRIBUTION,
        }
