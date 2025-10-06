import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime
import time

# --- تنظیمات API ---
API_CURRENCY = "https://api.alanchand.com/?type=currencies&token=OHt1R0mKruA6tGysczCy"
API_GOLD = "https://api.alanchand.com/?type=golds&token=OHt1R0mKruA6tGysczCy"

CURRENCY_SYMBOLS = {"usd", "eur"}
GOLD_SYMBOLS = {"abshodeh", "geram18", "sekkeh", "nim", "rob", "gerami"}

# --- اتصال به Google Sheets ---
SCOPE = ["https://www.googleapis.com/auth/spreadsheets"]

# مسیر فایل JSON در root repository
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "realtimeprices-474213-8bedc97f8515.json", SCOPE
)
client = gspread.authorize(creds)

SHEET_NAME = "CurrencyGoldPrices"
sheet = client.open(SHEET_NAME).sheet1

# --- تابع برای گرفتن داده‌ها ---
def fetch_data():
    rows = []

    # دریافت ارزها
    try:
        res_currency = requests.get(API_CURRENCY)
        data_currency = res_currency.json()
        for symbol, info in data_currency.items():
            if symbol in CURRENCY_SYMBOLS:
                rows.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    symbol,
                    info.get("name", symbol),
                    info.get("sell", 0)
                ])
    except Exception as e:
        print("❌ خطا در دریافت ارز:", e)

    # دریافت طلاها
    try:
        res_gold = requests.get(API_GOLD)
        data_gold = res_gold.json()
        for symbol, info in data_gold.items():
            if symbol in GOLD_SYMBOLS:
                rows.append([
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    symbol,
                    info.get("name", symbol),
                    info.get("price", 0)
                ])
    except Exception as e:
        print("❌ خطا در دریافت طلا:", e)

    return rows


# --- حلقه اصلی برای ذخیره لحظه‌ای ---
REFRESH_SECONDS = 60  # فاصله زمانی بین رفرش داده‌ها

print("شروع ذخیره داده‌ها در Google Sheet...")

# اطمینان از وجود عنوان ستون‌ها
sheet.update("A1:D1", [["Timestamp", "Symbol", "Name", "Price"]])

while True:
    data = fetch_data()
    if not data:
        print("⚠️ داده‌ای دریافت نشد، تلاش مجدد بعداً...")
        time.sleep(REFRESH_SECONDS)
        continue

    # پاک کردن داده‌های قبلی (ردیف‌های بعد از عنوان)
    sheet.batch_clear(["A2:D1000"])

    # نوشتن داده‌های جدید
    sheet.update(f"A2:D{len(data)+1}", data)

    print(f"✅ {len(data)} ردیف جدید جایگزین شد در {datetime.now().strftime('%H:%M:%S')}")
    time.sleep(REFRESH_SECONDS)
