import os
import threading
import telebot
import subprocess
from flask import Flask, request
from playwright.sync_api import sync_playwright

# ✅ تثبيت Playwright والمتصفحات تلقائيًا عند بدء التشغيل
try:
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print(f"❌ خطأ أثناء تثبيت Playwright: {e}")

# ✅ إعدادات بوت تيليجرام
BOT_TOKEN = os.getenv("BOT_TOKEN")  # قراءة التوكن من المتغير البيئي
if not BOT_TOKEN:
    print("❌ لم يتم العثور على توكن البوت. تأكد من إضافته كمتغير بيئي.")
bot = telebot.TeleBot(BOT_TOKEN)

app = Flask(__name__)

# ✅ إعداد رؤوس الطلبات لمنع TikTok من الحظر
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Referer": "https://www.tiktok.com/",
    "Accept-Language": "en-US,en;q=0.9"
}

@app.route('/get_tiktok_info', methods=['GET'])
def get_tiktok_info():
    """ يجلب معلومات حساب تيك توك باستخدام Playwright """
    username = request.args.get("username")
    if not username:
        return {"error": "يرجى إدخال اسم المستخدم"}, 400

    tiktok_url = f"https://www.tiktok.com/@{username}"
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(tiktok_url, timeout=15000)

            # استخراج البيانات
            username_real = page.inner_text("h1[data-e2e='user-title']")
            user_id = page.inner_text("div[data-e2e='user-unique-id']")
            followers = page.inner_text("strong[data-e2e='followers-count']")
            following = page.inner_text("strong[data-e2e='following-count']")
            likes = page.inner_text("strong[data-e2e='likes-count']")
            videos = page.inner_text("span[data-e2e='video-count']")
            verified = "نعم" if page.query_selector("span[data-e2e='verified-badge']") else "لا"
            private = "نعم" if page.query_selector("div[data-e2e='private-account-badge']") else "لا"

            metadata = requests.get(f"https://www.tiktok.com/node/share/user/@{username}", headers=HEADERS).json()
            country = metadata.get("userInfo", {}).get("user", {}).get("region", "غير معروف")
            language = metadata.get("userInfo", {}).get("user", {}).get("language", "غير معروف")
            creation_time = metadata.get("userInfo", {}).get("user", {}).get("createTime", "غير معروف")
            bio = metadata.get("userInfo", {}).get("user", {}).get("signature", "لا يوجد")

            browser.close()

            return {
                "username": username,
                "real_name": username_real,
                "id": user_id,
                "followers": followers,
                "following": following,
                "likes": likes,
                "videos": videos,
                "verified": verified,
                "private": private,
                "country": country,
                "language": language,
                "creation_time": creation_time,
                "bio": bio,
                "profile_url": tiktok_url
            }
    except Exception as e:
        return {"error": f"❌ خطأ أثناء جلب البيانات: {e}"}, 500

# ✅ تشغيل البوت
def start_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    print(f"✅ تشغيل Flask على Render")
    threading.Thread(target=start_bot, daemon=True).start()
    app.run(host="0.0.0.0", port=8080, debug=True, use_reloader=False)
