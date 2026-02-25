import requests, os, time, json

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
PRICE_FILE = "last_price.json"

def get_silver_price():
    url = "https://webapi.charisma.ir/api/Plan/plan-calculator-info-by-id?planId=04689a46-3eff-45d4-a070-f83f7d4d20d8"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cache-Control": "no-cache, no-store",
        "Pragma": "no-cache",
    }
    # اضافه کردن timestamp به URL تا کش نخونه
    r = requests.get(url, headers=headers, params={"_t": int(time.time())}, timeout=10)
    raw_price = r.json()['lastPrice']
    return round(raw_price / 10, 0)

def load_last_price():
    if os.path.exists(PRICE_FILE):
        with open(PRICE_FILE, "r") as f:
            return json.load(f).get("price")
    return None

def save_last_price(price):
    with open(PRICE_FILE, "w") as f:
        json.dump({"price": price}, f)

def send_to_telegram(price, old_price=None):
    if old_price:
        change = price - old_price
        emoji = "📈" if change > 0 else "📉"
        msg = (
            f"{emoji} قیمت هر گرم : "
            f"{price:,.0f} تومان\n"
        )
    else:
        msg = f"💰 شروع ربات - قیمت نقره: {price:,.0f} تومان"

    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={"chat_id": CHAT_ID, "text": msg}
    )

print("✅ ربات شروع به کار کرد...")

while True:
    try:
        price = get_silver_price()
        last_price = load_last_price()

        if price != last_price:
            send_to_telegram(price, last_price)
            save_last_price(price)
            print(f"✅ قیمت جدید: {price:,.0f}")
        else:
            print(f"🔄 تغییری نبود: {price:,.0f}")

    except Exception as e:
        print(f"❌ خطا: {e}")

    time.sleep(20)  # هر 3 ثانیه


