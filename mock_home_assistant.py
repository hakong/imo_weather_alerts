# mock_home_assistant.py
import asyncio

# Mock Home Assistant core and entity objects
class MockHass:
    def __init__(self):
        self.states = {}

    async def add_states(self, entity_id, state):
        self.states[entity_id] = state

    async def get_state(self, entity_id):
        return self.states.get(entity_id)

# Import your service function
from alert_service import handle_check_user_in_alert_area

# Create a mock service call object
class MockServiceCall:
    def __init__(self, user_entity_id, alert_entity_id=None):
        self.data = {
            "user_entity_id": user_entity_id,
            "alert_entity_id": alert_entity_id
        }

# Define a test function
async def test_service():
    # Create a mock Home Assistant instance
    hass = MockHass()

    # Mock adding states
    await hass.add_states('sensor.icelandic_met_office_alerts', {
        'attributes': {
            'alerts': [
                # ... put your test alerts here ...
            ]
        }
    })
    await hass.add_states('device_tracker.some_user', {'state': 'home', 'attributes': {'latitude': 64.0, 'longitude': -21.0}})

    # Mock a service call
    service_call = MockServiceCall(user_entity_id='device_tracker.some_user')

    # Call your service with the mock objects
    await handle_check_user_in_alert_area(hass, service_call)

# Run the test function
asyncio.run(test_service())
