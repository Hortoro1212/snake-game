import secrets
import threading
import time

auth_event: threading.Event = threading.Event()
authenticated_email: str | None = None

_tokens: dict[str, dict] = {}
TOKEN_TTL = 900  # 15 minutes


def create_token(email: str) -> str:
    token = secrets.token_urlsafe(32)
    _tokens[token] = {'email': email, 'expires': time.time() + TOKEN_TTL}
    return token


def verify_token(token: str) -> str | None:
    global authenticated_email
    _clear_expired()
    entry = _tokens.pop(token, None)
    if entry is None:
        return None
    authenticated_email = entry['email']
    auth_event.set()
    return authenticated_email


def reset_auth() -> None:
    global authenticated_email
    auth_event.clear()
    authenticated_email = None


def _clear_expired() -> None:
    now = time.time()
    expired = [t for t, v in _tokens.items() if v['expires'] <= now]
    for t in expired:
        del _tokens[t]
