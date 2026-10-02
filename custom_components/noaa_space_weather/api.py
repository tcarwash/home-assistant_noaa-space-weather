"""API client helpers for fetching NOAA SWPC images/animations.

Adds support for animation sources that are either:
- JSON arrays of frame URLs (via swpclib or manual JSON handling)
- Single-image endpoints (PNG/JPG), returned as-is

Also includes a tiny in-memory cache and a prefetch utility so animations
can be warmed in the background without blocking config entry setup.
"""

import asyncio
import json
import logging
import time
from io import BytesIO
from urllib.parse import urlsplit

import aiohttp
from swpclib import swpclib

_LOGGER: logging.Logger = logging.getLogger(__package__)


class NoaaSpaceWeatherApiClient:
    """Sample API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self.swpc = swpclib.Runner()
        # Simple in-memory cache for built animations keyed by product URL/path
        self._animation_cache = {}

    # -------------------- URL helpers --------------------
    def _resolve_url(self, product: str) -> str:
        """Resolve product into absolute SWPC URL when path-like."""
        if not product:
            return ""
        if product.startswith("http://") or product.startswith("https://"):
            return product
        # Default SWPC host for leading slash paths
        if product.startswith("/"):
            return f"https://services.swpc.noaa.gov{product}"  # noqa: E231
        # Fallback: assume already a path usable by swpclib
        return product

    def _is_json_index(self, product: str) -> bool:
        p = urlsplit(product).path.lower()
        return p.endswith(".json")

    def _is_single_image(self, product: str) -> bool:
        p = urlsplit(product).path.lower()
        return p.endswith(".png") or p.endswith(".jpg") or p.endswith(".jpeg")

    # -------------------- HTTP helpers --------------------
    async def _fetch_text(self, url: str) -> str:
        async with self._session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()

    async def _fetch_bytes(self, url: str) -> bytes:
        async with self._session.get(url) as resp:
            resp.raise_for_status()
            return await resp.read()

    # (No HTML directory parsing; JSON and single-image only)

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        try:
            data = await self.swpc.get_standard()
        except Exception:
            data = {}

        # Ensure dict type
        if not isinstance(data, dict):
            return {}
        return data

    async def async_get_first_frame(self, product) -> bytes:
        """Return bytes for an initial frame for quick display.

        Supports JSON frame lists or single image URLs.
        """
        # Single-image endpoint
        if self._is_single_image(product):
            url = self._resolve_url(product)
            _LOGGER.debug("first_frame: fetching single image %s", url)
            return await self._fetch_bytes(url)

        # Resolve JSON frame URLs through the shared Home Assistant session so
        # relative and absolute NOAA URLs behave the same way.
        if self._is_json_index(product):
            try:
                response_json = json.loads(
                    await self._fetch_text(self._resolve_url(product))
                )
                first_frame_url = next(
                    frame.get("url")
                    for frame in response_json
                    if isinstance(frame, dict) and frame.get("url")
                )
                return await self._fetch_bytes(self._resolve_url(first_frame_url))
            except Exception as err:
                _LOGGER.debug("first_frame: JSON index path failed: %s", err)

        return b""

    async def async_load_animation(
        self, product, *, bypass_cache: bool = False
    ) -> bytes:
        """Return bytes for an animated GIF or a single image if only one frame exists.

        bypass_cache: when True, do not short-circuit on the in-memory cache. We'll
        still update the cache with any freshly built data.
        """
        # Serve from cache if available (unless bypassing)
        cached = self.get_cached_animation(product)
        if cached and not bypass_cache:
            return cached

        url = self._resolve_url(product)
        # Single image → just return it
        if self._is_single_image(url):
            data = await self._fetch_bytes(url)
            if data:
                self.set_cached_animation(product, data)
            return data

        # JSON indexes are built through the shared session below. swpclib
        # creates its own sessions and downloads frames sequentially, which
        # bypasses Home Assistant's connection settings and can stall refreshes.
        if self._is_json_index(product):
            try:
                url_json = self._resolve_url(product)
                # Cache buster to avoid upstream/CDN stale content
                ts = int(time.time())
                url_json_busted = f"{url_json}{'&' if '?' in url_json else '?'}_ts={ts}"
                json_text = await self._fetch_text(url_json_busted)
                response_json = json.loads(json_text)
                frame_urls = [
                    f.get("url")
                    for f in response_json
                    if isinstance(f, dict) and f.get("url")
                ]
                max_frames = 50
                if len(frame_urls) > max_frames:
                    frame_urls = frame_urls[-max_frames:]
                _LOGGER.debug(
                    "%s frames in %s (cap=%s)", len(frame_urls), product, max_frames
                )

                async def fetch_frame(frame_url: str) -> bytes | None:
                    try:
                        u_abs = self._resolve_url(frame_url)
                        u_abs = f"{u_abs}{'&' if '?' in u_abs else '?'}_ts={ts}"
                        return await self._fetch_bytes(u_abs)
                    except Exception as err:
                        _LOGGER.debug(
                            "Unable to fetch animation frame %s: %s", frame_url, err
                        )
                        return None

                # Keep frame order while fetching concurrently; NOAA indexes can
                # contain dozens of frames and serial downloads delay animation.
                semaphore = asyncio.Semaphore(5)

                async def fetch_limited(frame_url: str) -> bytes | None:
                    async with semaphore:
                        return await fetch_frame(frame_url)

                results = await asyncio.gather(*(fetch_limited(u) for u in frame_urls))
                images = [image for image in results if image]

                if len(images) <= 1:
                    single = images[0] if images else b""
                    if single:
                        self.set_cached_animation(product, single)
                    return single

                try:
                    from PIL import Image  # type: ignore
                except Exception:
                    data = images[-1] if images else b""
                    if data:
                        self.set_cached_animation(product, data)
                    return data

                pil_frames = []
                for b in images:
                    try:
                        frame = Image.open(BytesIO(b)).convert("RGB")
                        frame.thumbnail((768, 768), Image.Resampling.LANCZOS)
                        pil_frames.append(frame)
                    except Exception:
                        pass
                if not pil_frames:
                    data = images[-1] if images else b""
                    if data:
                        self.set_cached_animation(product, data)
                    return data

                # A shared palette keeps the GIF compact and avoids color
                # shifts between frames caused by independent frame palettes.
                sample_width = 32
                palette_samples = Image.new(
                    "RGB", (sample_width * len(pil_frames), sample_width)
                )
                for index, frame in enumerate(pil_frames):
                    sample = frame.copy()
                    sample.thumbnail((sample_width, sample_width))
                    palette_samples.paste(sample, (index * sample_width, 0))
                palette = palette_samples.quantize(colors=256)
                gif_frames = [
                    frame.quantize(palette=palette, dither=Image.Dither.NONE)
                    for frame in pil_frames
                ]

                bio = BytesIO()
                gif_frames[0].save(
                    bio,
                    format="GIF",
                    save_all=True,
                    append_images=gif_frames[1:],
                    duration=150,
                    loop=0,
                    disposal=2,
                    optimize=True,
                )
                data = bio.getvalue()
                if data:
                    self.set_cached_animation(product, data)
                return data
            except Exception as err:
                _LOGGER.debug(
                    "manual JSON animation build failed for %s: %s", product, err
                )
                return b""

        # Non-JSON or last resort — rely on library
        try:
            data = await self.swpc.gen_gif(product)
            if data:
                self.set_cached_animation(product, data)
            return data
        except Exception:
            # Return first frame so something shows up
            data = await self.async_get_first_frame(product)
            if data:
                self.set_cached_animation(product, data)
            return data

    # -------------------- Cache & prefetch helpers --------------------
    def get_cached_animation(self, product: str):
        return self._animation_cache.get(product) or self._animation_cache.get(
            self._resolve_url(product)
        )

    def set_cached_animation(self, product: str, data: bytes) -> None:
        try:
            if not data:
                return
            self._animation_cache[product] = data
            self._animation_cache[self._resolve_url(product)] = data
        except Exception:
            pass

    async def async_prefetch_animations(
        self,
        products: list[str],
        *,
        concurrency: int = 3,
        per_item_timeout: float = 60.0,
    ) -> None:
        if not products:
            return

        sem = asyncio.Semaphore(max(1, concurrency))

        async def _prefetch_one(prod: str):
            if self.get_cached_animation(prod):
                return
            async with sem:
                try:
                    data = await asyncio.wait_for(
                        self.async_load_animation(prod), timeout=per_item_timeout
                    )
                    if data:
                        self.set_cached_animation(prod, data)
                except Exception:
                    pass

        await asyncio.gather(*(_prefetch_one(p) for p in products))
