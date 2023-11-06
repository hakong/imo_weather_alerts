import asyncio
from aiohttp import ClientSession
# If your IMOMetAlertsSensor class is in sensor.py, you'd import it like this:
from sensor import IMOMetAlertsSensor

async def main():
    # This will run the async code in an event loop
    async with ClientSession() as session:
        # Instantiate your sensor with the actual session
        sensor = IMOMetAlertsSensor(session)

        # Now you can call your async update method to fetch the data
        await sensor.async_update()

        # Output the fetched data
        print(f"State: {sensor.state}")
        print(f"Attributes: {sensor.extra_state_attributes}")

# Run the main function in the event loop
asyncio.run(main())
