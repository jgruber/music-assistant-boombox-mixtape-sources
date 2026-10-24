# Music Assistant (Boombox + Mixtape) — local add-on

Fork of the upstream `music_assistant` add-on that bakes in two music providers:

- **Boombox** (directory `ytmusic_anon/`) — public YouTube Music. Browses, searches and plays what any logged-out visitor to music.youtube.com would see, resolved to playable URLs with yt-dlp. No Google account needed; no substitute for YouTube Music Premium.
- **Mixtape** (directory `spotify/`) — Spotify catalog, YouTube audio. Reads open.spotify.com's public web catalog for search and playlist metadata, and plays audio from YouTube using the same pipeline as Boombox. Does not retrieve or play audio from Spotify. Does not require, use, or substitute for a Spotify account.

Both providers are complements to, not replacements for, the official YouTube Music and Spotify providers. If you have those subscriptions, keep the official providers installed alongside these.

## Updating when upstream MA releases a new version

The repo's `upstream-bump` GitHub Action watches `music-assistant/server` daily and opens a PR with the bumps when a new stable release lands. Merge → HA → **Rebuild**.

Manual bump:
1. `version:` in `config.yaml`, matching tags in `build.yaml`'s `build_from:` entries, and the `io.hass.version` LABEL in the Dockerfile.
2. If any new field appeared in the upstream add-on's `config.yaml`, mirror it here.
3. From the HA UI: open the add-on → **Rebuild**.

## Rollback

The upstream `music_assistant` add-on is unaffected by this fork. To roll back: stop this add-on and start the upstream one. (Data is per-slug, so your library from this fork does **not** carry over to the upstream add-on; back up first if you've been using this fork for real.)
