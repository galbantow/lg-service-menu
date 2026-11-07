"""Open the hidden service menu (IN-START) on an LG webOS TV over the network.

No service remote needed. The script talks to the TV's local control API
(the same one the LG ThinQ app and Home Assistant use), pairs once, and then
asks the TV to launch its factory/service app in IN-START mode.

Usage:
    python lg_service_menu.py <TV_IP>              # pair if needed, open IN-START
    python lg_service_menu.py <TV_IP> --pair-only  # just pair and save the key
    python lg_service_menu.py <TV_IP> --forget     # delete the saved key

Tested on an LG OLED C1. Use at your own risk; see README.md.
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

try:
    from aiowebostv import WebOsClient
except ImportError:
    sys.exit(
        "Missing dependency 'aiowebostv'. Install it with:\n"
        "    python -m pip install -r requirements.txt"
    )

DEFAULT_KEY_FILE = Path.home() / ".lg_service_menu_keys.json"

SERVICE_APP_ID = "com.webos.app.factorywin"
INSTART_PARAMS = {"id": "executeFactory", "irKey": "inStart"}


def load_keys(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_keys(path: Path, keys: dict) -> None:
    path.write_text(json.dumps(keys, indent=2))


async def run(host: str, key_file: Path, pair_only: bool) -> int:
    keys = load_keys(key_file)
    client = WebOsClient(host, client_key=keys.get(host))

    if keys.get(host):
        print(f"Connecting to {host} using saved pairing key...")
    else:
        print(f"Connecting to {host}. Accept the pairing prompt on the TV with your remote...")

    try:
        await client.connect()
    except Exception as err:  # connection refused, timeout, pairing rejected...
        print(f"Could not connect/pair: {type(err).__name__}: {err}")
        print("Check the TV is on, on the same network, and that you accepted the prompt.")
        return 1

    if client.client_key and client.client_key != keys.get(host):
        keys[host] = client.client_key
        save_keys(key_file, keys)
        print(f"Paired. Key saved to {key_file}")
    else:
        print("Connected.")

    try:
        if pair_only:
            return 0
        print("Sending IN-START service menu command...")
        result = await client.launch_app_with_params(SERVICE_APP_ID, INSTART_PARAMS)
        if result.get("returnValue"):
            print("TV accepted the command. The IN-START menu should now be on screen.")
            print("If it asks for a password, enter 0413 with your remote.")
            return 0
        print(f"TV did not accept the command: {result}")
        return 1
    except Exception as err:
        print(f"Command failed: {type(err).__name__}: {err}")
        print("Your firmware may have blocked network access to the service menu.")
        return 1
    finally:
        await client.disconnect()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Open the IN-START service menu on an LG webOS TV over the network."
    )
    parser.add_argument("host", help="TV IP address, e.g. 192.168.1.13")
    parser.add_argument("--pair-only", action="store_true",
                        help="only pair with the TV and save the key")
    parser.add_argument("--forget", action="store_true",
                        help="delete the saved pairing key for this TV and exit")
    parser.add_argument("--key-file", type=Path, default=DEFAULT_KEY_FILE,
                        help=f"where pairing keys are stored (default: {DEFAULT_KEY_FILE})")
    args = parser.parse_args()

    if args.forget:
        keys = load_keys(args.key_file)
        if keys.pop(args.host, None):
            save_keys(args.key_file, keys)
            print(f"Removed saved key for {args.host}.")
        else:
            print(f"No saved key for {args.host}.")
        return 0

    return asyncio.run(run(args.host, args.key_file, args.pair_only))


if __name__ == "__main__":
    sys.exit(main())
