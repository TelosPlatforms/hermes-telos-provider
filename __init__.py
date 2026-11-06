"""Telos workspace routers and canonical models. Browser sign-in uses Hermes's PKCE plugin helper."""
from urllib.parse import urlsplit
from providers import register_provider
from providers.base import ProviderProfile

DEFAULT_BASE_URL = "https://app.telosplatforms.com/v1"
EFFORTS = ("none", "minimal", "low", "medium", "high", "xhigh", "max")  # Telos reasoning_effort levels, ascending


def auth_handler(action, args):
    """Hermes's PKCE handler for the configured Telos origin; Hermes stores the credential."""
    from hermes_cli.config import get_env_value_prefer_dotenv
    from hermes_cli.auth_oauth_pkce_plugin import OAuthPKCEConfig, pkce_auth_handler
    base_url = (get_env_value_prefer_dotenv("TELOS_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
    parsed = urlsplit(base_url)
    if parsed.path != "/v1" or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("TELOS_BASE_URL must be an origin followed by /v1")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    return pkce_auth_handler(OAuthPKCEConfig(client_id="hermes", label="Telos",
        authorize_url=origin + "/api/oauth/authorize", token_url=origin + "/api/oauth/token",
        scopes=("inference:write",)))(action, args)


class TelosProfile(ProviderProfile):
    def build_api_kwargs_extras(self, *, reasoning_config=None, **context):
        body, kwargs = super().build_api_kwargs_extras(reasoning_config=reasoning_config, **context)
        conversation_id = context.get("cache_scope_id") or context.get("session_id")
        if conversation_id:
            body["metadata"] = {"conversation_id": conversation_id}
        # Telos fits an explicit level to the selected model; no level (or reasoning off) lets a router choose.
        # A Hermes level above Telos's vocabulary asks for Telos's strongest.
        config = reasoning_config if isinstance(reasoning_config, dict) else {}
        effort = str(config.get("effort") or "").strip().lower()
        if effort and config.get("enabled") is not False:
            kwargs["reasoning_effort"] = effort if effort in EFFORTS else EFFORTS[-1]
        return body, kwargs

    def fetch_models(self, *, api_key=None, base_url=None, timeout=8.0):
        available = super().fetch_models(api_key=api_key, base_url=base_url, timeout=timeout)
        if available is None:
            return None
        return sorted(available, key=lambda key: not key.startswith("route:"))


register_provider(TelosProfile(
    name="telos", display_name="Telos",
    description="Telos — models and workspace routers",
    signup_url="https://app.telosplatforms.com/platform/api-keys",
    env_vars=("TELOS_API_KEY", "TELOS_BASE_URL"), base_url=DEFAULT_BASE_URL,
    api_mode="chat_completions", auth_type="api_key", auth_handler=auth_handler,
))
