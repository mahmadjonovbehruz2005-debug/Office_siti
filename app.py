from flask import Flask, request, redirect, render_template_string, session, url_for, send_from_directory
import json
import os
import requests
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "lmk_secret_key_change_me")

# ===== ENV / PASSWORDS =====
PASSWORD = os.environ.get("PASSWORD", "Limak2026")
NILUFAR_PASSWORD = os.environ.get("NILUFAR_PASSWORD", "Nilufar2026")
FATMA_PASSWORD = os.environ.get("FATMA_PASSWORD", "Fatma2026")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Admin2026")

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
NILUFAR_CHAT_ID = os.environ.get("NILUFAR_CHAT_ID", "")
FATMA_CHAT_ID = os.environ.get("FATMA_CHAT_ID", "")

ORDERS_FILE = "web_orders.json"
COUNTER_FILE = "web_counter.txt"

BACK_RU = "Назад"
BACK_TR = "Geri"

TEXTS = {
    "ru": {
        "title": "LMK Заказ напитков",
        "password": "Введите пароль",
        "name": "Введите имя",
        "language": "Выберите язык",
        "floor": "Выберите этаж",
        "choose_chaynitsa": "Выберите чайницу",
        "office": "Выберите офис",
        "drink": "Выберите напиток",
        "tea_option": "Выберите добавку для чая",
        "coffee_option": "Выберите вариант кофе",
        "turk_sugar": "Выберите сахар для турецкого кофе",
        "qty": "Выберите количество",
        "more": "Добавить ещё или завершить заказ?",
        "submit": "Отправить",
        "add_more": "➕ Ещё",
        "finish": "✅ Всё",
        "wait": "⏳ Ваш заказ отправлен.",
        "accepted_user": "✅ Ваш заказ принят",
        "unavailable_user": "❌ К сожалению, этого сейчас нет",
        "lunch_user": "🍽 Официант сейчас на обеде. Пожалуйста, подождите и заказывайте позже.",
        "my_orders_empty": "Заказов пока нет.",
        "new_order": "Новый заказ",
        "panel_title": "Панель чайницы / администратора",
        "wrong_password": "❌ Неверный пароль",
        "telegram_sent": "📨 Заказ отправлен в Telegram",
        "telegram_failed": "⚠️ Заказ сохранён, но Telegram не отправился",
        "new_orders_only": "Только новые",
        "all_orders": "Все заказы",
        "orders_empty": "Заказов нет.",
        "hero_title": "LMK Order System",
        "hero_text": "Быстро • Удобно • Для офиса",
    },
    "tr": {
        "title": "LMK İçecek Siparişi",
        "password": "Şifreyi girin",
        "name": "Adınızı girin",
        "language": "Dil seçin",
        "floor": "Kat seçin",
        "choose_chaynitsa": "Çaycıyı seçin",
        "office": "Ofis seçin",
        "drink": "İçeceği seçin",
        "tea_option": "Çay için ek seçin",
        "coffee_option": "Kahve seçeneğini seçin",
        "turk_sugar": "Türk kahvesi için şeker seçin",
        "qty": "Adet seçin",
        "more": "Bir şey daha eklemek ister misiniz?",
        "submit": "Gönder",
        "add_more": "➕ Yine ekle",
        "finish": "✅ Bitti",
        "wait": "⏳ Siparişiniz gönderildi.",
        "accepted_user": "✅ Siparişiniz kabul edildi",
        "unavailable_user": "❌ Maalesef bu ürün şu anda yok",
        "lunch_user": "🍽 Garson şu anda öğle yemeğinde. Lütfen bekleyin ve daha sonra sipariş verin.",
        "my_orders_empty": "Henüz sipariş yok.",
        "new_order": "Yeni sipariş",
        "panel_title": "Çaycı / yönetici paneli",
        "wrong_password": "❌ Yanlış şifre",
        "telegram_sent": "📨 Sipariş Telegram'a gönderildi",
        "telegram_failed": "⚠️ Sipariş kaydedildi ama Telegram gönderilemedi",
        "new_orders_only": "Sadece yeni",
        "all_orders": "Tüm siparişler",
        "orders_empty": "Sipariş yok.",
        "hero_title": "LMK Order System",
        "hero_text": "Hızlı • Kolay • Ofis için",
    },
}

