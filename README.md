# LG Service Menu (no service remote needed)

Open the hidden **IN-START service menu** on an LG webOS TV from your PC, over your home network.
No IR service remote is needed.

The main reason to do this is to switch off **ASBL** (Automatic Static Brightness Limiter), the feature that makes dark, slow movie scenes gradually get darker on LG OLEDs.

> **Tested on:** LG OLED **C1** (webOS 6), Windows 11, Python 3.14.
> Other LG webOS TVs (CX, C2, C3, G-series, etc.) use the same API and will likely work, but LG has blocked this on some firmware versions. See [Troubleshooting](#troubleshooting).

---

## ⚠️ Read this first

- **The service menu holds factory settings.** Changing the wrong value (region, "Tool Option", panel settings) can cause real problems, including a TV that needs a technician. **Only change the settings this guide names.**
- **Turning off ASBL/TPC raises burn-in risk.** It exists to protect the panel from static images. Fine for movies; be more careful if you leave static content (news tickers, game HUDs, a PC desktop) on screen for hours.
- **Warranty:** LG may refuse a burn-in claim if service settings were changed.
- **Never run Panel Refresh / "OLED Off-RS" manually** from the service menu.

You use this entirely at your own risk.

---

## What it does

LG webOS TVs expose a local control API (WebSocket, ports 3000/3001). The LG ThinQ app, Home Assistant and ColorControl use it to change inputs, volume and so on.

This script:

1. **Connects** to the TV at the IP you give it.
2. **Pairs** the first time: the TV shows a prompt and you accept it with your remote. A pairing key is saved to `~/.lg_service_menu_keys.json`, so you won't be asked again.
3. **Asks the TV to launch its built-in factory app** (`com.webos.app.factorywin`) in IN-START mode. This is the same thing pressing **IN-START** on an LG service remote does.

The script does **not** change any settings itself. It only opens the menu, and you make the changes on the TV with your normal remote.

It uses [`aiowebostv`](https://github.com/home-assistant-libs/aiowebostv), the open-source LG library from the Home Assistant project.

---

## Requirements

- An LG webOS TV on the **same network** as your PC.
- **Python 3.10+** ([python.org](https://www.python.org/downloads/))
- On the TV, network control must be allowed. This is on by default. If connecting fails, check
  **Settings → General → Devices → External Devices → TV On With Mobile / "LG Connect Apps"** (the name varies by model) and turn it **On**.

---

## Installation

```bash
git clone https://github.com/galbantow/lg-service-remove.git
cd lg-service-remove
python -m pip install -r requirements.txt
```

### Find your TV's IP address

On the TV: **Settings → General → Network → (Wired / Wi-Fi Connection) → Advanced Settings**. You'll see an address like `192.168.1.13`.

Tip: give the TV a fixed IP (a DHCP reservation in your router) so it doesn't change.

---

## Usage

```bash
python lg_service_menu.py <TV_IP>
```

Example:

```bash
python lg_service_menu.py 192.168.1.13
```

| Command | What it does |
|---|---|
| `python lg_service_menu.py 192.168.1.13` | Pair if needed, then open the IN-START menu |
| `python lg_service_menu.py 192.168.1.13 --pair-only` | Only pair and save the key (doesn't open the menu) |
| `python lg_service_menu.py 192.168.1.13 --forget` | Delete the saved pairing key for that TV |
| `python lg_service_menu.py 192.168.1.13 --key-file mykeys.json` | Store keys somewhere else |

**First run:** the TV shows a pairing prompt. Press **Accept** on the Magic Remote within about 30 seconds.

Expected output:

```
Connecting to 192.168.1.13 using saved pairing key...
Connected.
Sending IN-START service menu command...
TV accepted the command. The IN-START menu should now be on screen.
If it asks for a password, enter 0413 with your remote.
```

> **Note:** If the TV accepts the command but nothing shows, **run the script again**. Sending it a few times is harmless.

---

## Disabling ASBL (dark scenes getting darker)

Once the **IN-START** menu is on screen, use the **Magic Remote** arrows and OK:

1. If prompted for a password, enter **`0413`**.
2. Go to **OLED**.
3. Set **TPC Enable → Off**. *(This is ASBL.)*
4. *(Optional)* Set **GSR Enable → Off**. *(See below. You may want to leave this on.)*
5. **Don't change anything else.**
6. Press **Back / Exit** until the menu closes.
7. **Turn the TV off and on** so the change takes effect.

**Check it worked:** pause a dark movie scene for 30–60 seconds. The picture should no longer slowly dim.

### What TPC and GSR are

| Setting | Full name | What it does | Recommendation |
|---|---|---|---|
| **TPC** | Temporal Peak luminance Control | The ASBL itself: dims the **whole screen** when the picture stays mostly unchanged for a while. This is what darkens slow, dark movie scenes. | **Off** for movie watching |
| **GSR** | Global Sticky Reduction | Watches for **static elements that "stick"** over long periods (channel logos, game HUDs, taskbars) and lowers brightness to reduce wear. Its exact behaviour isn't well documented. | Leave **On** if you game, use it as a PC monitor or watch channels with fixed logos. Turn **Off** only if you still notice dimming after disabling TPC. |

Not to be confused with **ABL** (Automatic Brightness Limiter). ABL limits brightness on very bright full-screen images, is part of how the panel works, and **can't be disabled**. It's also not the problem in dark scenes.

> Firmware updates can turn TPC back on. If the dimming returns, run the script again and re-check the setting.

---

## Other settings worth checking (normal menu, no service menu needed)

These are in the regular **Settings** menu, and none of them affect panel safety:

| Setting | Recommended | Why |
|---|---|---|
| Picture Mode (SDR) | **Filmmaker Mode** | Most accurate to how the film was mastered |
| Picture Mode (HDR10) | **Filmmaker Mode** or **Cinema** | |
| Picture Mode (Dolby Vision) | **Cinema Home** (bright room) / **Cinema** (dark room) | |
| Peak Brightness (HDR) | **High** | Brighter highlights |
| Dynamic Tone Mapping (HDR10) | **On** (punchier) or **HGIG/Off** (accurate) | Personal preference |
| Dynamic Contrast | **Off** | Can crush shadow detail |
| Black Level | **Auto** | Match your source if shadows look grey or crushed |
| Noise Reduction / MPEG NR | **Off** for good sources | Avoids smearing fine detail |
| Smooth Gradation | **Low** | Reduces banding in dark scenes and skies |
| TruMotion | **Off** or **Cinematic Movement** | Avoids the "soap opera" effect |
| Real Cinema | **On** | Correct 24 fps cadence for films |
| Energy Saving | **Off** | Another source of dimming |
| AI Brightness / AI Picture Pro | **Off** | Stops automatic picture changes |
| Digital Sound Out (with eARC soundbar/AVR) | **Passthrough** | Sends Atmos etc. untouched |

**Burn-in care with TPC off:** keep **Logo Luminance Adjustment** (OLED Care) on, let the TV run its automatic panel refresh (leave it in standby, plugged in), and now and then check a grey screen for image retention.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Could not connect/pair` | TV must be **on** and on the same network. Check the IP. Make sure "LG Connect Apps" / mobile TV-on is enabled. Accept the prompt on the TV. |
| No pairing prompt appears | Run with `--forget`, then run again. The prompt can be hidden if another app is in full screen; press Home first. |
| `TV accepted the command` but nothing appears | Run it again (see the note above). If it never appears, your firmware likely blocks network access to the service menu. Use an **LG In-Start service remote** (about $10–15 online) instead. |
| `Command failed ... 404 no such service` | Your firmware doesn't expose the factory app over the network. Use a service remote. |
| Menu asks for a password | **`0413`**. Some older models use `0000`. |
| Dimming came back | A firmware update probably re-enabled TPC. Run the script and turn it off again. |

### Other ways into the service menu

- **LG In-Start service remote** (IR). Works on any firmware.
- **Android phone with an IR blaster** plus an IR remote app that has the LG IN-START code.
- **[ColorControl](https://github.com/Maassoft/ColorControl)** (Windows), which has similar features in its LG Expert menu.

> Holding **Settings** on the Magic Remote and entering `1105` opens the **Installation (Hotel) Menu**, *not* the service menu. It has no TPC option. Don't change hotel-mode settings.

---

## Files

| File | Purpose |
|---|---|
| `lg_service_menu.py` | The script |
| `requirements.txt` | Python dependency (`aiowebostv`) |
| `~/.lg_service_menu_keys.json` | Created on first run. Holds your TV's pairing key (kept outside the repo; don't share it) |

---

## Disclaimer

Not affiliated with or endorsed by LG Electronics. "LG" and "webOS" are trademarks of their respective owners. This tool only opens a menu built into the TV; any changes you make in it are your responsibility.
