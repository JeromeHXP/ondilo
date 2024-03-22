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
    pass


class Ondilo:
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
        req = self.request("get", "/pools")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_ICO_details(self, pool_id: int):
        req = self.request("get", "/pools/" + str(pool_id) + "/device")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_last_pool_measures(self, pool_id: int):
        qstr = "?types[]=temperature&types[]=ph&types[]=orp&types[]=salt&types[]=battery&types[]=tds&types[]=rssi"
        req = self.request("get", f"/pools/{str(pool_id)}/lastmeasures{qstr}")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_pool_recommendations(self, pool_id: int):
        req = self.request("get", "/pools/" + str(pool_id) + "/recommendations")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def validate_pool_recommendation(self, pool_id: int, recommendation_id: int):
        req = self.request("put", "/pools/" + str(pool_id) + "/recommendations/" + str(recommendation_id))

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_user_units(self):
        req = self.request("get", "/user/units")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_user_info(self):
        req = self.request("get", "/user/info")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_pool_config(self, pool_id: int):
        req = self.request("get", "/pools/" + str(pool_id) + "/configuration")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_pool_shares(self, pool_id: int):
        req = self.request("get", "/pools/" + str(pool_id) + "/shares")

        if req.status_code != 200:
            raise OndiloError

        return req.json()

    def get_pool_histo(self, pool_id: int, measure, period: str):
        req = self.request("get", "/pools/" + str(pool_id) + "/measures?type=" + measure + "&period=" + period)

        if req.status_code != 200:
            raise OndiloError

        return req.json()