OFFICES = {
    "1 этаж": [
        "1 АДМИНИСТРАЦИЯ",
        "2 СЕРВЕРНАЯ",
        "3 ОТДЕЛ КАДРОВ",
        "4 Гранел 1",
        "5 Гранел 2",
        "6 Гранел 3",
        "7 ОТДЕЛ ОТ и ТБ",
        "8 ОТДЕЛ ГЕОДЕЗИИ",
        "9 НАЧАЛЬНИК СТРОИТЕЛЬСТВА",
        "10 ИНЖЕНЕРЫ УЧАСТКА / ПРОРАБЫ",
    ],
    "2 этаж": [
        "1 РУКОВОДИТЕЛЬ ПРОЕКТА",
        "2 ЗАЛ СОВЕЩАНИЙ",
        "3 ДИЗАЙН ОФИС",
        "4 СЕКРЕТАРША",
        "5 КООРДИНАТОР ЭЛЕКТРОМЕХАНИЧЕСКОЙ СИСТЕМЫ",
        "6 ОТДЕЛ МЕХАНИК & ЭЛЕКТРИК",
        "7 ПТО",
        "8 ГЛАВНЫЙ ИНЖЕНЕР ПРОЕКТА",
        "9 ОТДЕЛ СНАБЖЕНИЯ",
        "10 БУХГАЛТЕРИЯ & ЮРИДИЧЕСКИЙ ОТДЕЛ",
        "11 ТЕХНИЧЕСКИЙ ОТДЕЛ",
        "12 ЗАМЕСТИТЕЛЬ РУКОВОДИТЕЛЯ ПРОЕКТА",
    ],
    "1. kat": [
        "1 İDARİ İŞLER",
        "2 SERVER ODASI",
        "3 PERSONEL",
        "4 Granel 1",
        "5 Granel 2",
        "6 Granel 3",
        "7 İŞ GÜVENLİĞİ",
        "8 ÖLÇME İŞLERİ",
        "9 ŞANTİYE ŞEFİ",
        "10 SAHA EKİBİ",
    ],
    "2. kat": [
        "1 PROJE MÜDÜRÜ",
        "2 TOPLANTI ODASI",
        "3 DİZAYN OFİS",
        "4 SEKRETER",
        "5 MEKANİK & ELEKTRİK KOORDİNATÖRÜ",
        "6 MEKANİK & ELEKTRİK GRUBU",
        "7 PTO GRUBU",
        "8 GIP",
        "9 SATIN ALMA",
        "10 MUHASEBE & HUKUK",
        "11 TEKNİK OFİS DEPARTMANI",
        "12 PROJE MÜDÜR YARDIMCISI",
    ],
}


def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_counter():
    if os.path.exists(COUNTER_FILE):
        try:
            with open(COUNTER_FILE, "r", encoding="utf-8") as f:
                return int(f.read().strip())
        except Exception:
            return 1
    return 1


def save_counter(value):
    with open(COUNTER_FILE, "w", encoding="utf-8") as f:
        f.write(str(value))


orders = load_json(ORDERS_FILE, {})
order_counter = load_counter()


def get_lang():
    return session.get("language", "ru")


def t():
    return TEXTS[get_lang()]


def status_text(lang, status):
    if lang == "tr":
        return {
            "new": "⏳ Yeni",
            "accepted": "✅ Kabul edildi",
            "unavailable": "❌ Yok",
            "lunch": "🍽 Öğle yemeğinde",
        }.get(status, status)
    return {
        "new": "⏳ Новый",
        "accepted": "✅ Принят",
        "unavailable": "❌ Нет в наличии",
        "lunch": "🍽 На обеде",
    }.get(status, status)


def panel_status_message(lang, status):
    if status == "accepted":
        return TEXTS[lang]["accepted_user"]
    if status == "unavailable":
        return TEXTS[lang]["unavailable_user"]
    if status == "lunch":
        return TEXTS[lang]["lunch_user"]
    return status_text(lang, status)


def send_telegram_message(chat_id, text, reply_markup=None):
    if not BOT_TOKEN or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text}

    if reply_markup:
        data["reply_markup"] = json.dumps(reply_markup)

    try:
        response = requests.post(url, data=data, timeout=20)
        print("SEND RESPONSE:", response.text)
        return response.ok
    except Exception as e:
        print("SEND ERROR:", e)
        return False


def edit_telegram_message(chat_id, message_id, text):
    if not BOT_TOKEN:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText"
    data = {"chat_id": chat_id, "message_id": message_id, "text": text}

    try:
        response = requests.post(url, data=data, timeout=20)
        print("EDIT RESPONSE:", response.text)
        return response.ok
    except Exception as e:
        print("EDIT ERROR:", e)
        return False


def answer_callback_query(callback_query_id):
    if not BOT_TOKEN:
        return False

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, data={"callback_query_id": callback_query_id}, timeout=20)
        return True
    except Exception as e:
        print("CALLBACK ERROR:", e)
        return False


def get_target_chat_id(chaynitsa_value):
    if chaynitsa_value == "Nilufar":
        return NILUFAR_CHAT_ID
    return FATMA_CHAT_ID


@app.route("/logo")
def logo():
    return send_from_directory(".", "logo.jpg")


