"""API client helpers for fetching NOAA SWPC images/animations.

Adds support for animation sources that are either:
- JSON arrays of frame URLs (existing behavior via swpclib)
- HTML directory index pages listing frames (new)
- Single-image endpoints (PNG/JPG), returned as-is
"""

import logging
import re
from io import BytesIO

import aiohttp
from swpclib import swpclib

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {"Content-type": "application/json; charset=UTF-8"}


class NoaaSpaceWeatherApiClient:
    """Sample API Client."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self.swpc = swpclib.Runner()

    # -------------------- URL helpers --------------------
    def _resolve_url(self, product: str) -> str:
        """Resolve product into absolute SWPC URL when path-like."""
        if not product:
            return ""
        if product.startswith("http://") or product.startswith("https://"):
            return product
        # Default SWPC host for leading slash paths
        if product.startswith("/"):
            return f"https://services.swpc.noaa.gov{product}"
        # Fallback: assume already a path usable by swpclib
        return product

    def _is_json_index(self, product: str) -> bool:
        p = product.lower()
        return p.endswith(".json")

    def _is_dir_index(self, product: str) -> bool:
        # Heuristic: directory-style animation source
        return product.endswith("/")

    def _is_single_image(self, product: str) -> bool:
        p = product.lower()
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

    # -------------------- HTML index parsing --------------------
    def _extract_frame_hrefs(self, html: str, base_url: str) -> list[str]:
        """Parse a simple directory index HTML and return absolute frame URLs.

        Avoids heavy dependencies; uses regex to grab href/src for common image types.
        """
        # Find candidate links from href or img src
        candidates = re.findall(
            r"(?:href|src)=[\"']([^\"']+\.(?:png|jpe?g|gif))[\"']",
            html,
            flags=re.IGNORECASE,
        )
        if not candidates:
            return []

        # Normalize and absolutize
        def abs_url(link: str) -> str:
            if link.startswith("http://") or link.startswith("https://"):
                return link
            if link.startswith("/"):
                # Root-relative
                return f"https://services.swpc.noaa.gov{link}"
            # Directory-relative
            if not base_url.endswith("/"):
                parent = base_url.rsplit("/", 1)[0] + "/"
            else:
                parent = base_url
            return parent + link

        urls = [abs_url(u) for u in candidates]
        # De-dup while preserving order
        seen = set()
        uniq: list[str] = []
        for u in urls:
            if u not in seen:
                seen.add(u)
                uniq.append(u)
        # Some indexes include a latest.* link; keep chronological frames first.
        # Move any 'latest.*' to the end.
        latest = [
            u
            for u in uniq
            if "/latest." in u
            or u.lower().endswith("/latest.png")
            or u.lower().endswith("/latest.jpg")
        ]
        frames = [u for u in uniq if u not in latest]
        return frames + latest

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

        Supports JSON frame lists, HTML directory indexes, or single image URLs.
        """
        # Single-image endpoint
        if self._is_single_image(product):
            url = self._resolve_url(product)
            _LOGGER.debug("first_frame: fetching single image %s", url)
            return await self._fetch_bytes(url)

        # JSON index — use swpclib fast path
        if self._is_json_index(product):
            try:
                response_json = await self.swpc.get_data_method(product)
                first_frame_url = response_json[0].get("url")
                return await self.swpc.get_bytes_method(first_frame_url)
            except Exception as err:
                _LOGGER.debug(
                    "first_frame: JSON index path failed, will try HTML fallback: %s",
                    err,
                )

        # HTML/directory index — parse and fetch the first (or latest) frame
        index_url = self._resolve_url(product)
        try:
            html = await self._fetch_text(index_url)
            frames = self._extract_frame_hrefs(html, index_url)
            if not frames:
                raise RuntimeError("no frames found in index")
            # Prefer last chronological frame for initial view
            first = frames[-1]
            _LOGGER.debug("first_frame: using %s from index %s", first, index_url)
            return await self._fetch_bytes(first)
        except Exception as err:
            _LOGGER.warning(
                "first_frame: failed to parse directory index %s: %s", index_url, err
            )
            # Last resort: ask swpclib to try anyway
            try:
                response_json = await self.swpc.get_data_method(product)
                first_frame_url = response_json[0].get("url")
                return await self.swpc.get_bytes_method(first_frame_url)
            except Exception:
                raise

    async def async_load_animation(self, product) -> bytes:
        """Return bytes for an animated GIF or a single image if only one frame exists."""
        # Attempt library path first — it may handle both JSON and index pages
        try:
            return await self.swpc.gen_gif(product)
        except Exception as err:
            _LOGGER.debug("gen_gif via swpclib failed, falling back: %s", err)

        # Fallbacks
        url = self._resolve_url(product)
        # Single image → just return it
        if self._is_single_image(url):
            return await self._fetch_bytes(url)

        # Parse directory HTML and build GIF
        try:
            html = await self._fetch_text(url)
            frames = self._extract_frame_hrefs(html, url)
            # Keep a sane number of frames to bound size/time
            max_frames = 50
            if len(frames) > max_frames:
                frames = frames[-max_frames:]
            if not frames:
                raise RuntimeError("no frames discovered in directory index")

            # Fetch frame bytes sequentially (could be optimized to parallel with limits)
            images: list[bytes] = []
            for f in frames:
                try:
                    images.append(await self._fetch_bytes(f))
                except Exception as ferr:  # pragma: no cover - best effort
                    _LOGGER.debug("skip bad frame %s: %s", f, ferr)

            # If we ended up with 0 or 1 frames, return the single frame
            if len(images) <= 1:
                return images[0] if images else b""

            # Build GIF via Pillow
            try:
                from PIL import Image  # type: ignore
            except (
                Exception
            ) as perr:  # pragma: no cover - HA image component usually has pillow
                _LOGGER.warning("Pillow not available to build GIF: %s", perr)
                return images[-1]

            pil_frames: list[Image.Image] = []
            for b in images:
                try:
                    pil_frames.append(Image.open(BytesIO(b)).convert("RGB"))
                except Exception as ierr:  # pragma: no cover - skip corrupt
                    _LOGGER.debug("skip corrupt frame while building GIF: %s", ierr)
            if not pil_frames:
                return images[-1]

            bio = BytesIO()
            # Save with a reasonable duration; NOAA frames often closer to 100ms, but use 150ms default
            pil_frames[0].save(
                bio,
                format="GIF",
                save_all=True,
                append_images=pil_frames[1:],
                duration=150,
                loop=0,
                disposal=2,
            )
            return bio.getvalue()
        except Exception as derr:
            _LOGGER.error(
                "Failed to build animation from directory index %s: %s", url, derr
            )
            # Last-chance: return first frame bytes to show something
            return await self.async_get_first_frame(product)
