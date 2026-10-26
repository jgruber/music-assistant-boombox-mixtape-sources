"""
Build-time patches for Music Assistant core.

Each patch is a precise text substitution against the installed package in the
venv. On a miss the build fails loudly so an upstream shape change is caught
before deploy, not at runtime.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass

import music_assistant  # resolves the real site-packages path

MA_PKG = os.path.dirname(music_assistant.__file__)
CTRL_MUSIC = os.path.join(MA_PKG, "controllers", "music", "controller.py")
CTRL_STREAMS = os.path.join(MA_PKG, "controllers", "streams", "controller.py")
CONSTANTS = os.path.join(MA_PKG, "constants.py")


@dataclass(frozen=True)
class Edit:
    """One anchor-based text substitution."""

    file: str
    old: str
    new: str


# ---------------------------------------------------------------------------
# Patch 1: respect media_types/providers in MusicController.search when the
# query is a public shareable URL. Upstream PR music-assistant/server#7228.
# ---------------------------------------------------------------------------

SEARCH_FILTER = Edit(
    file=CTRL_MUSIC,
    old=(
        "        if (url_result := await self._search_shareable_url(search_query)) is not None:\n"
        "            return url_result\n"
    ),
    new=(
        "        # fork patch (mirrors upstream PR #7228): respect the caller's\n"
        "        # media_types and providers filters when resolving a public shareable URL,\n"
        "        # so a pasted Spotify / Apple Music / Qobuz / Deezer URL doesn't come back\n"
        "        # once per scoped call from the frontend's progressive search, and so a\n"
        "        # type-restricted search doesn't return other-type items.\n"
        "        try:\n"
        "            _url_type, _url_prov, _ = await parse_uri(search_query, validate_id=False)\n"
        "            _url_is_shareable = _url_prov in PROVIDERS_WITH_SHAREABLE_URLS\n"
        "        except InvalidProviderURI:\n"
        "            _url_is_shareable = False\n"
        "            _url_type = _url_prov = None\n"
        "        if _url_is_shareable:\n"
        "            if _url_type not in media_types:\n"
        "                return SearchResults()\n"
        "            if providers is not None:\n"
        "                _requested = set(providers)\n"
        "                _primary = self.mass.get_provider(_url_prov)\n"
        "                if not _primary or not (\n"
        "                    _primary.instance_id in _requested\n"
        "                    or _primary.domain in _requested\n"
        "                ):\n"
        "                    return SearchResults()\n"
        "            if (url_result := await self._search_shareable_url(search_query)) is not None:\n"
        "                return url_result\n"
    ),
)


# ---------------------------------------------------------------------------
# Patch 2: add an optional CONF_PUBLISH_BASE_URL that fully overrides the URL
# base used in stream URLs handed to players. Lets operators place the stream
# server behind a reverse proxy (HTTPS, friendly hostname, remapped port)
# while publish_ip stays an IP for mDNS/AirPlay discovery.
#
# Default behavior unchanged: when publish_base_url is unset (default), the
# existing http://<publish_ip>:<bind_port> URL is used.
# ---------------------------------------------------------------------------

# a) register the constant alongside the existing publish/bind keys
PUBLISH_BASE_URL_CONSTANT = Edit(
    file=CONSTANTS,
    old='CONF_PUBLISH_IP: Final[str] = "publish_ip"\n',
    new=(
        'CONF_PUBLISH_IP: Final[str] = "publish_ip"\n'
        'CONF_PUBLISH_BASE_URL: Final[str] = "publish_base_url"\n'
    ),
)

# b) import the new constant in the streams controller
PUBLISH_BASE_URL_IMPORT = Edit(
    file=CTRL_STREAMS,
    old="    CONF_PUBLISH_IP,\n",
    new="    CONF_PUBLISH_BASE_URL,\n    CONF_PUBLISH_IP,\n",
)

# c) add urllib.parse.urlparse import for the validator
URLLIB_IMPORT = Edit(
    file=CTRL_STREAMS,
    old=(
        "from typing import TYPE_CHECKING, cast\n"
        "from uuid import uuid4\n"
    ),
    new=(
        "from typing import TYPE_CHECKING, cast\n"
        "from urllib.parse import urlparse\n"
        "from uuid import uuid4\n"
    ),
)

# d) add the validator function next to _is_valid_publish_ip
PUBLISH_BASE_URL_VALIDATOR = Edit(
    file=CTRL_STREAMS,
    old=(
        "    try:\n"
        "        ip_address(value)\n"
        "    except ValueError:\n"
        "        return False\n"
        "    return True\n"
        "\n"
        "\n"
        "def _root_cause(err: BaseException) -> BaseException:\n"
    ),
    new=(
        "    try:\n"
        "        ip_address(value)\n"
        "    except ValueError:\n"
        "        return False\n"
        "    return True\n"
        "\n"
        "\n"
        "def _is_valid_publish_base_url(value: ConfigValueType) -> bool:\n"
        '    """Return whether a configured publish_base_url value is usable.\n'
        "\n"
        "    An empty value (unset) is allowed and means the default http://<publish_ip>:\n"
        "    <bind_port> URL is used. A non-empty value must be an http(s) scheme + host\n"
        "    URL with no path (other than '/'), no query, and no fragment.\n"
        '    """\n'
        "    if not value:\n"
        "        return True\n"
        "    if not isinstance(value, str):\n"
        "        return False\n"
        "    parsed = urlparse(value)\n"
        '    if parsed.scheme not in ("http", "https"):\n'
        "        return False\n"
        "    if not parsed.netloc:\n"
        "        return False\n"
        '    if parsed.path and parsed.path != "/":\n'
        "        return False\n"
        "    if parsed.query or parsed.fragment:\n"
        "        return False\n"
        "    return True\n"
        "\n"
        "\n"
        "def _root_cause(err: BaseException) -> BaseException:\n"
    ),
)

