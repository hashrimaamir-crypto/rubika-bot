from pyrubi import Client
import datetime

SOURCE_GUIDS = [
    "c0BfWAy021c09b3fc4a6434c36c1be49",
    "c0hcam05b50a3f2a120c707733124b4c",
    "c0C19TD0c1f172db04742816671b15f1",
    "c0CrTQF00f821681d3fd575377059ce0",
    "c0BIfGD06bd7c27fb90b8002d082deae",
    "c0T34w0337a4466d88b96e909364cab0",
    "c0BNcv80384727059880921b7b95845d",
    "c0CcUB50d889cea99378115cf9404d5b"
]
TARGET_GUID = "c0Kidu021945dd23ce5ee1a83b16ab9a"
SEARCH_KEYWORD = "sharjikaaa"
LOG_PATH = "/storage/emulated/0/forwarder.log"
FORWARDED_IDS_PATH = "/storage/emulated/0/forwarded_today.txt"

client = Client("mySelf")

def log(msg):
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def save_forwarded_id(msg_id):
    try:
        with open(FORWARDED_IDS_PATH, "a", encoding="utf-8") as f:
            f.write(str(msg_id) + "\n")
    except Exception as e:
        log(f"[ERROR] ذخیره آیدی فوروارد: {e}")

def check_channels_and_forward():
    log("🚀 شروع بررسی کانال‌ها برای پیام‌های امروز...")
    today = datetime.date.today()

    for guid in SOURCE_GUIDS:
        try:
            try:
                client.join_chat(guid)
                log(f"[join] جوین به {guid} موفق بود.")
            except Exception as e:
                log(f"[warn] جوین به {guid} ممکن نبود: {e}")

            raw = client.get_messages(guid, limit=50)
            msgs = raw["messages"] if isinstance(raw, dict) and "messages" in raw else raw
            if not isinstance(msgs, list):
                continue

            found = None
            for msg in msgs:
                text = msg.get("text", "") or ""
                if SEARCH_KEYWORD.lower() not in text.lower():
                    continue

                # زمان پیام
                t = msg.get("time") or msg.get("date") or msg.get("message_date")
                if not t:
                    continue
                try:
                    msg_date = datetime.datetime.fromtimestamp(int(float(t))).date()
                except:
                    continue

                if msg_date == today:
                    found = msg
                    break

            if not found:
                log(f"[warn] پیام امروز با '{SEARCH_KEYWORD}' در {guid} نبود.")
                continue

            msg_id = found.get("message_id")
            client.forward_messages(guid, [msg_id], TARGET_GUID)
            log(f"[✅] پیام از {guid} فوروارد شد ({msg_id}).")
            save_forwarded_id(msg_id)

        except Exception as e:
            log(f"[FATAL] خطا در {guid}: {e}")

    log("🏁 بررسی و فوروارد تموم شد.")

# اجرای اصلی
log("تست اتصال...")
try:
    client.send_text(TARGET_GUID, "🤖 ربات فعال شد (فقط پیام‌های امروز فوروارد می‌شوند).")
except Exception as e:
    log(f"[ERROR] پیام تست: {e}")

check_channels_and_forward()
client.run()
