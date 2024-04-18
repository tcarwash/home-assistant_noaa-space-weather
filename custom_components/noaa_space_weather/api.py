"""Sample API Client."""

import logging

import aiohttp
from swpclib import swpclib

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class NoaaSpaceWeatherApiClient:
    """Sample API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self.swpc = swpclib.Runner()

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        try:
            data = await self.swpc.get_standard()
        except Exception:
            data = {}

        return data

    async def async_get_first_frame(self, product) -> bytes:
        response_json = await self.swpc.get_data_method(product)
        first_frame_url = response_json[0].get("url")
        return await self.swpc.get_bytes_method(first_frame_url)

    async def async_load_animation(self, product) -> bytes:
        return await self.swpc.gen_gif(product)
