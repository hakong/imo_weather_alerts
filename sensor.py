# sensor.py
import logging
import asyncio
from urllib.parse import quote
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from aiohttp import ClientTimeout
from yarl import URL
from datetime import timedelta

# Define a constant at the top of your file, representing the time between updates
SCAN_INTERVAL = timedelta(minutes=15)  # Example: update every 15 minutes
_LOGGER = logging.getLogger(__name__)

class IMOMetAlertsSensor(Entity):
    def __init__(self, session, preferred_language='en-US'):
        self._state = None
        self._attributes = {'alerts': []}
        self.preferred_language = preferred_language
        self.session = session
        self.list_url = "https://api.vedur.is/cap/v1/capbroker/active/category/Met/"
        # url for testing. will return 5 active alerts.
        #self.list_url = "https://api.vedur.is/cap/v1/capbroker/sent/from/2023/1/1/to/2023/1/5/category/All/"

    @property
    def name(self):
        return "Icelandic Met Office Alerts"

    @property
    def state(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return self._attributes

    def construct_alert_url(self, sender, identifier, sent):
        _LOGGER.debug("Inside construct_alert_url")
        # base_url defined with placeholders
        base_url = "https://api.vedur.is/cap/v1/capbroker/sender/{sender}/identifier/{identifier}/sent/{sent}/json/"
        
        # Encode parameters using the yarl library, which is a dependency of aiohttp
        encoded_sent = quote(sent)
        formatted_url = base_url.format(sender=sender, identifier=identifier, sent=encoded_sent)
        
        # Using yarl.URL to construct the full URL
        url = URL(formatted_url)
        return str(url)

    def parse_alerts(self, json_data):
        _LOGGER.debug("Inside parse_alerts. JSON Data:")
        _LOGGER.debug(json_data)
        alerts = []
        if 'alert' in json_data:
            for info in json_data['alert'].get('info', []):
                if info.get('language') == self.preferred_language:
                    alert_info = {
                        'areaDesc': info.get('area', {}).get('areaDesc', 'Unknown area'),
                        'polygon': info.get('area', {}).get('polygon', []),
                        'category': info.get('category', 'Unknown category'),
                        'certainty': info.get('certainty', 'Unknown certainty'),
                        'description': info.get('description', ''),
                        'event': info.get('event', 'Unknown event'),
                        'headline': info.get('headline', ''),
                        'onset': info.get('onset', ''),
                        'expires': info.get('expires', ''),
                        'severity': info.get('severity', 'Unknown severity'),
                        'urgency': info.get('urgency', 'Unknown urgency'),
                        'language': info.get('language', self.preferred_language),
                        'icon_uri': info.get('resource', {}).get('uri', ''),
                        'link': info.get('web', '')
                    }
                    # Only add to the list if the required fields are available
                    if 'area' in info and 'event' in info:
                        alerts.append(alert_info)
                    else:
                        _LOGGER.debug(f"Alert info missing 'area' or 'event': {info}")
        else:
            _LOGGER.debug("No 'alert' key in JSON data.")
        return alerts

    async def async_update(self):
        # Define a timeout for the operations
        timeout = ClientTimeout(total=10)  # Total timeout for the whole operation

        try:
            all_alert_details = []
            _LOGGER.debug("Fetching list of active alerts")
            async with self.session.get(self.list_url, timeout=timeout) as response_list_url:
                response_list_url.raise_for_status()
                response_content = await response_list_url.text()
                if not response_content:
                    _LOGGER.debug("The response body is empty. No alerts to fetch.")
                    alerts_list = []
                else:
                    alerts_list = await response_list_url.json()
            _LOGGER.debug("Entering for alert in alerts_list")
            for alert in alerts_list:
                _LOGGER.debug("Calling self.construct_alert_url")
                alert_url = self.construct_alert_url(alert['sender'], alert['identifier'], alert['sent'])
                _LOGGER.debug("Async fetch response_alert_url")
                async with self.session.get(alert_url) as response_alert_url:
                    response_alert_url.raise_for_status()
                    alert_data = await response_alert_url.json()
                parsed_alerts = self.parse_alerts(alert_data)
                all_alert_details.extend(parsed_alerts)
            self._state = len(all_alert_details)
            self._attributes['alerts'] = all_alert_details
            return

        except asyncio.TimeoutError:
            _LOGGER.error("Timeout while fetching alerts.")
            self._state = None
            self._attributes = {'alerts': []}
        except Exception as e:
            _LOGGER.error(f"Error fetching alerts: {e}")
            _LOGGER.error('Exception stack trace:', exc_info=True)
            self._state = None
            self._attributes = {'alerts': []}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    _LOGGER.debug("Setting up IMOMetAlertsSensor platform.")
    preferred_language = config.get('preferred_language', 'en-US')
    session = async_get_clientsession(hass)
    sensor = IMOMetAlertsSensor(session, preferred_language)
    async_add_entities([sensor], update_before_add=True)
