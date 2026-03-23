<p align="center">
  <img src="https://github.com/user-attachments/assets/6d562252-a7e6-44ab-bfeb-8a753469b117" width="700">
</p>
<p align="center">
  <a href="https://github.com/qwertyquerty/pypresence">
    <img src="https://img.shields.io/badge/using-pypresence-00bb88?style=flat-square&logo=discord">
  </a>
  <img src="https://img.shields.io/badge/platform-Windows%20%26%20Linux-lightgrey?style=flat-square">
  <img src="https://img.shields.io/github/downloads/Jelloge/Deadlock-Rich-Presence/total?style=flat-square">
  <img src="https://img.shields.io/badge/license-GPL--3.0-blue?style=flat-square">
</p>
<p align="center">
Discord Rich Presence for Valve's
<a href="https://store.steampowered.com/app/1422450/Deadlock/">Deadlock</a>.
Shows your live in-game status on your Discord profile
(hero, game mode, match type, party size, match timer, etc). Supports all game modes!
</p>
<p align="center">
  <img src="https://github.com/user-attachments/assets/bb411785-66f4-43ce-8c9e-d979f6ca7e96" height="135">
  <img src="https://github.com/user-attachments/assets/1d872c8d-a10f-4807-89ea-3f5327471e4b" height="135">
  <img src="https://github.com/user-attachments/assets/52f40fe4-fd2a-4abf-b404-280c84a50d8e" height="135">
  <img src="https://github.com/user-attachments/assets/112f40b9-d8d4-40f2-afa1-9f950a7ab438" height="135">
</p>

## Installation

### Windows
1. Download **DeadlockRPC-windows-x86_64.zip** from the [latest release](https://github.com/Jelloge/Deadlock-Rich-Presence/releases/latest)
2. Extract and run **DeadlockRPC.exe**,  it will show up in your system tray

### Linux
1. Download **DeadlockRPC-linux-x86_64.zip** from the [latest release](https://github.com/Jelloge/Deadlock-Rich-Presence/releases/latest)
2. Extract and run:
```bash
unzip DeadlockRPC-linux-x86_64.zip
cd DeadlockRPC
chmod +x DeadlockRPC
./DeadlockRPC
```
Make sure `-condebug` is in your Steam launch options for Deadlock (the app needs `console.log` to track game state).

### Notes
- The app automatically checks for updates on startup and prompts you to update if a new release is available.
- By default, the app launches Deadlock with `-condebug` automatically via Steam.
- If you manage your own Steam launch options, set `"launch_game": false` in `config.json` and add `-condebug` to your launch options manually:
<img width="480" height="119" alt="Steam launch options" src="https://github.com/user-attachments/assets/21aaf748-3f15-41de-9479-d48b3b8eba6d" />
<details>
<summary>Running from source</summary>

If you prefer to run from source instead of using the pre-built binary:

```bash
git clone https://github.com/Jelloge/Deadlock-Rich-Presence.git
cd Deadlock-Rich-Presence
pip install -r requirements.txt
cd src
python main.py
```

Requires Python 3.10+. To build a standalone executable:
```bash
pip install pyinstaller
python build.py
```
Output: `dist/DeadlockRPC.exe` (Windows) or `dist/DeadlockRPC` (Linux)

</details>

## How It Works

DeadlockRPC monitors Deadlock's `console.log` file (written when the game runs with `-condebug`). It parses log events using regex patterns that I painstakingly mapped out to detect game state changes and pushes updates to Discord.

The game's runtime and memory are never touched. VAC-safe and won't affect performance.

## Disclaimer

Your antivirus MAY flag this application as malware. This is a known issue w/ executables bundled with PyInstaller, which packages Python applications into standalone .exe files. I get it if the detection concerns you. In that case, you can build the application from source!

## Changelog

- **Auto-Update** The app checks GitHub for new releases on startup and prompts you to update
- **Linux Support** Full Linux support via Proton. Game detection, Steam library paths, and system tray all work on Linux
- **Dynamic Hero Data** Integrates with `deadlock-api.com`. Hero names are fetched automatically so new heroes work instantly without manual code updates
- **Hideout Text** Your presence now displays hero-specific flavour text in the hideout (e.g., *"Mixing Drinks in the Hideout"* for Infernus)
- **Fixed Hero Detection** Hero now correctly updates when entering a match. The hideout hero is cleared on match entry so the actual in-match hero is shown. Also fixed hero swapping in Sandbox
- **Fixed Match Detection** Fixed standard and Street Brawl matches being misclassified as Bot Match due to placeholder bots loading before all players connect
- **Party Tracking** Real party size tracking using GC party events. Party size now reflects actual members instead of being capped at 2
- **Steam Path Detection** Added Windows Registry lookup so the app finds Deadlock regardless of where Steam is installed

## Future Changes

- Upload new unreleased hero assets to the Discord app (names work via API, but images still require manual Dev Portal uploads)
- Localization

## Known Bugs

Please open an issue if you encounter any bugs.

## Support

If you need help, message me on Discord : boba