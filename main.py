from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>🚀 البروكسي يعمل بنجاح</title></head>
    <body>
    <h2>✅ تم تشغيل Flask على استضافة Render!</h2>
    <p>🌍 رابط الوصول: <a href='/'>Your Render App Link</a></p>
    </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)  # Render يحدد المنفذ تلقائيًا
