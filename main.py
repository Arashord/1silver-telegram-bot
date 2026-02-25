import requests, os, time, json

# ════════════════════════════════════════════════════════
# 🎯 تنظیمات هشدار
TARGET_BUY_PRICE  = 525000
BUY_THRESHOLD     = 1000

TARGET_SELL_PRICE = 535000
SELL_THRESHOLD    = 1000
# ════════════════════════════════════════════════════════

PRICE_BOT = {
    "token": os.getenv("PRICE_BOT_TOKEN"),
    "chat": os.getenv("PRICE_CHAT_ID"),
}

ALERT_BOT = {
    "token": os.getenv("ALERT_BOT_TOKEN"),
    "chat": os.getenv("ALERT_CHAT_ID"),
}

PRICE_FILE = "last_price.json"
ALERT_FILE = "last_alert.json"

# ════════════════════════════════════════════════════════

def get_silver_price():
    url = "https://webapi.charisma.ir/api/Plan/plan-calculator-info-by-id"
    params = {
        "planId": "04689a46-3eff-45d4-a070-f83f7d4d20d8",
        "_t": int(time.time()),
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cache-Control": "no-cache, no-store",
        "Pragma": "no-cache",
    }
    r = requests.get(url, headers=headers, params=params, timeout=10)
    r.raise_for_status()
    return int(round(r.json()["lastPrice"] / 10, 0))


def send(bot, text):
    requests.post(
        f"https://api.telegram.org/bot{bot['token']}/sendMessage",
        json={"chat_id": bot["chat"], "text": text},
        timeout=10,
    )


def load_json(path):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f)


# ───────────────── قیمت لحظه‌ای (ربات 1) ─────────────────
def handle_price_bot(price):
    data = load_json(PRICE_FILE)
    last_price = data["price"] if data else None

    if price != last_price:
        emoji = "📈" if last_price and price > last_price else "📉"
        msg = f"{emoji} قیمت هر گرم : {price:,} تومان"
        send(PRICE_BOT, msg)
        save_json(PRICE_FILE, {"price": price})
        print("✅ قیمت لحظه‌ای ارسال شد")


# ───────────────── هشدارها (ربات 2) ─────────────────
def handle_alert_bot(price):
    data = load_json(ALERT_FILE)
    last_alert = data["price"] if data else None

    def alert(msg):
        send(ALERT_BOT, msg)
        save_json(ALERT_FILE, {"price": price})

    if price > TARGET_SELL_PRICE:
        diff = price - TARGET_SELL_PRICE
        if price != last_alert:
            alert(
                f"⚠️🟢 قیمت لحظه‌ای: {price:,} تومان\n"
                f"________________________________\n\n"
                f"⚠️🟢 هشدار: قیمت هدف فروش منقضی شد!\n\n"
                f"قیمت هدف فروش: {TARGET_SELL_PRICE:,} تومان\n"
                f"________________________________\n"
                f"اختلاف: {diff:,} تومان"
            )

    elif price < TARGET_BUY_PRICE:
        diff = TARGET_BUY_PRICE - price
        if price != last_alert:
            alert(
                f"⚠️🔴 قیمت لحظه‌ای: {price:,} تومان\n"
                f"________________________________\n\n"
                f"⚠️🔴 هشدار: قیمت هدف خرید منقضی شد!\n\n"
                f"قیمت هدف خرید: {TARGET_BUY_PRICE:,} تومان\n"
                f"________________________________\n"
                f"اختلاف: {diff:,} تومان"
            )

    elif abs(price - TARGET_BUY_PRICE) <= BUY_THRESHOLD and price != last_alert:
        alert(
            f"قیمت لحظه‌ای: {price:,} تومان\n"
            f"________________________________\n"
            f"📉 🔴 🛎 🔴 لحظه خرید\n"
            f"قیمت هدف خرید: {TARGET_BUY_PRICE:,} تومان\n"
            f"________________________________\n"
            f"اختلاف: {abs(price - TARGET_BUY_PRICE):,} تومان"
        )

    elif abs(price - TARGET_SELL_PRICE) <= SELL_THRESHOLD and price != last_alert:
        alert(
            f"قیمت لحظه‌ای: {price:,} تومان\n"
            f"________________________________\n"
            f"📈 🟢 🛎 🟢 لحظه فروش\n"
            f"قیمت هدف فروش: {TARGET_SELL_PRICE:,} تومان\n"
            f"________________________________\n"
            f"اختلاف: {abs(price - TARGET_SELL_PRICE):,} تومان"
        )


# ════════════════════════════════════════════════════════
print("✅ ربات دوگانه نقره شروع شد...")

while True:
    try:
        price = get_silver_price()
        print(f"💰 قیمت: {price:,}")
        handle_price_bot(price)
        handle_alert_bot(price)
    except Exception as e:
        print(f"❌ خطا: {e}")

    time.sleep(20)


