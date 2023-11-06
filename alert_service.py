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
            _LOGGER.debug(f"Entity '{user_entity_id}' not found")
            return
        
        if alert_state is None:
            # Handle the error appropriately
            _LOGGER.debug(f"Entity '{alert_entity_id}' not found")
            return
        
        # Assume that the user's state object has 'latitude' and 'longitude' attributes
        user_location = Point(float(user_state.attributes.get('latitude')), 
                              float(user_state.attributes.get('longitude')))
        _LOGGER.debug(f"User location: {user_location}")

        # Get the alerts from the sensor's state object
        alerts = alert_state.attributes.get('alerts')
        if not alerts:
            _LOGGER.debug(f"No alerts in alert_state.attributes '{alert_state}'")
            return

        # Loop over each alert to check the polygons
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
                    _LOGGER.debug(f"YES: alert_polygon contains user_location. User location: {user_location}")
                else:
                    _LOGGER.debug(f"NO: alert_polygon does not container user_location. User location: {user_location}")

    # Register our service with Home Assistant.
    hass.services.async_register(
        'imo_weather_alerts',  # The domain where your service will live
        'check_user_in_alert_area',  # The service name
        handle_check_user_in_alert_area  # The callback function that is called when the service is executed
    )

