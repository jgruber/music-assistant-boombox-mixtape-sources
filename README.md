# Music Assistant with Boombox, Mixtape and JW.org Music providers

A Home Assistant add-on repository that ships a single add-on:

- **`music_assistant_anon/`** — a fork of the upstream [Music Assistant](https://music-assistant.io) add-on with three music providers baked in:
  - **Boombox** (directory `ytmusic_anon/`): public YouTube Music. Browses, searches and plays what any logged-out visitor to music.youtube.com would see, resolved to playable URLs with yt-dlp. No Google account needed.
  - **Mixtape** (directory `spotify/`): Spotify catalog, YouTube audio. Reads open.spotify.com's public web catalog for search and playlist metadata, and plays audio from YouTube using the same pipeline as Boombox. Does not retrieve or play audio from Spotify, and does not require or substitute for a Spotify account.
  - **JW.org Music** (directory `jwmusic/`): public music catalog from jw.org/library/music-songs. Mirrors each top-level publication (Sing Out Joyfully and its variants, Original Songs, Sing to Jehovah, International Music, and more) as a browsable album and plays each track from the official MP3 URL the site serves on its public download pages. No account required.

The two anonymous-catalog providers (Boombox, Mixtape) are complements to, not replacements for, the official YouTube Music and Spotify providers. If you have those subscriptions, keep the official providers installed alongside these — they offer features (library sync, personalized recommendations, higher bitrates, official support) that the public web endpoints cannot provide.

## Installation

1. In Home Assistant: **Settings → Add-ons → Add-on Store → ⋮ (top right) → Repositories**.
2. Paste `https://github.com/jgruber/music-assistant-boombox-mixtape-sources` and click **Add**.
3. Close the dialog, scroll down to the new section.
4. Open **Music Assistant (Boombox + Mixtape + JW.org Music)** and **Install**. First install builds the Docker image locally; expect 2–5 minutes.
5. Start the add-on. In the Music Assistant UI, go to **Settings → Music sources → Add Music source** and pick **Boombox**, **Mixtape**, or **JW.org Music**.

## Relationship to the upstream Music Assistant add-on

This add-on uses a different `slug` (`music_assistant_anon` vs upstream `music_assistant`), so it runs as a **separate add-on** with its own `/data` volume. The upstream add-on is unaffected — you can keep both installed, though they will fight over `ingress_port: 8094` on the host network, so run only one at a time.

## Keeping in sync with upstream Music Assistant

A GitHub Action (`.github/workflows/upstream-bump.yml`) runs daily, checks the latest stable `music-assistant/server` release, and opens a PR that bumps `config.yaml`, `build.yaml` and the Dockerfile LABEL when a new version is out. Merge the PR, then in HA: open the add-on → **Rebuild**.

Manual bump: edit the `version:` field in [`music_assistant_anon/config.yaml`](./music_assistant_anon/config.yaml), the matching tags in [`music_assistant_anon/build.yaml`](./music_assistant_anon/build.yaml), and the `io.hass.version` LABEL in the Dockerfile.

## License

Providers inherit Music Assistant's license (Apache 2.0). Add-on files reused from upstream are subject to [Music Assistant's add-on repository license](https://github.com/music-assistant/home-assistant-addon).
