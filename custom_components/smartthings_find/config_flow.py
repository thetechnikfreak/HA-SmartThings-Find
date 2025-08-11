import logging
import voluptuous as vol
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    DOMAIN,
    CONF_USER_AUTH_TOKEN,
    CONF_AUTH_SERVER_URL,
    CONF_USER_ID,
    CONF_COUNTRY_CODE,
    CONF_DEVICE_MODEL,
    CONF_DEVICE_NAME,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): cv.string,
        vol.Optional(CONF_COUNTRY_CODE, default="us"): cv.string,
        vol.Optional(CONF_DEVICE_MODEL, default="Home Assistant"): cv.string,
        vol.Optional(CONF_DEVICE_NAME, default="Home Assistant Device"): cv.string,
    }
)

STEP_AUTH_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USER_AUTH_TOKEN): cv.string,
        vol.Required(CONF_AUTH_SERVER_URL): cv.string,
        vol.Required(CONF_USER_ID): cv.string,
    }
)


class SamsungFindConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Samsung Find."""

    VERSION = 1

    def __init__(self):
        """Initialize the config flow."""
        self._email: Optional[str] = None
        self._country_code: Optional[str] = None
        self._device_model: Optional[str] = None
        self._device_name: Optional[str] = None

    async def async_step_user(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            self._email = user_input[CONF_EMAIL]
            self._country_code = user_input[CONF_COUNTRY_CODE]
            self._device_model = user_input[CONF_DEVICE_MODEL]
            self._device_name = user_input[CONF_DEVICE_NAME]

            # Check if already configured
            await self.async_set_unique_id(self._email)
            self._abort_if_unique_id_configured()

            # Move to authentication step
            return await self.async_step_auth()

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )

    async def async_step_auth(self, user_input: Optional[Dict[str, Any]] = None) -> FlowResult:
        """Handle the authentication step."""
        errors: Dict[str, str] = {}

        if user_input is not None:
            # Validate the authentication data
            try:
                # Here you would normally validate the tokens
                # For now, we'll accept any input
                return self.async_create_entry(
                    title=f"Samsung Find ({self._email})",
                    data={
                        CONF_EMAIL: self._email,
                        CONF_COUNTRY_CODE: self._country_code,
                        CONF_DEVICE_MODEL: self._device_model,
                        CONF_DEVICE_NAME: self._device_name,
                        CONF_USER_AUTH_TOKEN: user_input[CONF_USER_AUTH_TOKEN],
                        CONF_AUTH_SERVER_URL: user_input[CONF_AUTH_SERVER_URL],
                        CONF_USER_ID: user_input[CONF_USER_ID],
                    },
                )
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="auth",
            data_schema=STEP_AUTH_DATA_SCHEMA,
            description_placeholders={
                "email": self._email,
                "login_url": "Please visit the Samsung Account login page to obtain your authentication tokens.",
            },
            errors=errors,
        )