# e) register the new ConfigEntry right after the publish_ip entry
PUBLISH_BASE_URL_ENTRY = Edit(
    file=CTRL_STREAMS,
    old=(
        "            ConfigEntry(\n"
        "                key=CONF_PUBLISH_IP,\n"
        "                type=ConfigEntryType.STRING,\n"
        "                default_value=CONF_VALUE_AUTO,\n"
        "                required=False,\n"
        '                category="generic",\n'
        "                advanced=True,\n"
        "                requires_reload=True,\n"
        "                validate=_is_valid_publish_ip,\n"
        "            ),\n"
        "            ConfigEntry(\n"
        "                key=CONF_BIND_PORT,\n"
    ),
    new=(
        "            ConfigEntry(\n"
        "                key=CONF_PUBLISH_IP,\n"
        "                type=ConfigEntryType.STRING,\n"
        "                default_value=CONF_VALUE_AUTO,\n"
        "                required=False,\n"
        '                category="generic",\n'
        "                advanced=True,\n"
        "                requires_reload=True,\n"
        "                validate=_is_valid_publish_ip,\n"
        "            ),\n"
        "            ConfigEntry(\n"
        "                key=CONF_PUBLISH_BASE_URL,\n"
        "                type=ConfigEntryType.STRING,\n"
        "                default_value=None,\n"
        "                required=False,\n"
        '                category="generic",\n'
        "                advanced=True,\n"
        "                requires_reload=True,\n"
        "                validate=_is_valid_publish_base_url,\n"
        "            ),\n"
        "            ConfigEntry(\n"
        "                key=CONF_BIND_PORT,\n"
    ),
)

# f) consume the override when building _base_url
PUBLISH_BASE_URL_USE = Edit(
    file=CTRL_STREAMS,
    old=(
        "        # the single address players are handed, taken from the top of the ranked list\n"
        "        self.publish_ip = self._publish_addresses[0]\n"
        '        self._base_url = f"http://{format_ip_for_url(self.publish_ip)}:{self.publish_port}"\n'
    ),
    new=(
        "        # the single address players are handed, taken from the top of the ranked list\n"
        "        self.publish_ip = self._publish_addresses[0]\n"
        "        # publish_base_url, when set, overrides the generated URL entirely so operators\n"
        "        # can place the stream server behind a reverse proxy (TLS, friendly hostname,\n"
        "        # different port). publish_ip stays an IP for mDNS/AirPlay discovery.\n"
        "        configured_base_url = self.mass.config.get_raw_core_config_value(\n"
        "            self.domain, CONF_PUBLISH_BASE_URL, None\n"
        "        )\n"
        "        if configured_base_url and _is_valid_publish_base_url(configured_base_url):\n"
        '            self._base_url = str(configured_base_url).rstrip("/")\n'
        "        else:\n"
        '            self._base_url = f"http://{format_ip_for_url(self.publish_ip)}:{self.publish_port}"\n'
    ),
)


EDITS: tuple[Edit, ...] = (
    SEARCH_FILTER,
    PUBLISH_BASE_URL_CONSTANT,
    PUBLISH_BASE_URL_IMPORT,
    URLLIB_IMPORT,
    PUBLISH_BASE_URL_VALIDATOR,
    PUBLISH_BASE_URL_ENTRY,
    PUBLISH_BASE_URL_USE,
)


def apply_edit(edit: Edit) -> int:
    with open(edit.file, encoding="utf-8") as f:
        src = f.read()
    if edit.new in src:
        print(f"patch_core: already applied in {edit.file}")
        return 0
    if edit.old not in src:
        print(
            f"patch_core: anchor not found in {edit.file}; upstream changed shape",
            file=sys.stderr,
        )
        # emit the first ~80 chars of the missing anchor for triage
        preview = edit.old.splitlines()[0][:80] if edit.old else ""
        print(f"  missing anchor begins: {preview!r}", file=sys.stderr)
        return 1
    if src.count(edit.old) > 1:
        print(
            f"patch_core: anchor is ambiguous in {edit.file}; refusing to apply",
            file=sys.stderr,
        )
        return 1
    with open(edit.file, "w", encoding="utf-8") as f:
        f.write(src.replace(edit.old, edit.new, 1))
    print(f"patch_core: applied edit in {edit.file}")
    return 0


def main() -> int:
    rc = 0
    for edit in EDITS:
        rc |= apply_edit(edit)
    return rc


if __name__ == "__main__":
    sys.exit(main())
