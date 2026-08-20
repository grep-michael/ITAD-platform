import urllib,os,json,logging
import urllib.request
import urllib.error
from Utilities.Config import Config
from Utilities.Utils import GetSerial

def send_discord_webhook(url: str, embeds: list[dict]) -> None:
    data = json.dumps({"embeds": embeds}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json","User-Agent": "ITADPlatform/1.0"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status != 204:
                logging.info(f"Unexpected status: {resp.status}")
                #raise RuntimeError(f"Unexpected status: {resp.status}")
    except urllib.error.HTTPError as e:
        logging.info(f"Webhook failed: {e.code} {e.reason}")
        logging.info(e.read().decode("utf-8"))
        #raise RuntimeError(f"Webhook failed: {e.code} {e.reason}")

def SendDiscordSuccess(title: str, message: str, fields:list = []) -> None:
    fields.append({"name": "Tech ID", "value": Config.TECH_ID})
    send_discord_webhook(Config.WEBHOOK, [{
        "title": "✅ " + title,
        "description": message,
        "color": 0x2ECC71,
        "fields": fields
    }])


def SendDiscordError(title: str, message: str, fields:list = []) -> None:
    fields.append({"name": "Tech ID", "value": Config.TECH_ID})
    send_discord_webhook(Config.WEBHOOK, [{
        "title": "❌ " + title,
        "description": message,
        "color": 0xE74C3C,
        "fields": fields
    }])

import urllib.request
def AuditLogPost(status, **fields):
    host = Config.LOGGER_URL
    url = f"http://{host}:8080/api/machines"
    serial = GetSerial()
    body = json.dumps({"serial": serial, "status": status, "fields": fields}).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    with urllib.request.urlopen(req, timeout=5) as res:
        return json.load(res)