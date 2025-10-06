import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from datetime import datetime
import time
import streamlit as st

st.title("📊 ذخیره لحظه‌ای قیمت ارز و طلا در Google Sheet")

# --- تنظیمات API ---
API_CURRENCY = "https://api.alanchand.com/?type=currencies&token=OHt1R0mKruA6tGysczCy"
API_GOLD = "https://api.alanchand.com/?type=golds&token=OHt1R0mKruA6tGysczCy"

CURRENCY_SYMBOLS = {"usd", "eur"}
GOLD_SYMBOLS = {"abshodeh", "geram18", "sekkeh", "nim", "rob", "gerami"}

# --- اتصال به Google Sheets ---
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# مسیر فایل JSON داخل repository
JSON_FILE = "realtimeprices-474213-8bedc97f8515.json"

creds = ServiceAccountCredentials.from_json_keyfile_name(JSON_FILE, SCOPE)
client = gspread.authorize(creds)

SHEET_NAME = "CurrencyGoldPrices"
sheet = client.open(SHEET_NAME).sheet1

# --- تابع دریافت داده‌ها ---
def fetch_data():
    rows = []

    try:
        res_currency = requests.get(API_CURRENCY)
        data_currency = res_currency.json()
        for symbol, info in data_currency.items():
            if symbol in CURRENCY_SYMBOLS:
                rows.append([symbol, info.get("name", symbol), info.get("sell", 0)])
    except Exception as e:
        st.error(f"خطا در دریافت ارز: {e}")

    try:
        res_gold = requests.get(API_GOLD)
        data_gold = res_gold.json()
        for symbol, info in data_gold.items():
            if symbol in GOLD_SYMBOLS:
                rows.append([symbol, info.get("name", symbol), info.get("price", 0)])
    except Exception as e:
        st.error(f"خطا در دریافت طلا: {e}")

    return rows

REFRESH_SECONDS = 60

st.write("اپلیکیشن در حال اجراست... هر 60 ثانیه داده‌ها به Google Sheet آپدیت می‌شوند.")

# --- حلقه Streamlit ---
while True:
    data = fetch_data()
    if data:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # پاک کردن داده‌های قبلی
        sheet.clear()

        # نوشتن header
        sheet.append_row(["timestamp", "symbol", "name", "price"])

        # نوشتن داده‌ها
        for item in data:
            sheet.append_row([timestamp, item[0], item[1], item[2]])

        st.write(f"{len(data)} ردیف ذخیره شد در {timestamp}")
    else:
        st.warning("هیچ داده‌ای دریافت نشد.")

    time.sleep(REFRESH_SECONDS)
