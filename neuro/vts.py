"""Lip sync: tell VTube Studio how wide to open the mouth, through its plugin API.

The first time this runs, VTube Studio shows a popup asking to allow the plugin. Click Allow.
The token is then saved so you only have to do it once.
"""

import json
import uuid
from pathlib import Path

from websockets.sync.client import connect

import config

PLUGIN_NAME = "Neuro Voice Lip Sync"
PLUGIN_DEVELOPER = "Neuro-Sama-Project"


class VTubeStudio:
    def __init__(self):
        self.ws = None

    def _request(self, message_type: str, data: dict | None = None) -> dict:
        self.ws.send(json.dumps({
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": uuid.uuid4().hex,
            "messageType": message_type,
            "data": data or {},
        }))
        response = json.loads(self.ws.recv())
        if response.get("messageType") == "APIError":
            raise RuntimeError(response["data"].get("message", "VTube Studio API error"))
        return response.get("data", {})

    def connect(self) -> bool:
        """Connect and authenticate. Returns False (and keeps going without lip sync) on failure."""
        try:
            self.ws = connect(config.VTS_URL, open_timeout=3)
        except OSError:
            print(
                f"VTube Studio not found at {config.VTS_URL}. Lip sync is off.\n"
                "  (In VTube Studio: Settings > 'Start API' must be on.)"
            )
            return False

        plugin = {"pluginName": PLUGIN_NAME, "pluginDeveloper": PLUGIN_DEVELOPER}
        token_file = Path(config.VTS_TOKEN_FILE)
        try:
            for attempt in range(2):
                if not token_file.exists():
                    print("Check VTube Studio and click 'Allow' on the plugin popup...")
                    token = self._request("AuthenticationTokenRequest", plugin)["authenticationToken"]
                    token_file.write_text(token)
                auth = self._request(
                    "AuthenticationRequest",
                    {**plugin, "authenticationToken": token_file.read_text().strip()},
                )
                if auth.get("authenticated"):
                    print("Connected to VTube Studio.")
                    return True
                token_file.unlink()  # Token was revoked; ask for a new one.
        except (RuntimeError, OSError) as e:
            print(f"VTube Studio refused the connection ({e}). Lip sync is off.")
        self.close()
        return False

    def set_mouth(self, value: float):
        if not self.ws:
            return
        try:
            self._request("InjectParameterDataRequest", {
                "faceFound": False,
                "mode": "set",
                "parameterValues": [
                    {"id": config.VTS_MOUTH_PARAMETER, "value": max(0.0, min(1.0, value))}
                ],
            })
        except (RuntimeError, OSError) as e:
            print(f"Lost VTube Studio connection ({e}). Lip sync is off.")
            self.close()

    def close(self):
        if self.ws:
            self.ws.close()
            self.ws = None