def render_page(title, body):
    hero_title = t()["hero_title"]
    hero_text = t()["hero_text"]

    return render_template_string("""
    <!doctype html>
    <html lang="{{ lang }}">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <link rel="icon" href="{{ url_for('logo') }}">
      <title>{{ title }}</title>
      <style>
        * {
          box-sizing: border-box;
        }

        body {
          font-family: Arial, sans-serif;
          margin: 0;
          padding: 0;
          color: #0f172a;
          background:
            radial-gradient(circle at top left, rgba(255, 99, 132, 0.18), transparent 30%),
            radial-gradient(circle at top right, rgba(59, 130, 246, 0.20), transparent 28%),
            radial-gradient(circle at bottom left, rgba(16, 185, 129, 0.20), transparent 30%),
            radial-gradient(circle at bottom right, rgba(245, 158, 11, 0.22), transparent 28%),
            linear-gradient(135deg, #f8fafc, #eef2ff, #ecfeff, #fdf2f8);
          min-height: 100vh;
          animation: bgMove 10s ease-in-out infinite alternate;
        }

        @keyframes bgMove {
          0% { background-position: left top, right top, left bottom, right bottom, center; }
          100% { background-position: left 20px top 10px, right 20px top 20px, left 15px bottom 15px, right 10px bottom 20px, center; }
        }

        .container {
          max-width: 760px;
          margin: 24px auto;
          padding: 20px;
          border-radius: 28px;
          background: rgba(255, 255, 255, 0.82);
          backdrop-filter: blur(18px);
          -webkit-backdrop-filter: blur(18px);
          border: 1px solid rgba(255,255,255,0.6);
          box-shadow:
            0 20px 50px rgba(15, 23, 42, 0.10),
            0 8px 20px rgba(59, 130, 246, 0.08),
            inset 0 1px 0 rgba(255,255,255,0.8);
          animation: pageIn 0.6s ease;
        }

        @keyframes pageIn {
          from {
            opacity: 0;
            transform: translateY(18px) scale(0.98);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }

        .logo-box {
          display: flex;
          align-items: center;
          gap: 14px;
          margin-bottom: 18px;
          padding-bottom: 14px;
          border-bottom: 1px solid rgba(148, 163, 184, 0.25);
        }

        .logo-box img {
          width: 56px;
          height: 56px;
          border-radius: 16px;
          object-fit: cover;
          box-shadow:
            0 8px 20px rgba(0,0,0,0.12),
            0 0 0 3px rgba(255,255,255,0.65);
          animation: floatLogo 3s ease-in-out infinite;
        }

        @keyframes floatLogo {
          0% { transform: translateY(0); }
          50% { transform: translateY(-3px); }
          100% { transform: translateY(0); }
        }

        .logo-title {
          font-size: 22px;
          font-weight: 800;
          background: linear-gradient(90deg, #0f766e, #2563eb, #9333ea, #e11d48, #f59e0b);
          background-size: 300% 300%;
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          animation: titleGlow 6s ease infinite;
        }

        @keyframes titleGlow {
          0% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
          100% { background-position: 0% 50%; }
        }

        .hero {
          height: 200px;
          border-radius: 24px;
          margin-bottom: 20px;
          position: relative;
          overflow: hidden;
          background-size: cover;
          background-position: center;
          animation: heroSlide 20s infinite;
          box-shadow: 0 15px 40px rgba(0,0,0,0.15);
        }

        .hero::after {
          content: "";
          position: absolute;
          inset: 0;
          background: linear-gradient(90deg, rgba(0,0,0,0.55), rgba(0,0,0,0.18), transparent);
        }

        .hero-text {
          position: absolute;
          left: 22px;
          bottom: 22px;
          z-index: 2;
          color: white;
          text-shadow: 0 2px 8px rgba(0,0,0,0.35);
        }

        .hero-text h1 {
          margin: 0;
          font-size: 28px;
          font-weight: 800;
        }

        .hero-text p {
          margin: 6px 0 0;
          font-size: 14px;
          opacity: 0.96;
        }

        @keyframes heroSlide {
          0%   { background-image: url("/static/images/bg1.jpg"); }
          25%  { background-image: url("/static/images/bg2.jpg"); }
          50%  { background-image: url("/static/images/bg3.jpg"); }
          75%  { background-image: url("/static/images/bg4.jpg"); }
          100% { background-image: url("/static/images/bg5.jpg"); }
        }

        h1, h2, h3 {
          margin-top: 0;
          margin-bottom: 16px;
          font-weight: 800;
          line-height: 1.2;
        }

        h2, h3 {
          font-size: 20px;
        }

        .btn {
          display: block;
          width: 100%;
          text-align: center;
          padding: 15px 16px;
          margin: 10px 0;
          border: none;
          border-radius: 18px;
          color: white;
          font-size: 16px;
          font-weight: 700;
          text-decoration: none;
          cursor: pointer;
          transition: all 0.22s ease;
          box-shadow: 0 10px 22px rgba(15, 23, 42, 0.10);
          background: linear-gradient(135deg, #0f766e, #14b8a6);
        }

        .btn:hover {
          transform: translateY(-3px) scale(1.02);
          box-shadow: 0 14px 28px rgba(15, 23, 42, 0.14);
          filter: brightness(1.04);
        }

        .btn:active {
          transform: translateY(0);
          box-shadow: 0 6px 12px rgba(15, 23, 42, 0.10);
        }

        .btn-secondary {
          background: linear-gradient(135deg, #475569, #64748b);
        }

        .btn-green {
          background: linear-gradient(135deg, #16a34a, #22c55e);
        }

        .btn-red {
          background: linear-gradient(135deg, #dc2626, #f43f5e);
        }

        .btn-orange {
          background: linear-gradient(135deg, #ea580c, #f59e0b);
        }

        input {
          width: 100%;
          padding: 13px 14px;
          border-radius: 16px;
          border: 1px solid rgba(148, 163, 184, 0.35);
          margin: 8px 0 14px 0;
          font-size: 16px;
          background: rgba(255,255,255,0.85);
          outline: none;
          transition: all 0.2s ease;
        }

        input:focus {
          border-color: #38bdf8;
          box-shadow: 0 0 0 4px rgba(56, 189, 248, 0.15);
          transform: scale(1.01);
        }

        .card {
          background:
            linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.90)),
            linear-gradient(90deg, rgba(16,185,129,0.04), rgba(59,130,246,0.04), rgba(168,85,247,0.04));
          border: 1px solid rgba(226,232,240,0.8);
          border-radius: 20px;
          padding: 16px;
          margin: 14px 0;
          white-space: pre-line;
          box-shadow:
            0 8px 20px rgba(15,23,42,0.05),
            inset 0 1px 0 rgba(255,255,255,0.8);
          animation: fadeUp 0.35s ease;
        }

        @keyframes fadeUp {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        .small {
          color: #64748b;
          font-size: 14px;
          text-align: center;
        }

        .row {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
        }

        .row form {
          flex: 1;
          min-width: 120px;
        }

        ul {
          margin: 0;
          padding-left: 20px;
        }

        .notice-ok {
          background: linear-gradient(135deg, #dcfce7, #ecfdf5);
          border: 1px solid #86efac;
          color: #166534;
          border-radius: 18px;
          padding: 13px;
          margin: 12px 0;
          text-align: center;
          font-weight: 700;
          box-shadow: 0 8px 18px rgba(22, 163, 74, 0.08);
        }

        .notice-warn {
          background: linear-gradient(135deg, #fff7ed, #fffbeb);
          border: 1px solid #fdba74;
          color: #9a3412;
          border-radius: 18px;
          padding: 13px;
          margin: 12px 0;
          text-align: center;
          font-weight: 700;
          box-shadow: 0 8px 18px rgba(245, 158, 11, 0.08);
        }

        .filter-row {
          display: flex;
          gap: 10px;
          margin: 12px 0 20px;
          flex-wrap: wrap;
        }

        .filter-row a {
          flex: 1;
          min-width: 150px;
          text-align: center;
          text-decoration: none;
          padding: 12px;
          border-radius: 16px;
          background: linear-gradient(135deg, #e2e8f0, #f1f5f9);
          color: #0f172a;
          font-weight: 700;
          transition: all 0.2s ease;
        }

        .filter-row a:hover {
          transform: translateY(-2px);
        }

        .filter-row a.active {
          background: linear-gradient(135deg, #0f766e, #2563eb, #7c3aed);
          color: white;
          box-shadow: 0 12px 24px rgba(37, 99, 235, 0.18);
        }

        @media (max-width: 640px) {
          .container {
            margin: 12px;
            padding: 16px;
            border-radius: 22px;
          }

          .logo-title {
            font-size: 20px;
          }

          .hero {
            height: 170px;
            border-radius: 20px;
          }

          .hero-text h1 {
            font-size: 22px;
          }

          .btn {
            font-size: 16px;
            padding: 15px;
            border-radius: 16px;
          }

          h2, h3 {
            font-size: 18px;
          }
        }
      </style>
    </head>
    <body>
      <div class="container">
        <div class="logo-box">
          <img src="{{ url_for('logo') }}" alt="LMK Logo">
          <div class="logo-title">LMK Заказ</div>
        </div>

        <div class="hero">
          <div class="hero-text">
            <h1>{{ hero_title }}</h1>
            <p>{{ hero_text }}</p>
          </div>
        </div>

        {{ body|safe }}
      </div>
    </body>
    </html>
    """, title=title, body=body, lang=get_lang(), hero_title=hero_title, hero_text=hero_text)


