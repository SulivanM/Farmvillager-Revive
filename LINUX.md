# Linux (FarmVille Revive)

:warning: To play on GNU/Linux, you must run the server from source.

## Requirements

- **Python 3.14+**: This version is optimized for modern Python.
- **Browser with Flash support**: See [Flash Chromium browser](#flash-chromium-browser).
- **Adobe Flash Player**: See [Flash Player for Linux Pepper](#flash-player-for-linux-pepper).
- **Assets**: The server will automatically download the 17 GB of assets from [cdnalpha.ttron.eu](https://cdnalpha.ttron.eu/production/farmvillage/) on the first launch.

## Quick Start

1. Clone the repo: `git clone https://github.com/SulivanM/Farmvillager-Revive`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `python server.py`

## Flash Chromium browser

Download a Chromium version with PPAPI support.
<br>Tested with version *86.0.4240.75*, which can be downloaded [here](https://chromium.cypress.io/linux/stable/86.0.4240.75).

## Flash Player for Linux Pepper

Download `flashplayer32_0r0_371_linuxpep.x86_64.tar.gz` from the [32.0.0.371 archive](https://archive.org/download/flashplayerarchive/pub/flashplayer/installers/archive/fp_32.0.0.371_archive.zip/).
<br>For 32-bit, download `flashplayer32_0r0_371_linuxpep.i386.tar.gz`.

Extract its contents to `/usr/lib/adobe-flashplugin`

## Running Chromium with PPAPI Flash

Run the chrome binary with `--ppapi-flash-path=/usr/lib/adobe-flashplugin/libpepflashplayer.so`
<br>and `--ppapi-flash-version=32.0.0.371` flags.

*Note:* To avoid providing those flags every time, you can set the `CHROMIUM_FLAGS` environment variable.
