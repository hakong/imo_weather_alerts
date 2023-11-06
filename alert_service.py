# alert_service.py
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from shapely.geometry import Point, Polygon

_LOGGER = logging.getLogger(__name__)

async def async_setup_alert_service(hass: HomeAssistant):
    """Set up the alert service."""

    async def handle_check_user_in_alert_area(call: ServiceCall):
        """Handle the service call."""
        user_entity_id = call.data.get('user_entity_id')
        alert_entity_id = call.data.get('alert_entity_id', 'sensor.icelandic_met_office_alerts')

        # Fetch the state objects from entity registry using the entity_id
        user_state = hass.states.get(user_entity_id)
        alert_state = hass.states.get(alert_entity_id)

        if user_state is None:
            # Handle the error appropriately
            _LOGGER.error(f"Entity '{user_entity_id}' not found")
            return
        
        if alert_state is None:
            # Handle the error appropriately
            _LOGGER.error(f"Entity '{alert_entity_id}' not found")
            return
        
        user_location = Point(float(user_state.attributes.get('latitude')), 
                              float(user_state.attributes.get('longitude')))
        _LOGGER.debug(f"User location: {user_location}")

        alerts = alert_state.attributes.get('alerts')
        if not alerts:
            _LOGGER.error(f"No alerts found in attribute 'alerts' of entity '{alert_entity_id}'")
            return

        # Initialize a list to store the identifiers of alerts where the user is in the area
        user_in_alert_area_identifiers = []

        # Loop over each alert to check the polygons and collect the identifiers
        for alert in alerts:
            _LOGGER.debug(f"Inside for alert in alerts")
            polygon_coords = alert.get('polygon')
            _LOGGER.debug(f"alert polygon_coords: {polygon_coords}")
            if polygon_coords:
                # Convert the string of coordinates to a list of tuples
                polygon_list = [tuple(map(float, p.split(','))) for p in polygon_coords.split()]
                alert_polygon = Polygon(polygon_list)
                _LOGGER.debug(f"alert_polygon: {alert_polygon}")
                # Check if the user is in the alert area
                if alert_polygon.contains(user_location):
                    _LOGGER.debug(f"User is in alert area: {alert.get('identifier')} - {alert.get('areaDesc')}")
                    user_in_alert_area_identifiers.append(alert.get('identifier'))
                else:
                    _LOGGER.debug(f"NO: alert_polygon does not container user_location. User location: {user_location} - {alert.get('areaDesc')}")

        # Do something with the list of identifiers, like logging, calling another service, etc.
        _LOGGER.info(f"User '{user_entity_id}' is in the following alert areas: {user_in_alert_area_identifiers}")
        # For example, you could return this list to the caller or store it somewhere.
        # return user_in_alert_area_identifiers

    # Register our service with Home Assistant.
    hass.services.async_register(
        'imo_weather_alerts',
        'check_user_in_alert_area',
        handle_check_user_in_alert_area
    )
