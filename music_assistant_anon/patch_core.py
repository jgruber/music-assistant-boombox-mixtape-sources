"""
Build-time patch for Music Assistant core.

Upstream `MusicController.search` resolves a public shareable URL via
`_search_shareable_url` and returns the resolved item, but ignores both
the caller's `media_types` filter AND the caller's `providers` filter.

The MA frontend's `useProgressiveSearch` dispatches one `music/search`
per configured music provider that supports SEARCH plus one for the
library, each with `providers=[<one target>]`. Without a providers
filter the resolved item comes back from every scoped call, so one
pasted Spotify / Apple Music / Qobuz / Deezer URL shows up N times in
the UI.

Fix (upstream PR music-assistant/server#7228, mirrored here as a
build-time patch): at the single call site, parse the URL ourselves,
and before resolving:

  * if the URL's media_type isn't in the caller's `media_types`, return
    empty immediately (covers playlist URL on a tracks-only search,
    radio URL on a tracks-only search, etc.);
  * if the caller gave a providers filter, only resolve on the one
    scoped call whose target matches the URL's provider by instance_id
    or domain; return empty on the others.

Resolve the controller path from the installed package so a Python-
version bump upstream doesn't break the patch.
"""

from __future__ import annotations

import os
import sys

import music_assistant  # resolves the real site-packages path

CTRL = os.path.join(
    os.path.dirname(music_assistant.__file__),
    "controllers",
    "music",
    "controller.py",
)

OLD = (
    "        if (url_result := await self._search_shareable_url(search_query)) is not None:\n"
    "            return url_result\n"
)

NEW = (
    "        # BoomboxMixtape fork patch (mirrors upstream PR #7228): respect the\n"
    "        # caller's media_types and providers filters when resolving a public\n"
    "        # shareable URL, so a pasted Spotify / Apple Music / Qobuz / Deezer URL\n"
    "        # doesn't come back once per scoped call from the frontend's progressive\n"
    "        # search, and so a type-restricted search doesn't return other-type items.\n"
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
)


def main() -> int:
    with open(CTRL, encoding="utf-8") as f:
        src = f.read()
    if NEW in src:
        print(f"patch_core: already applied to {CTRL}")
        return 0
    if OLD not in src:
        print(
            f"patch_core: anchor not found in {CTRL}; upstream changed shape",
            file=sys.stderr,
        )
        return 1
    with open(CTRL, "w", encoding="utf-8") as f:
        f.write(src.replace(OLD, NEW))
    print(f"patch_core: applied to {CTRL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
