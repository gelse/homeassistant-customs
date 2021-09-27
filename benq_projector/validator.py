from __future__ import annotations
import voluptuous as vol
from typing import Any, cast
from urllib.parse import urlparse


def socket(value: Any) -> str:
    """Validate an URL."""
    url_in = str(value)

    if urlparse(url_in).scheme in ["http", "socket"]:
        return cast(str, vol.Schema(vol.Url())(url_in))

    raise vol.Invalid("invalid url")

