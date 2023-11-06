# __init__.py
from .alert_service import async_setup_alert_service

async def async_setup(hass, config):
    """Set up the IMO Weather Alerts component."""
    # Do setup here (e.g., load configuration, initialize communication with API, etc.)

    # Set up alert service
    await async_setup_alert_service(hass)

    return True
