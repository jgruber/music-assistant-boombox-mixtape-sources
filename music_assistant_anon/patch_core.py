"""
Build-time patch for Music Assistant core.

Upstream `MusicController._search_shareable_url` ignores both the caller's
`media_types` filter AND the caller's `providers` filter, and the resolved
item (e.g. a Spotify playlist) comes back from every per-call context the
MA frontend fires:

  * `useProgressiveSearch` dispatches one `music/search` per configured music
    provider that supports SEARCH plus the library, each with
    `providers=[<one target>]`. Every call hits the shareable-URL path and
    returns the playlist, which the frontend then concatenates into a flat
    `playlists[]` — one duplicate per provider in the UI.
  * On a global search the per-media_type section queries would also each
    receive the item in the playlist bucket regardless of what they asked for.

Fix: at the single call site, skip the shareable-URL handler when `providers`
is set (per-provider calls fall through to the real per-provider search path,
and our provider's own URL short-circuit returns the item on the one call
that targets `spotify`). On the global path, mask fields the caller didn't
ask for so section queries only get what they asked for.

Resolve the controller path from the installed package so a Python-version
bump upstream doesn't break the patch.
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
    "        # ytmusic_anon fork patch: upstream _search_shareable_url ignores both\n"
    "        # the caller's providers filter and media_types filter. Skip it on\n"
    "        # per-provider calls so the frontend's progressive search doesn't get\n"
    "        # the same item back from every per-provider call; on the global path\n"
    "        # mask fields the caller didn't ask for.\n"
    "        if providers is None and (url_result := await self._search_shareable_url(search_query)) is not None:\n"
    "            for _mt, _attr in (\n"
    "                (MediaType.ARTIST, 'artists'),\n"
    "                (MediaType.ALBUM, 'albums'),\n"
    "                (MediaType.TRACK, 'tracks'),\n"
    "                (MediaType.PLAYLIST, 'playlists'),\n"
    "                (MediaType.AUDIOBOOK, 'audiobooks'),\n"
    "                (MediaType.PODCAST, 'podcasts'),\n"
    "            ):\n"
    "                if _mt not in media_types:\n"
    "                    setattr(url_result, _attr, [])\n"
    "            return url_result\n"
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
