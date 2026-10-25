# Third-party projects and attribution

This repository contains original setup/launcher code and documentation. It does not vendor Spotatui or Spotify Soloist source code, archives, executables, credentials, or music. Downloads happen on the user's computer from the upstream hosts.

## Spotatui

- Project: https://github.com/LargeModGames/spotatui
- Maintainer: LargeModGames; additional work by the project's contributors.
- License: MIT, https://github.com/LargeModGames/spotatui/blob/main/LICENSE
- Upstream copyright notices: Copyright (c) 2021 Alexander Keliris; Copyright (c) 2025 LargeModGames.
- Role: terminal interface, library browsing, and Spotify playback controls.

Spotatui retains its own license and ownership. Anyone who later vendors or redistributes its code or binaries must preserve the applicable upstream copyright and permission notices. This repository's license grants no ownership over Spotatui.

## Spotify Soloist

- Publisher: Spotify.
- Documentation: https://developer.spotify.com/documentation/soloist
- Official downloads and distribution instructions: https://developer.spotify.com/documentation/soloist/reference/downloads-and-updates
- Third-party notices: follow the Soloist Third-Party Licenses link from the official download page.
- Role: audio playback and Spotify Connect receiver.

Spotify instructs users not to redistribute Soloist archives or binaries directly. This repository does not host or bundle them; its installer downloads from Spotify's official server onto each user's machine. Users must generate their own Soloist API key, review and accept applicable Spotify terms, and pair their own account. Never publish a shared API key or session.

## Project identity

terminal-music is an independent community integration. It is not an official Spotify or Spotatui release and claims no endorsement. Spotify and Spotatui names identify the upstream products. No upstream logos or branding assets are bundled.

The MIT license in this repository applies only to its original contributions. Attribution does not replace compliance with upstream licenses or service terms.
