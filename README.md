# terminal-music

Play Spotify from your terminal with **Spotatui for browsing** and **Spotify Soloist for audio**. Enter your own Soloist API key, pair once, then launch with one command:

```sh
terminal-music
```

```text
Spotatui (library, search, playlists) → Spotify Connect → Soloist → speakers
```

This project is a small installer and launcher, not a new Spotify client. It uses Soloist instead of Spotatui's built-in librespot streaming, which can fail with `error audio key 0 1`. It does not repair librespot or bypass Spotify authentication.

## Requirements

- Linux with PipeWire or PulseAudio, a working default output, and Python 3.10+.
- A Spotify Premium account and your own **Soloist API key** from the [Soloist dashboard](https://developer.spotify.com/dashboard/soloist). A Web API client ID or client secret is not a Soloist key.
- Spotify on a phone/tablet on the same local network for initial pairing.
- Internet access to Spotify and GitHub. Git is needed to clone this repo.

Soloist supports Linux x86_64, ARM64 and ARMv7. Automatic Spotatui installation requires a matching official release and checksums; if one isn't available, install Spotatui separately and rerun setup. Alpine/musl, macOS and Windows are outside this launcher's current scope.

## Install

Clone this repository from its GitHub page, open its directory, then run:

```sh
bash install.sh
```

The installer:

1. Installs `terminal-music` into `~/.local/bin` without sudo.
2. Reuses installed players, or downloads Soloist directly from Spotify and Spotatui from its official GitHub releases. Spotatui downloads are checked against the release's SHA-256 checksum file.
3. Prompts for your Soloist API key with input hidden and stores it with owner-only permissions.
4. Creates separate Spotatui settings with native streaming disabled. Your original Spotatui config stays unchanged.

You can choose a device name:

```sh
bash install.sh --name "My Terminal"
```

No player binaries, credentials, or user sessions are distributed in this repository. Spotify's binaries remain subject to Spotify's terms. See [official Soloist downloads](https://developer.spotify.com/documentation/soloist/reference/downloads-and-updates).

## Pair once

```sh
terminal-music pair
```

Soloist starts in the background. Open Spotify on your phone on the same Wi-Fi, select **Terminal-Music** (or your chosen name) in the device picker, and play a song. This pairs Soloist and saves its session.

Next:

```sh
terminal-music
```

Complete Spotatui's own Spotify login when prompted. Press **d** and choose **Terminal-Music**. Spotatui's login and Soloist's pairing are separate: the first lets you browse and control your account; the second authorizes the audio player. Keep both on the same Spotify account.

For subsequent listening, run `terminal-music`. No browser or desktop Spotify app needs to remain open. Soloist stays running when you close Spotatui; it does not automatically start at login.

If your shell says “command not found”, run `~/.local/bin/terminal-music`, or add this to your shell configuration and open a new terminal:

```sh
export PATH="$HOME/.local/bin:$PATH"
```

## Commands

| Command | Purpose |
| --- | --- |
| `terminal-music` | Start/reuse Soloist and open Spotatui |
| `terminal-music pair` | Start Soloist and show pairing instructions |
| `terminal-music start` | Start audio player only |
| `terminal-music status` | Show this setup's Soloist process status |
| `terminal-music stop` | Stop this setup's Soloist process |
| `terminal-music setup --reset-key` | Replace your key using the hidden prompt |
| `terminal-music setup --name "My Terminal"` | Change the device name; restart Soloist afterward |
| `terminal-music update` | Update Soloist and a Spotatui copy managed by this tool; stop first |
| `terminal-music paths` | Show configuration and log locations |

A system/package-manager Spotatui installation is reused and must be updated through its own package manager. Updating Soloist installs this tool's own copy without replacing your system executable.

## Files and settings

Paths follow absolute `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME`, and `XDG_STATE_HOME` values when set. Defaults:

| Path | Contents |
| --- | --- |
| `~/.config/terminal-music/settings.json` | Device name |
| `~/.config/terminal-music/api-key` | Private Soloist key |
| `~/.config/terminal-music/spotatui.yml` | This launcher's Spotatui settings |
| `~/.local/share/terminal-music/bin/` | Downloaded player executables |
| `~/.local/share/terminal-music/soloist/` | Soloist device identity and pairing |
| `~/.cache/terminal-music/soloist/` | Audio cache, capped at 100 MB |
| `~/.local/state/terminal-music/soloist.log` | Private diagnostic log |

Key and config files use mode `600`; private directories use `700`. Soloist currently requires the key as a command-line argument, so other processes running as your user (and root) can inspect it. Do not post process listings, API keys, session files, or unredacted logs publicly. The optional Soloist control socket binds only to `127.0.0.1`.

## Troubleshooting

- **Device missing:** ensure Soloist is running, pair from Spotify on the same network, and check that a VPN/router/firewall isn't blocking local discovery.
- **No sound:** select your Soloist device in Spotatui, check the default PipeWire/PulseAudio output, then inspect the local Soloist log. Do not select a separate `spotatui` native player from another Spotatui instance.
- **Invalid key/login:** use a Soloist key from your own Premium account. Run `terminal-music setup --reset-key`, then restart and pair again.
- **Expired build / exit code 10:** stop Soloist and run `terminal-music update`.
- **Player won't launch:** run its `--version` to check library compatibility. Install a compatible Spotatui build using its [official instructions](https://github.com/LargeModGames/spotatui).
- **Another Soloist already running:** this project keeps its own data directory. Stop a previous setup if you don't want multiple devices listed.

## Uninstall

Stop playback with `terminal-music stop`, then remove `~/.local/bin/terminal-music`. To erase this setup's saved key, pairing and files, remove the four `terminal-music` directories shown by `terminal-music paths` before deleting the launcher. Your original Spotatui configuration and system-installed players are not removed.

## Development and validation

```sh
python3 -m unittest discover -s tests -v
bash -n install.sh publish.sh
```

Tests use temporary directories and mocked downloads/processes. They do not access your Spotify account. The original Soloist/Spotatui combination was manually confirmed to play audio on Manjaro x86_64; this generalized installer has not yet been verified with fresh accounts or every supported architecture.

## Credits

- [Spotatui](https://github.com/LargeModGames/spotatui) provides the terminal interface.
- [Spotify Soloist](https://developer.spotify.com/documentation/soloist) provides official audio playback.

This project is independent and is not affiliated with or endorsed by Spotify or Spotatui. The MIT license here covers only this repository's original code; it does not relicense either player.
