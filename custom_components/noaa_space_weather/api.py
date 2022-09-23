"""Sample API Client."""
import logging
from swpclib import swpclib

import aiohttp

TIMEOUT = 10


_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class NoaaSpaceWeatherApiClient:
    """Sample API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self.swpc = swpclib.Runner()

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        return await self.swpc.get_standard()
