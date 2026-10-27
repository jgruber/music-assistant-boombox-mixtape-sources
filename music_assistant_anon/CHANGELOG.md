# Changelog

## 2.10.8-fork.4

Switch the add-on to a generic shape: it no longer opinionates on which
custom providers to install.

- `run.sh` now bootstraps only the Custom Provider Installer plugin
  ([jgruber/music-assistant-provider-installer](https://github.com/jgruber/music-assistant-provider-installer)).
- Any additional custom provider (music, player, metadata, audio analysis,
  plugin) is installed through the plugin's config UI, by adding its
  GitHub repository URL.
- Existing custom providers under `/data/custom_providers/<domain>/`
  (Boombox, Mixtape, JW.org Music if you had them) are not removed — they
  continue to load normally. If you want them managed by the installer
  plugin going forward (auto-updates on container start), add their URLs
  to the plugin's config.
- Rename: the add-on's display name is now "Music Assistant Server
  (jgruber fork)". The slug is unchanged, so `/data` and all your state
  carry over without migration.

## 2.10.8-fork.3

Install each custom provider's `requirements` from its manifest into the
Music Assistant venv on container start. Music Assistant pip-installs
provider requirements on first-time UI configuration, not on subsequent
restarts, so a provider installed by this add-on's `run.sh` would fail to
import on restart if its deps aren't already in the venv — Mixtape hit this
on `2.10.8-fork.2` with `ModuleNotFoundError: No module named 'spotapi'`.

## 2.10.8-fork.2

Switch to the clean-fork pattern: the three providers now install at
container start as *custom providers*, rather than being baked into the
base image.

- The fork image (`ghcr.io/jgruber/music-assistant-server`) is now upstream
  Music Assistant plus a HACS-style custom-providers loader, with no music
  providers of its own. The upstream Spotify provider is restored.
- A new `run.sh` fetches the three provider repos (`jgruber/music-assistant-boombox`,
  `-mixtape`, `-jwmusic`) into `/data/custom_providers/` on every start, so
  the three providers auto-update to the latest release of each repo and
  a fresh install (empty `/data`) still gets them.
- The `spotify` custom provider (Mixtape) shadows upstream's Spotify provider
  because they claim the same `domain`. The custom-providers loader emits a
  WARNING on the shadow — operators who want Premium stay on upstream MA.
- Note: this release pulls the full fork image again (~1–2 GB per arch).

## 2.10.8-fork.1

Rebase the add-on onto the `ghcr.io/jgruber/music-assistant-server` fork image
instead of layering changes on top of upstream Music Assistant.

- The three providers (Boombox, Mixtape, JW.org Music) and all their runtime
  deps now ship inside the base image. The add-on's Dockerfile collapses to
  `FROM ${BUILD_FROM}` plus a LABEL.
- `patch_core.py` and `patch_translations.py` are gone — the URL-search filter
  fix, `CONF_PUBLISH_BASE_URL`, and the three providers' translations live in
  the fork's source tree now.
- Pulls the prebuilt image from GHCR instead of building it locally. First
  update pulls ~1–2 GB on each architecture.

## 2.10.8-boombox.9

Drop `sjj` / `sn` / `snnw` from JW.org Music (printed-songbook publications with
no MP3 release); tolerate per-publication fetch errors so one missing pub does
not take down the whole top-level browse.

## 2.10.8-boombox.8

Fix "requested media item could not be found" on JW.org Music tracks whose
`docid` is `0` (International Music); switch the root browse to full `Album`
objects so `album_type` renders properly.

## 2.10.8-boombox.7

Fix `AlbumType` import for the JW.org Music provider (lives in
`music_assistant_models.enums`, not `music_assistant_models.media_items`).

## 2.10.8-boombox.6

Bake a music-note icon (`icon.svg` + `icon_monochrome.svg`) for the JW.org
Music provider so it renders in both dark and light themes.

## 2.10.8-boombox.5

Add `publish_base_url` configuration entry to the stream server. Lets operators
place the stream server behind a reverse proxy that terminates TLS (needed for
Amazon Echo custom skills).

## 2.10.8-boombox.4

Add JW.org Music provider: mirrors the public pub-media catalog at
`jw.org/library/music-songs/` as browsable albums with direct MP3 playback.

## 2.10.8-boombox.3

First release with Mixtape (Spotify catalog, YouTube audio) alongside Boombox.
