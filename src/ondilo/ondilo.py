from typing import Optional, Union, Callable, Dict

from requests import Response
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError

API_HOST = "https://interop.ondilo.com"
API_URL = API_HOST + "/api/customer/v1"
ENDPOINT_TOKEN = "/oauth2/token"
ENDPOINT_AUTHORIZE = "/oauth2/authorize"
DEFAULT_CLIENT_ID = "customer_api"
DEFAULT_CLIENT_SECRET = ""
DEFAULT_SCOPE = "api"


class OndiloError(Exception):
    """Ondilo API error. Provides status code and error message from the API call"""
    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return f"{self.status_code}: {self.message}"


class Ondilo:
    """Ondilo API client. Handles OAuth2 authorization and API requests."""
    def __init__(
        self,
        token: Optional[Dict[str, str]] = None,
        client_id: str = DEFAULT_CLIENT_ID,
        client_secret: str = DEFAULT_CLIENT_SECRET,
        redirect_uri: str = None,
        token_updater: Optional[Callable[[str], None]] = None,
    ):
        self.host = API_HOST
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.token_updater = token_updater
        self.scope = DEFAULT_SCOPE

        extra = {"client_id": self.client_id, "client_secret": self.client_secret}

        self._oauth = OAuth2Session(
            auto_refresh_kwargs=extra,
            redirect_uri=redirect_uri,
            client_id=client_id,
            token=token,
            token_updater=token_updater,
            scope=self.scope,
        )

    def refresh_tokens(self) -> Dict[str, Union[str, int]]:
        """Refresh and return new tokens."""
        token = self._oauth.refresh_token(f"{self.host}{ENDPOINT_TOKEN}")

        if self.token_updater is not None:
            self.token_updater(token)

        return token

    def request_token(
        self,
        authorization_response: Optional[str] = None,
        code: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Generic method for fetching an access token.
        :param authorization_response: Authorization response URL, the callback
                                       URL of the request back to you.
        :param code: Authorization code
        :return: A token dict
        """
        return self._oauth.fetch_token(
            f"{self.host}{ENDPOINT_TOKEN}",
            authorization_response=authorization_response,
            code=code,
            include_client_id=True,
        )

    def get_authurl(self):
        """Get the URL needed for the authorization code grant flow."""
        authorization_url, _ = self._oauth.authorization_url(
            f"{self.host}{ENDPOINT_AUTHORIZE}"
        )
        return authorization_url

    def request(self, method: str, path: str, **kwargs) -> Response:
        """Make a request.

        We don't use the built-in token refresh mechanism of OAuth2 session because
        we want to allow overriding the token refresh logic.
        """
        url = f"{API_URL}{path}"
        try:
            return getattr(self._oauth, method)(url, **kwargs)
        except TokenExpiredError:
            self._oauth.token = self.refresh_tokens()

            return getattr(self._oauth, method)(url, **kwargs)

    def get_pools(self):
        """Get all pools/spas associated with the user."""
        req = self.request("get", "/pools")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_ICO_details(self, pool_id: int) -> dict:
        """
        Retrieves the details of an ICO device associated with a specific pool.

        Args:
            pool_id (int): The ID of the pool.

        Returns:
            dict: A dictionary containing the details of the ICO device.

        Raises:
            OndiloError: If the request to retrieve the device details fails.
        """
        req = self.request("get", "/pools/" + str(pool_id) + "/device")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_last_pool_measures(self, pool_id: int) -> dict:
        """
        Retrieves the last measures of a specific pool.

        Args:
            pool_id (int): The ID of the pool.

        Returns:
            dict: A dictionary containing the last measures for the pool.

        Raises:
            OndiloError: If the request to retrieve the last measures fails.
        """
        qstr = "?types[]=temperature&types[]=ph&types[]=orp&types[]=salt&types[]=battery&types[]=tds&types[]=rssi"
        req = self.request("get", f"/pools/{str(pool_id)}/lastmeasures{qstr}")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_pool_recommendations(self, pool_id: int) -> dict:
        """
        Retrieves the recommendations for a specific pool.

        Args:
            pool_id (int): The ID of the pool.

        Returns:
            dict: A dictionary containing the recommendations for the pool.

        Raises:
            OndiloError: If the request to retrieve the recommendations fails.
        """
        req = self.request("get", "/pools/" + str(pool_id) + "/recommendations")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def validate_pool_recommendation(self, pool_id: int, recommendation_id: int) -> str:
        """
        Validates a pool recommendation.

        Args:
            pool_id (int): The ID of the pool.
            recommendation_id (int): The ID of the recommendation.

        Returns:
            str: The JSON response from the API. Should be "Done".

        Raises:
            OndiloError: If the API request fails.
        """
        req = self.request("put", "/pools/" + str(pool_id) + "/recommendations/" + str(recommendation_id))

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_user_units(self) -> dict:
        """
        Retrieves the units of measurement for the user.

        Returns:
            A dictionary containing the user's units of measurement.
        Raises:
            OndiloError: If the request to retrieve the units fails.
        """
        req = self.request("get", "/user/units")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_user_info(self) -> dict:
        """
        Retrieves the user information from the Ondilo API.

        Returns:
            A dictionary containing the user information.
        Raises:
            OndiloError: If the request to retrieve the user info fails.
        """
        req = self.request("get", "/user/info")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_pool_config(self, pool_id: int) -> dict:
        """
        Retrieves the configuration of a pool.

        Args:
            pool_id (int): The ID of the pool.

        Returns:
            dict: The configuration of the pool.

        Raises:
            OndiloError: If the request to retrieve the configuration fails.
        """
        req = self.request("get", "/pools/" + str(pool_id) + "/configuration")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_pool_shares(self, pool_id: int) -> dict:
        """
        Retrieves the shares of a specific pool.

        Args:
            pool_id (int): The ID of the pool.

        Returns:
            dict: A dictionary containing the shares of the pool.

        Raises:
            OndiloError: If the request to retrieve the shares fails.
        """
        req = self.request("get", "/pools/" + str(pool_id) + "/shares")

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()

    def get_pool_histo(self, pool_id: int, measure: str, period: str) -> dict:
        """
        Retrieves the historical data for a specific pool.

        Args:
            pool_id (int): The ID of the pool.
            measure (str): The type of measure to retrieve.
            period (str): The time period for the historical data. Allowed values are "day", "week", "month".

        Returns:
            dict: The historical data for the pool.

        Raises:
            OndiloError: If the request to retrieve the historical data fails.
        """
        req = self.request("get", "/pools/" + str(pool_id) + "/measures?type=" + measure + "&period=" + period)

        if req.status_code != 200:
            raise OndiloError(req.status_code, req.text)

        return req.json()
