import httpx
import os
import asyncio
import json
from .utils import get_auth_token
from typing import Dict
from .errors import UnExpectedError


class Requester:
    """
    A class for making HTTP requests to the GitHub Gists API.

    Args:
        auth_token (str, optional): GitHub API token for authentication.
        timeout (int, optional): Request timeout in seconds.
        sleep_time (float, optional): Time to sleep between retries.
        max_connection_retries (int, optional): Number of retries for failed requests.
    """

    BASE_HEADERS: Dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": os.environ.get("GITHUB_API_VERSION", "2022-11-28"),
    }
    API_URL: str = "https://api.github.com/gists"

    def __init__(
        self,
        auth_token: str = None,
        timeout: int = 5,
        sleep_time: float = 0.5,
        max_connection_retries: int = 2,
    ):
        self.auth_token = auth_token or get_auth_token()
        self.timeout = timeout
        self.sleep_time = sleep_time
        self.retries = max_connection_retries
        self.headers = self.BASE_HEADERS.copy()
        self.headers["Authorization"] = f"Bearer {auth_token}"

    async def _async_request(
        self, method: str, endpoint: str = "", data: dict = None, params: dict = None
    ):
        """
        Send an HTTP request to the GitHub Gists API asynchronously.

        Args:
            method (str): HTTP request method (GET, POST, PUT, DELETE, etc.).
            endpoint (str, optional): API endpoint path.
            data (dict, optional): JSON data to send in the request body.
            params (dict, optional): URL query parameters.

        Returns:
            dict: Parsed JSON response from the API.

        Raises:
            httpx.TimeoutException: If a timeout occurs during the request.
            UnExpectedError: If an unexpected HTTP error occurs.
        """
        url = self.API_URL + endpoint
        tries = 0
        resp = None
        while resp is None and tries <= self.retries:
            tries += 1
            try:
                async with httpx.AsyncClient(
                    headers=self.headers, timeout=self.timeout
                ) as client:
                    resp = await client.request(
                        method=method, url=url, json=data, params=params
                    )
            except httpx.TimeoutException as e:
                err = f"Timeout error: {e}"
                if tries >= self.retries:
                    raise httpx.TimeoutException(err)
            except Exception as e:
                err = f"An Unexpected error occurred: {e}"
                if tries >= self.retries:
                    raise UnExpectedError(err)

            await asyncio.sleep(self.sleep_time)

        try:
            json_ = resp.json()
        except json.decoder.JSONDecodeError:
            json_ = {}

        json_["code"] = resp.status_code
        return json_

    def _request(
        self, method: str, endpoint: str = "", data: dict = None, params: dict = None
    ):
        """
        Send an HTTP request to the GitHub Gists API synchronously.

        Args:
            method (str): HTTP request method (GET, POST, PUT, DELETE, etc.).
            endpoint (str, optional): API endpoint path.
            data (dict, optional): JSON data to send in the request body.
            params (dict, optional): URL query parameters.

        Returns:
            dict: Parsed JSON response from the API.
        """
        return asyncio.run(
            self._async_request(method, endpoint, data=data, params=params)
        )