@app.route("/")
def home():
    if not session.get("authorized"):
        return redirect(url_for("password"))
    if not session.get("name"):
        return redirect(url_for("name"))
    if not session.get("language"):
        return redirect(url_for("language"))
    if not session.get("floor"):
        return redirect(url_for("floor"))
    if not session.get("chaynitsa"):
        return redirect(url_for("chaynitsa"))
    if not session.get("office"):
        return redirect(url_for("office"))
    return redirect(url_for("drink"))


@app.route("/password", methods=["GET", "POST"])
def password():
    error = ""
    if request.method == "POST":
        if request.form.get("password") == PASSWORD:
            session["authorized"] = True
            return redirect(url_for("name"))
        error = TEXTS["ru"]["wrong_password"]
    body = f"""
    <h2>{TEXTS['ru']['title']}</h2>
    <form method="post">
      <label>{TEXTS['ru']['password']}</label>
      <input type="password" name="password" required>
      <button class="btn" type="submit">OK</button>
    </form>
    <div class="small">{error}</div>
    """
    return render_page(TEXTS["ru"]["title"], body)


@app.route("/name", methods=["GET", "POST"])
def name():
    if request.method == "POST":
        user_name = request.form.get("name", "").strip()
        if user_name:
            session["name"] = user_name
            return redirect(url_for("language"))
    body = f"""
    <h2>{TEXTS['ru']['title']}</h2>
    <form method="post">
      <label>{TEXTS['ru']['name']}</label>
      <input type="text" name="name" required>
      <button class="btn" type="submit">{TEXTS['ru']['submit']}</button>
    </form>
    """
    return render_page(TEXTS["ru"]["title"], body)


@app.route("/language", methods=["GET", "POST"])
def language():
    if request.method == "POST":
        session["language"] = request.form.get("language", "ru")
        return redirect(url_for("floor"))
    body = """
    <h2>Выберите язык / Dil seçin</h2>
    <form method="post">
      <button class="btn" type="submit" name="language" value="ru">Русский</button>
      <button class="btn" type="submit" name="language" value="tr">Türkçe</button>
    </form>
    """
    return render_page("Language", body)


