import urllib,os,json

def send_discord_webhook(url: str, embeds: list[dict]) -> None:
    data = json.dumps({"embeds": embeds}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            if resp.status != 204:
                raise RuntimeError(f"Unexpected status: {resp.status}")
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Webhook failed: {e.code} {e.reason}")

def SendDiscordSuccess(title: str, message: str, fields:list = []) -> None:
    fields.append({"TECHID",os.getenv("TECH_ID")})
    send_discord_webhook(os.getenv("WEBHOOK"), [{
        "title": f"✅ {title}",
        "description": message,
        "color": 0x2ECC71,
        "fields": fields
    }])


def SendDiscordError(title: str, message: str, fields:list = []) -> None:
    fields.append({"TECHID",os.getenv("TECH_ID")})
    send_discord_webhook(os.getenv("WEBHOOK"), [{
        "title": f"❌ {title}",
        "description": message,
        "color": 0xE74C3C,
        "fields": fields
    }])
    