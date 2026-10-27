# Changelog

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