@app.route("/floor", methods=["GET", "POST"])
def floor():
    if request.method == "POST":
        session["floor"] = request.form.get("floor")
        session.pop("chaynitsa", None)
        session.pop("office", None)
        session["cart"] = []
        return redirect(url_for("chaynitsa"))
    lang = get_lang()
    floor1 = "1 этаж" if lang == "ru" else "1. kat"
    floor2 = "2 этаж" if lang == "ru" else "2. kat"
    body = f"""
    <h2>{t()['floor']}</h2>
    <form method="post">
      <button class="btn" type="submit" name="floor" value="{floor1}">{floor1}</button>
      <button class="btn" type="submit" name="floor" value="{floor2}">{floor2}</button>
    </form>
    <a class="btn btn-secondary" href="{url_for('my_orders')}">📄 Мои заказы / Siparişlerim</a>
    """
    return render_page(t()["floor"], body)


@app.route("/chaynitsa", methods=["GET", "POST"])
def chaynitsa():
    if request.method == "POST":
        session["chaynitsa"] = request.form.get("chaynitsa")
        return redirect(url_for("office"))
    body = f"""
    <h2>{t()['choose_chaynitsa']}</h2>
    <form method="post">
      <button class="btn" type="submit" name="chaynitsa" value="Nilufar">1️⃣ Nilufar</button>
      <button class="btn" type="submit" name="chaynitsa" value="Fatma">2️⃣ Fatma</button>
      <a class="btn btn-secondary" href="{url_for('floor')}">{BACK_RU if get_lang() == 'ru' else BACK_TR}</a>
    </form>
    """
    return render_page(t()["choose_chaynitsa"], body)


@app.route("/office", methods=["GET", "POST"])
def office():
    floor_value = session.get("floor")
    if not floor_value:
        return redirect(url_for("floor"))
    if request.method == "POST":
        session["office"] = request.form.get("office")
        session["cart"] = []
        return redirect(url_for("drink"))
    options = "".join(
        f'<button class="btn" type="submit" name="office" value="{office}">{office}</button>'
        for office in OFFICES[floor_value]
    )
    body = f"""
    <h2>{t()['office']}</h2>
    <form method="post">
      {options}
      <a class="btn btn-secondary" href="{url_for('chaynitsa')}">{BACK_RU if get_lang() == 'ru' else BACK_TR}</a>
    </form>
    """
    return render_page(t()["office"], body)


@app.route("/drink", methods=["GET", "POST"])
def drink():
    if request.method == "POST":
        drink_value = request.form.get("drink")
        session["selected_drink"] = drink_value
        if drink_value in ["💧 Вода", "💧 Su"]:
            session["pending_item"] = drink_value
            return redirect(url_for("quantity"))
        if drink_value in ["🍵 Чай зелёный", "🍵 Чай чёрный", "🍵 Yeşil çay", "🍵 Siyah çay"]:
            return redirect(url_for("tea_option"))
        return redirect(url_for("coffee_option"))
    lang = get_lang()
    items = ["🍵 Чай зелёный", "🍵 Чай чёрный", "☕ Кофе", "💧 Вода"] if lang == "ru" else ["🍵 Yeşil çay", "🍵 Siyah çay", "☕ Kahve", "💧 Su"]
    buttons = "".join(f'<button class="btn" type="submit" name="drink" value="{x}">{x}</button>' for x in items)
    body = f"""
    <h2>{t()['drink']}</h2>
    <form method="post">
      {buttons}
      <a class="btn btn-secondary" href="{url_for('office')}">{BACK_RU if lang == 'ru' else BACK_TR}</a>
    </form>
    """
    return render_page(t()["drink"], body)


@app.route("/tea_option", methods=["GET", "POST"])
def tea_option():
    if request.method == "POST":
        opt = request.form.get("option")
        session["pending_item"] = f"{session['selected_drink']} — {opt}"
        return redirect(url_for("quantity"))
    lang = get_lang()
    options = ["🍬 С сахаром", "🚫 Без сахара", "🍋 С лимоном"] if lang == "ru" else ["🍬 Şekerli", "🚫 Şekersiz", "🍋 Limonlu"]
    buttons = "".join(f'<button class="btn" type="submit" name="option" value="{x}">{x}</button>' for x in options)
    body = f"""
    <h2>{t()['tea_option']}</h2>
    <form method="post">
      {buttons}
      <a class="btn btn-secondary" href="{url_for('drink')}">{BACK_RU if lang == 'ru' else BACK_TR}</a>
    </form>
    """
    return render_page(t()["tea_option"], body)


@app.route("/coffee_option", methods=["GET", "POST"])
def coffee_option():
    if request.method == "POST":
        opt = request.form.get("option")
        if opt == "☕ Türk kahvesi":
            session["coffee_subtype"] = opt
            return redirect(url_for("turk_sugar"))
        session["pending_item"] = f"{session['selected_drink']} — {opt}"
        return redirect(url_for("quantity"))
    lang = get_lang()
    options = ["☕ Sade kahve", "☕ Türk kahvesi", "🥛 С молоком", "🚫 Без молока", "☕ Капучино"] if lang == "ru" else ["☕ Sade kahve", "☕ Türk kahvesi", "🥛 Sütlü", "🚫 Sütsüz", "☕ Kapuçino"]
    buttons = "".join(f'<button class="btn" type="submit" name="option" value="{x}">{x}</button>' for x in options)
    body = f"""
    <h2>{t()['coffee_option']}</h2>
    <form method="post">
      {buttons}
      <a class="btn btn-secondary" href="{url_for('drink')}">{BACK_RU if lang == 'ru' else BACK_TR}</a>
    </form>
    """
    return render_page(t()["coffee_option"], body)


