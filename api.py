import logging

_LOGGER = logging.getLogger(__name__)


class TechnitiumApi:
    def __init__(self, host, api_key, session, timeout=10):
        self._host = host.rstrip('/')
        self._api_key = api_key
        self._timeout = timeout
        self._session = session

    async def get_status(self):
        url = f"{self._host}/api/settings/get"
        params = {"token": self._api_key}
        try:
            _LOGGER.debug(f"Requesting Technitium status from {url}")
            async with self._session.get(url, params=params, timeout=self._timeout) as resp:
                _LOGGER.debug(f"Technitium status response code: {resp.status}")
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.debug(f"Technitium status response data: {data}")
                response = data.get("response", {})
                # Check if blocking is enabled (temporaryDisableBlockingTill being null/absent means blocking is active)
                temp_disable_till = response.get("temporaryDisableBlockingTill")
                blocking_enabled = temp_disable_till is None or temp_disable_till == ""
                return {"ad_blocking_status": blocking_enabled}
        except Exception as e:
            _LOGGER.error(f"Error fetching Technitium status: {e}")
            return {"ad_blocking_status": None}

    async def pause_ad_blocking(self, seconds):
        # Technitium uses minutes, not seconds
        minutes = max(1, seconds // 60)
        url = f"{self._host}/api/settings/temporaryDisableBlocking"
        params = {"token": self._api_key, "minutes": minutes}
        try:
            _LOGGER.debug(f"Sending pause request to {url} for {minutes} minutes")
            async with self._session.get(url, params=params, timeout=self._timeout) as resp:
                _LOGGER.debug(f"Technitium pause response code: {resp.status}")
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.debug(f"Technitium pause response data: {data}")
                return data
        except Exception as e:
            _LOGGER.error(f"Error pausing ad blocking: {e}")
            return None

    async def enable_ad_blocking(self):
        """Re-enable ad blocking (cancels any temporary disable)."""
        url = f"{self._host}/api/settings/set"
        params = {"token": self._api_key, "enableBlocking": "true"}
        try:
            _LOGGER.debug(f"Sending enable blocking request to {url}")
            async with self._session.get(url, params=params, timeout=self._timeout) as resp:
                _LOGGER.debug(f"Technitium enable response code: {resp.status}")
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.debug(f"Technitium enable response data: {data}")
                return data
        except Exception as e:
            _LOGGER.error(f"Error enabling ad blocking: {e}")
            return None

    async def disable_ad_blocking(self):
        """Disable ad blocking indefinitely."""
        url = f"{self._host}/api/settings/set"
        params = {"token": self._api_key, "enableBlocking": "false"}
        try:
            _LOGGER.debug(f"Sending disable blocking request to {url}")
            async with self._session.get(url, params=params, timeout=self._timeout) as resp:
                _LOGGER.debug(f"Technitium disable response code: {resp.status}")
                resp.raise_for_status()
                data = await resp.json()
                _LOGGER.debug(f"Technitium disable response data: {data}")
                return data
        except Exception as e:
            _LOGGER.error(f"Error disabling ad blocking: {e}")
            return None

    async def close(self):
        # No need to close Home Assistant's managed session
        pass
