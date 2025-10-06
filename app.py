import requests
from pyairtable import Table
from datetime import datetime
import streamlit as st
import time

# ====== تنظیمات Airtable ======
AIRTABLE_API_KEY = "patRr6OVKGHn2Zyin.f779b21d2982f5d752d8f596220d3c55653851fe3b5d0e17e58813d3bec04474"
BASE_ID = "appBh5G9yDkiqBAkd"
TABLE_NAME = "tblVEZtxVsSXgOREF"

table = Table(AIRTABLE_API_KEY, BASE_ID, TABLE_NAME)

# ====== API URLs ======
API_CURRENCIES = "https://api.alanchand.com/?type=currencies&token=OHt1R0mKruA6tGysczCy"
API_GOLDS = "https://api.alanchand.com/?type=golds&token=OHt1R0mKruA6tGysczCy"

# ====== Symbols to extract ======
CURRENCIES_TO_KEEP = ["USD", "EUR"]
GOLDS_TO_KEEP = ["Abshodeh", "18ayar", "Sekkeh", "Nim", "Rob"]

# ====== Streamlit UI ======
st.title("Sync API Data to Airtable (Auto-refresh every 1 minute)")

status_text = st.empty()  # برای نمایش وضعیت
counter = st.empty()      # برای نمایش شمارشگر

def fetch_api(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def sync_data():
    try:
        # گرفتن داده‌ها
        currencies_data = fetch_api(API_CURRENCIES)
        golds_data = fetch_api(API_GOLDS)

        # ترکیب داده‌ها
        records_to_insert = []

        for item in currencies_data:
            symbol = item.get("symbol")
            if symbol in CURRENCIES_TO_KEEP:
                records_to_insert.append({
                    "timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "Name": item.get("name"),
                    "Price": item.get("price")
                })

        for item in golds_data:
            symbol = item.get("symbol")
            if symbol in GOLDS_TO_KEEP:
                records_to_insert.append({
                    "timestamp": datetime.now().isoformat(),
                    "symbol": symbol,
                    "Name": item.get("name"),
                    "Price": item.get("price")
                })

        # پاک کردن رکوردهای قبلی
        existing_records = table.all()
        for rec in existing_records:
            table.delete(rec['id'])

        # اضافه کردن رکوردهای جدید
        for record in records_to_insert:
            table.create(record)

        status_text.success(f"{len(records_to_insert)} رکورد جدید وارد Airtable شد.")
    except Exception as e:
        status_text.error(f"خطا: {e}")

# ====== حلقه رفرش هر 1 دقیقه ======
while True:
    sync_data()
    for i in range(60, 0, -1):
        counter.text(f"رفرش بعدی در: {i} ثانیه")
        time.sleep(1)
