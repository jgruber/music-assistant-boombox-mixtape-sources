# Music Assistant Server (jgruber fork) — Home Assistant add-on

A Home Assistant add-on wrapper for
[`jgruber/music-assistant-server`](https://github.com/jgruber/music-assistant-server),
the soft fork of upstream Music Assistant with a HACS-style custom-providers
loader. The add-on's only job is to deliver the fork image with the
[Custom Provider Installer plugin](https://github.com/jgruber/music-assistant-provider-installer)
pre-staged, so an operator can install any custom provider from a GitHub
URL through the plugin's config UI once Music Assistant is up.

## Installation

1. Settings → Add-ons → Add-on Store → ⋮ (top right) → **Repositories**.
2. Paste `https://github.com/jgruber/music-assistant-server-addon` and click **Add**.
3. Open **Music Assistant Server (jgruber fork)** → **Install** → **Start**.
4. In the Music Assistant UI, go to **Settings → Providers → Add plugin**
   and pick **Custom Provider Installer**.
5. In the installer's config, add one or more GitHub repository URLs. Each
   entry is `https://github.com/owner/repo`, optionally with a
   `@branch-or-tag` suffix. Save, then **restart Music Assistant** to
   activate the newly-installed providers.

## Relationship to upstream Music Assistant

Different slug (`music_assistant_anon` vs upstream's `music_assistant`), so
this add-on runs independently with its own `/data`. Both can be installed
side by side, but they contend for `ingress_port: 8094`; run only one at a
time.

## What's in the add-on

- **Base image**: `ghcr.io/jgruber/music-assistant-server:latest`. Upstream
  Music Assistant plus three generic additions — a HACS-style
  custom-providers loader, `CONF_PUBLISH_BASE_URL` for reverse-proxy
  installs, and the URL-search filter fix from upstream PR #7228. No music
  providers of its own.
- **Startup script**: fetches
  [`jgruber/music-assistant-provider-installer`](https://github.com/jgruber/music-assistant-provider-installer)
  into `/data/custom_providers/provider_installer/` on every start and
  `uv pip install`s its manifest requirements. Nothing else.

## Keeping in sync

Two layers can move independently:

- **Fork image** (`ghcr.io/jgruber/music-assistant-server:latest`) — rebuilt
  on every push to the fork's `main` branch. The add-on pulls this on
  **Rebuild** or on the Supervisor's regular cadence.
- **Installer plugin sources** — fetched into `/data/custom_providers/` by
  the add-on's `run.sh` on *every* container start. Restart the add-on to
  pick up a plugin update; no image rebuild needed.
- **Custom providers you added through the installer plugin** — the plugin
  re-fetches each configured URL on every setup. Restart Music Assistant
  (or save the plugin's config) to pick up a provider update.

## License

Add-on wrapper: Apache 2.0 (same as upstream Music Assistant). Fork image
and installer plugin carry their own LICENSE in their own repos.
