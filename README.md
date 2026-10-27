# Music Assistant with Boombox, Mixtape and JW.org Music providers

A Home Assistant add-on repository that ships a single add-on:

- **`music_assistant_anon/`** — a Home Assistant wrapper around [`ghcr.io/jgruber/music-assistant-server`](https://github.com/jgruber/music-assistant-server), the clean soft fork of upstream [Music Assistant](https://music-assistant.io). The fork image is upstream MA plus a HACS-style custom-providers loader; this add-on's job is to install three specific custom providers at container start:
  - **Boombox**: public YouTube Music. Browses, searches and plays what any logged-out visitor to music.youtube.com would see, resolved to playable URLs with yt-dlp. No Google account needed.
  - **Mixtape**: Spotify catalog, YouTube audio. Reads open.spotify.com's public web catalog for search and playlist metadata, and plays audio from YouTube using the same pipeline as Boombox. Does not retrieve or play audio from Spotify, and does not require or substitute for a Spotify account. **Replaces the upstream Spotify provider** (same domain), so this is for users without a Spotify Premium subscription.
  - **JW.org Music**: public music catalog from jw.org/library/music-songs. Mirrors each top-level publication (Sing Out Joyfully and its variants, Original Songs, Sing to Jehovah, International Music, and more) as a browsable album and plays each track from the official MP3 URL the site serves on its public download pages. No account required.

The fork also carries a HACS-style custom-providers mechanism (see [`docs/custom_providers.md`](https://github.com/jgruber/music-assistant-server/blob/main/docs/custom_providers.md) in the fork repo) and a `CONF_PUBLISH_BASE_URL` config entry for operators running the stream server behind a TLS-terminating reverse proxy.

## Installation

1. In Home Assistant: **Settings → Add-ons → Add-on Store → ⋮ (top right) → Repositories**.
2. Paste `https://github.com/jgruber/music-assistant-server-addon` and click **Add**.
3. Close the dialog, scroll down to the new section.
4. Open **Music Assistant (Boombox + Mixtape + JW.org Music)** and **Install**. First install pulls the fork's prebuilt image from GHCR; expect 2–5 minutes.
5. Start the add-on. In the Music Assistant UI, go to **Settings → Music sources → Add Music source** and pick **Boombox**, **Mixtape**, or **JW.org Music**.

## Relationship to the upstream Music Assistant add-on

This add-on uses a different `slug` (`music_assistant_anon` vs upstream `music_assistant`), so it runs as a **separate add-on** with its own `/data` volume. The upstream add-on is unaffected — you can keep both installed, though they will fight over `ingress_port: 8094` on the host network, so run only one at a time.

**Important**: this add-on's base image is the jgruber fork, not upstream Music Assistant. It replaces the upstream Spotify provider with Mixtape. If you have a Spotify Premium subscription and want to use the official Spotify provider, use the upstream add-on, not this one.

## Keeping in sync

Two layers can move independently:

- **Fork image** (`ghcr.io/jgruber/music-assistant-server:latest`) — rebuilt on every push to the fork's `main` branch. The add-on pulls this on **Rebuild** or on the Supervisor's regular cadence.
- **Provider sources** — each of the three providers lives in its own GitHub repo and is fetched into `/data/custom_providers/` by the add-on's `run.sh` on *every* container start. To pick up a provider update, just restart the add-on; the next run syncs. No image rebuild needed.

Manual version bump of the add-on wrapper: edit `version:` in [`music_assistant_anon/config.yaml`](./music_assistant_anon/config.yaml) and the matching `io.hass.version` LABEL in the Dockerfile.

## License

Add-on wrapper: Apache 2.0 (same as upstream Music Assistant). Fork image carries its own LICENSE at the fork repo.
