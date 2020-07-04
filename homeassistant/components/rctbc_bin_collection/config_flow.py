"""Config flow for RCTBC Bin Collection integration."""
import logging

import voluptuous as vol

from homeassistant import config_entries, core, exceptions

from .const import DOMAIN  # pylint:disable=unused-import
from .rctbc import Rctbc

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema({"number": str, "postcode": str})


async def validate_input(hass: core.HomeAssistant, data):
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """

    rctbc = Rctbc(data["number"], data["postcode"])
    await hass.async_add_executor_job(rctbc.update)

    if rctbc.data["recycling"] == "Unknown":
        raise InvalidAddress

    return {"title": f"RCTBC {data['number']} {data['postcode']}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RCTBC Bin Collection."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_UNKNOWN

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                user_input["postcode"] = user_input["postcode"].replace(" ", "").upper()
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidAddress:
                errors["base"] = "invalid_address"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class InvalidAddress(exceptions.HomeAssistantError):
    """Error to indicate there is invalid data."""