@app.route("/turk_sugar", methods=["GET", "POST"])
def turk_sugar():
    if request.method == "POST":
        sugar = request.form.get("sugar")
        session["pending_item"] = f"{session['selected_drink']} — {session['coffee_subtype']} — {sugar}"
        return redirect(url_for("quantity"))
    lang = get_lang()
    options = ["🍬 С сахаром", "🚫 Без сахара"] if lang == "ru" else ["🍬 Şekerli", "🚫 Şekersiz"]
    buttons = "".join(f'<button class="btn" type="submit" name="sugar" value="{x}">{x}</button>' for x in options)
    body = f"""
    <h2>{t()['turk_sugar']}</h2>
    <form method="post">
      {buttons}
      <a class="btn btn-secondary" href="{url_for('coffee_option')}">{BACK_RU if lang == 'ru' else BACK_TR}</a>
    </form>
    """
    return render_page(t()["turk_sugar"], body)


@app.route("/quantity", methods=["GET", "POST"])
def quantity():
    if request.method == "POST":
        qty = int(request.form.get("qty"))
        cart = session.get("cart", [])
        cart.append({"name": session["pending_item"], "qty": qty})
        session["cart"] = cart
        session.pop("pending_item", None)
        session.pop("selected_drink", None)
        session.pop("coffee_subtype", None)
        return redirect(url_for("more_or_finish"))
    buttons = "".join(f'<button class="btn" type="submit" name="qty" value="{i}">{i}</button>' for i in [1, 2, 3, 4, 5])
    body = f"""
    <h2>{t()['qty']}</h2>
    <form method="post">
      {buttons}
      <a class="btn btn-secondary" href="{url_for('drink')}">{BACK_RU if get_lang() == 'ru' else BACK_TR}</a>
    </form>
    """
    return render_page(t()["qty"], body)


@app.route("/more_or_finish", methods=["GET", "POST"])
def more_or_finish():
    if request.method == "POST":
        act = request.form.get("act")
        if act == "more":
            return redirect(url_for("drink"))
        return redirect(url_for("finish_order"))
    cart_html = "<ul>" + "".join(f"<li>{i+1}. {x['name']} × {x['qty']}</li>" for i, x in enumerate(session.get("cart", []))) + "</ul>"
    body = f"""
    <h2>{t()['more']}</h2>
    <div class="card">{cart_html}</div>
    <form method="post">
      <button class="btn" type="submit" name="act" value="more">{t()['add_more']}</button>
      <button class="btn btn-green" type="submit" name="act" value="finish">{t()['finish']}</button>
    </form>
    """
    return render_page(t()["more"], body)


@app.route("/finish_order")
def finish_order():
    global order_counter

    cart = session.get("cart", [])
    if not cart:
        return redirect(url_for("drink"))

    lang = get_lang()
    name_value = session.get("name")
    floor_value = session.get("floor")
    office_value = session.get("office")
    chaynitsa_value = session.get("chaynitsa")
    now_time = datetime.now().strftime("%H:%M")
    current_id = order_counter
    order_counter += 1
    save_counter(order_counter)

    items_text = "\n".join([f"{i+1}. {item['name']} × {item['qty']}" for i, item in enumerate(cart)])

    order_data = {
        "id": current_id,
        "name": name_value,
        "floor": floor_value,
        "office": office_value,
        "chaynitsa": chaynitsa_value,
        "items": cart,
        "items_text": items_text,
        "lang": lang,
        "time": now_time,
        "status": "new",
    }
    orders[str(current_id)] = order_data
    save_json(ORDERS_FILE, orders)

    target_chat_id = get_target_chat_id(chaynitsa_value)

    if lang == "ru":
        telegram_text = (
            f"📦 Новый заказ №{current_id}\n"
            f"👤 {name_value}\n"
            f"🏬 Этаж: {floor_value}\n"
            f"🫖 Чайница: {chaynitsa_value}\n"
            f"🏢 Офис: {office_value}\n"
            f"🧾 Заказ:\n{items_text}\n"
            f"🕒 {now_time}"
        )
        telegram_buttons = {
            "inline_keyboard": [[
                {"text": "✅ Принять", "callback_data": f"accepted:{current_id}"},
                {"text": "❌ Нет", "callback_data": f"unavailable:{current_id}"},
                {"text": "🍽 Обед", "callback_data": f"lunch:{current_id}"}
            ]]
        }
    else:
        telegram_text = (
            f"📦 Yeni Sipariş No: {current_id}\n"
            f"👤 {name_value}\n"
            f"🏬 Kat: {floor_value}\n"
            f"🫖 Çaycı: {chaynitsa_value}\n"
            f"🏢 Ofis: {office_value}\n"
            f"🧾 Sipariş:\n{items_text}\n"
            f"🕒 {now_time}"
        )
        telegram_buttons = {
            "inline_keyboard": [[
                {"text": "✅ Kabul et", "callback_data": f"accepted:{current_id}"},
                {"text": "❌ Yok", "callback_data": f"unavailable:{current_id}"},
                {"text": "🍽 Öğle", "callback_data": f"lunch:{current_id}"}
            ]]
        }

    telegram_ok = send_telegram_message(target_chat_id, telegram_text, telegram_buttons)

    session["cart"] = []
    session.pop("floor", None)
    session.pop("office", None)
    session.pop("chaynitsa", None)

    telegram_notice = (
        f"<div class='notice-ok'>{t()['telegram_sent']}</div>"
        if telegram_ok else
        f"<div class='notice-warn'>{t()['telegram_failed']}</div>"
    )

    body = f"""
    <h2>{t()['title']}</h2>
    <h3>{t()['wait']}</h3>
    {telegram_notice}
    <div class="card">
      <b>№{current_id}</b><br><br>
      {"<br>".join([f"{i+1}. {x['name']} × {x['qty']}" for i, x in enumerate(cart)])}
    </div>
    <a class="btn" href="{url_for('my_orders')}">📄 Мои заказы / Siparişlerim</a>
    <a class="btn btn-secondary" href="{url_for('floor')}">OK</a>
    """
    return render_page(t()["title"], body)


