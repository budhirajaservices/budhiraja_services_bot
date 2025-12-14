# ================= IMPORTS =================
import telebot
from telebot import types
import sqlite3
import datetime

# ================= CONFIG =================
BOT_TOKEN = "8266319055:AAHSltZMm_ZgnRL72QJGwAjPwTR18ywkTbg"
ADMIN_IDS = [7969971757]
DB_FILE = "budhiraja_services_bot.db"
BOT_NAME = "Budhiraja Services"

bot = telebot.TeleBot(BOT_TOKEN)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS leads (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        name TEXT,
        service TEXT,
        phone TEXT,
        requirement TEXT,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def save_lead(uid, username, name, service, phone, requirement=""):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
    INSERT INTO leads VALUES (NULL,?,?,?,?,?,?,?)
    """, (
        uid,
        username,
        name,
        service,
        phone,
        requirement,
        datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

# ================= SERVICES LIST =================
SERVICES = [
    "🌐 Websites",
    "📱 Mobile Development",
    "⚙ Custom Web Apps",
    "🔍 SEO Optimization",
    "▶ YouTube Monetization Sprint",
    "📸 Instagram Followers Boost",
    "📘 Facebook Community Growth",
    "💬 WhatsApp Channel Expansion",
    "🚀 Website Traffic Accelerator",
    "🐦 Twitter Profile Boost",
    "✈ Telegram Profile Boost",
    "🧵 Threads Profile Boost",
    "🎵 Spotify Profile Boost",
    "🤖 Telegram Chatbot",
    "🤖 Whatsapp Chatbot"
]

# ================= BOTTOM FIXED KEYBOARD =================
def bottom_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(0, len(SERVICES), 2):
        if i + 1 < len(SERVICES):
            kb.row(SERVICES[i], SERVICES[i + 1])
        else:
            kb.row(SERVICES[i])
    kb.row("📞 Contact Us", "🌐 Visit")
    return kb

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"👋 Welcome to *{BOT_NAME}*\n\n"
        "👇 Please select a service:",
        parse_mode="Markdown",
        reply_markup=bottom_menu()
    )

# ================= USER STATE =================
user_state = {}

# ================= SERVICE SELECTION =================
@bot.message_handler(func=lambda m: m.text in SERVICES)
def select_service(message):
    service_selected = message.text
    user_state[message.chat.id] = {"service": service_selected}

    # Ask full name
    msg = bot.send_message(
        message.chat.id,
        f"📝 *{service_selected}*\n\nEnter your full name:",
        parse_mode="Markdown"
    )
    bot.register_next_step_handler(msg, ask_phone)

# ================= LEAD FLOW =================
def ask_phone(message):
    user_state[message.chat.id]["name"] = message.text
    msg = bot.send_message(
        message.chat.id,
        "📱 Enter your mobile number:"
    )
    bot.register_next_step_handler(msg, finalize)

def finalize(message):
    chat = message.chat.id
    info = user_state[chat]
    user = message.from_user

    # Save lead with empty requirement (service fixed)
    save_lead(
        user.id,
        user.username or "",
        info["name"],
        info["service"],
        message.text,
        requirement=""  # empty because no extra requirement
    )

    # Notify admin
    for admin in ADMIN_IDS:
        bot.send_message(
            admin,
            f"🔔 NEW LEAD\n\n"
            f"Service: {info['service']}\n"
            f"Name: {info['name']}\n"
            f"Phone: {message.text}"
        )

    bot.send_message(
        chat,
        "✅ Thank you! We will contact you soon.",
        reply_markup=bottom_menu()
    )

    user_state.pop(chat, None)

# ================= CONTACT / VISIT HANDLERS =================
@bot.message_handler(func=lambda m: m.text == "📞 Contact Us")
def contact_us(message):
    # Inline keyboard with WhatsApp button
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        text="💬 Chat on WhatsApp",
        url="https://wa.me/919518126610?text=Hello%20Budhiraja%20Services"
    ))

    # Message text
    bot.send_message(
        message.chat.id,
        "📞 Contact Us\n\nYou can call us at 9518126610 or click below to WhatsApp us:",
        reply_markup=kb
    )

@bot.message_handler(func=lambda m: m.text == "🌐 Visit")
def visit_website(message):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton(
        text="🌐 Visit Website",
        url="https://www.budhirajaservices.in"
    ))
    bot.send_message(
        message.chat.id,
        "Visit our website:",
        reply_markup=kb
    )

# ================= RUN =================
if __name__ == "__main__":
    init_db()
    print("🚀 Budhiraja Services Bot Running...")
    bot.infinity_polling()