@app.route("/my_orders")
def my_orders():
    name_value = session.get("name")
    if not name_value:
        return redirect(url_for("name"))

    user_orders = []
    for _, order in orders.items():
        if order.get("name") == name_value:
            user_orders.append(order)

    user_orders.sort(key=lambda x: x["id"], reverse=True)

    if not user_orders:
        body = f"""
        <h2>📄 Мои заказы / Siparişlerim</h2>
        <div class="card">{t()['my_orders_empty']}</div>
        <a class="btn" href="{url_for('floor')}">{t()['new_order']}</a>
        """
        return render_page("My Orders", body)

    cards = ""
    for order in user_orders:
        msg = panel_status_message(order["lang"], order["status"])
        cards += f"""
        <div class="card">
        <b>№{order['id']}</b><br>
        👤 {order['name']}<br>
        🫖 {order['chaynitsa']}<br>
        🏢 {order['office']}<br>
        🕒 {order['time']}<br><br>
        {order['items_text']}<br><br>
        <b>{msg}</b>
        </div>
        """

    body = f"""
    <h2>📄 Мои заказы / Siparişlerim</h2>
    {cards}
    <a class="btn" href="{url_for('floor')}">{t()['new_order']}</a>
    """
    return render_page("My Orders", body)


@app.route("/panel_login", methods=["GET", "POST"])
def panel_login():
    error = ""
    if request.method == "POST":
        password_value = request.form.get("password", "")

        if password_value == NILUFAR_PASSWORD:
            session["panel_auth"] = True
            session["panel_role"] = "nilufar"
            return redirect(url_for("panel_chaynitsa", who="Nilufar"))

        if password_value == FATMA_PASSWORD:
            session["panel_auth"] = True
            session["panel_role"] = "fatma"
            return redirect(url_for("panel_chaynitsa", who="Fatma"))

        if password_value == ADMIN_PASSWORD:
            session["panel_auth"] = True
            session["panel_role"] = "admin"
            return redirect(url_for("panel_home"))

        error = TEXTS["ru"]["wrong_password"]

    body = f"""
    <h2>{TEXTS['ru']['panel_title']}</h2>
    <form method="post">
      <label>Пароль</label>
      <input type="password" name="password" required>
      <button class="btn" type="submit">OK</button>
    </form>
    <div class="small">{error}</div>
    """
    return render_page("Panel Login", body)


@app.route("/panel")
def panel_home():
    if not session.get("panel_auth"):
        return redirect(url_for("panel_login"))

    if session.get("panel_role") == "nilufar":
        return redirect(url_for("panel_chaynitsa", who="Nilufar"))
    if session.get("panel_role") == "fatma":
        return redirect(url_for("panel_chaynitsa", who="Fatma"))

    body = f"""
    <h2>Панель управления</h2>
    <a class="btn" href="{url_for('panel_chaynitsa', who='Nilufar')}">🫖 Nilufar</a>
    <a class="btn" href="{url_for('panel_chaynitsa', who='Fatma')}">🫖 Fatma</a>
    <a class="btn btn-orange" href="{url_for('admin_panel')}">👑 Администратор</a>
    <a class="btn btn-secondary" href="{url_for('floor')}">↩ На сайт заказов</a>
    """
    return render_page("Panel", body)


@app.route("/panel/<who>")
def panel_chaynitsa(who):
    if not session.get("panel_auth"):
        return redirect(url_for("panel_login"))

    role = session.get("panel_role")
    if role == "nilufar" and who != "Nilufar":
        return redirect(url_for("panel_chaynitsa", who="Nilufar"))
    if role == "fatma" and who != "Fatma":
        return redirect(url_for("panel_chaynitsa", who="Fatma"))

    mode = request.args.get("mode", "new")

    panel_orders = []
    for _, order in orders.items():
        if order.get("chaynitsa") == who:
            if mode == "new":
                if order.get("status") == "new":
                    panel_orders.append(order)
            else:
                panel_orders.append(order)

    panel_orders.sort(key=lambda x: x["id"], reverse=True)

    filter_row = f"""
    <div class="filter-row">
      <a href="{url_for('panel_chaynitsa', who=who)}?mode=new" class="{'active' if mode == 'new' else ''}">{t()['new_orders_only']}</a>
      <a href="{url_for('panel_chaynitsa', who=who)}?mode=all" class="{'active' if mode == 'all' else ''}">{t()['all_orders']}</a>
    </div>
    """

    cards = ""
    for order in panel_orders:
        status_badge = status_text(order["lang"], order["status"])
        cards += f"""
        <div class="card">
        <b>№{order['id']}</b><br>
        👤 {order['name']}<br>
        🏬 {order['floor']}<br>
        🏢 {order['office']}<br>
        🕒 {order['time']}<br>
        Статус: <b>{status_badge}</b><br><br>
        {order['items_text']}
        </div>

        <div class="row">
          <form method="post" action="{url_for('update_status', order_id=order['id'], status='accepted')}">
            <input type="hidden" name="back_to" value="{url_for('panel_chaynitsa', who=who)}?mode={mode}">
            <button class="btn btn-green" type="submit">✅ Принято</button>
          </form>
          <form method="post" action="{url_for('update_status', order_id=order['id'], status='unavailable')}">
            <input type="hidden" name="back_to" value="{url_for('panel_chaynitsa', who=who)}?mode={mode}">
            <button class="btn btn-red" type="submit">❌ Нет</button>
          </form>
          <form method="post" action="{url_for('update_status', order_id=order['id'], status='lunch')}">
            <input type="hidden" name="back_to" value="{url_for('panel_chaynitsa', who=who)}?mode={mode}">
            <button class="btn btn-orange" type="submit">🍽 Обед</button>
          </form>
        </div>
        """
    if not cards:
        cards = f"<div class='card'>{t()['orders_empty']}</div>"

    back_link = url_for("panel_home") if role == "admin" else url_for("panel_chaynitsa", who=who)

    body = f"""
    <h2>🫖 {who}</h2>
    {filter_row}
    {cards}
    <a class="btn btn-secondary" href="{back_link}">↩ Назад</a>
    """
    return render_page(f"Panel {who}", body)


@app.route("/admin")
def admin_panel():
    if not session.get("panel_auth"):
        return redirect(url_for("panel_login"))
    if session.get("panel_role") != "admin":
        return redirect(url_for("panel"))

    panel_orders = list(orders.values())
    panel_orders.sort(key=lambda x: x["id"], reverse=True)

    cards = ""
    for order in panel_orders:
        cards += f"""
        <div class="card">
        <b>№{order['id']}</b><br>
        👤 {order['name']}<br>
        🫖 {order['chaynitsa']}<br>
        🏬 {order['floor']}<br>
        🏢 {order['office']}<br>
        🕒 {order['time']}<br>
        Статус: <b>{status_text(order['lang'], order['status'])}</b><br><br>
        {order['items_text']}
        </div>
        """
    if not cards:
        cards = f"<div class='card'>{t()['orders_empty']}</div>"

    body = f"""
    <h2>👑 Администратор</h2>
    {cards}
    <a class="btn btn-secondary" href="{url_for('panel_home')}">↩ Назад</a>
    """
    return render_page("Admin", body)


@app.route("/update_status/<int:order_id>/<status>", methods=["POST"])
def update_status(order_id, status):
    key = str(order_id)
    if key in orders and status in ["accepted", "unavailable", "lunch"]:
        orders[key]["status"] = status
        save_json(ORDERS_FILE, orders)
    return redirect(request.form.get("back_to", url_for("panel_home")))


@app.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json(silent=True)

    if not data:
        return "ok"

    callback = data.get("callback_query")
    if not callback:
        return "ok"

    callback_query_id = callback.get("id")
    callback_data = callback.get("data", "")
    message = callback.get("message", {})
    telegram_chat_id = message.get("chat", {}).get("id")
    telegram_message_id = message.get("message_id")

    if callback_query_id:
        answer_callback_query(callback_query_id)

    if ":" not in callback_data:
        return "ok"

    status, order_id = callback_data.split(":", 1)

    if order_id not in orders:
        return "ok"

    if status not in ["accepted", "unavailable", "lunch"]:
        return "ok"

    orders[order_id]["status"] = status
    save_json(ORDERS_FILE, orders)

    order = orders[order_id]
    lang = order["lang"]

    if lang == "ru":
        new_text = (
            f"📦 Заказ №{order['id']}\n"
            f"👤 {order['name']}\n"
            f"🏬 Этаж: {order['floor']}\n"
            f"🫖 Чайница: {order['chaynitsa']}\n"
            f"🏢 Офис: {order['office']}\n"
            f"🧾 Заказ:\n{order['items_text']}\n"
            f"🕒 {order['time']}\n\n"
            f"Статус: {status_text(lang, status)}"
        )
    else:
        new_text = (
            f"📦 Sipariş No: {order['id']}\n"
            f"👤 {order['name']}\n"
            f"🏬 Kat: {order['floor']}\n"
            f"🫖 Çaycı: {order['chaynitsa']}\n"
            f"🏢 Ofis: {order['office']}\n"
            f"🧾 Sipariş:\n{order['items_text']}\n"
            f"🕒 {order['time']}\n\n"
            f"Durum: {status_text(lang, status)}"
        )

    edit_telegram_message(telegram_chat_id, telegram_message_id, new_text)
    return "ok"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
