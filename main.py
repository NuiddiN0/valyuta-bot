try:
    import telegram
except ImportError:
    import sys
    sys.exit("python-telegram-bot o'rnatilmagan!")

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests

TOKEN = "8749569760:AAHZB_eOryZohaLub3hd_GhDK4iOQfsVLQU"

def get_rates():
    try:
        url = "https://cbu.uz/uz/arkhiv-kursov-valyut/json/"
        data = requests.get(url, timeout=5).json()
        rates = {}
        for item in data:
            if item["Ccy"] in ["USD", "EUR", "RUB", "GBP", "TJS"]:
                rates[item["Ccy"]] = float(item["Rate"])
        return rates
    except:
        return {"USD": 12800, "EUR": 13900, "RUB": 142, "GBP": 16200, "TJS": 1180}

def convert(amount, from_ccy, to_ccy, rates):
    if from_ccy == "UZS":
        in_uzs = amount
    else:
        in_uzs = amount * rates[from_ccy]
    if to_ccy == "UZS":
        return in_uzs
    else:
        return in_uzs / rates[to_ccy]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💵 Dollar", "💶 Euro"],
        ["🇷🇺 Rubl", "🇬🇧 Funt"],
        ["🇹🇯 Somoni", "📊 Barcha kurslar"]
    ]
    markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Salom! 💱 Valyuta Kurs Botiga xush kelibsiz!\n\n"
        "📌 Ishlatish:\n"
        "• 10 dollar-somoni\n"
        "• 100 euro-somoni\n"
        "• 500 somoni-dollar\n"
        "• 50000 som-dollar\n\n"
        "Yoki tugmalardan birini bosing 👇",
        reply_markup=markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()
    rates = get_rates()

    mapping = {
        "dollar": "USD", "usd": "USD",
        "euro": "EUR", "eur": "EUR",
        "rubl": "RUB", "rub": "RUB",
        "funt": "GBP", "gbp": "GBP",
        "somoni": "TJS", "tjs": "TJS",
        "som": "UZS", "uzs": "UZS", "sum": "UZS"
    }

    emojis = {
        "USD": "💵", "EUR": "💶",
        "RUB": "🇷🇺", "GBP": "🇬🇧",
        "TJS": "🇹🇯", "UZS": "🇺🇿"
    }

    names = {
        "USD": "Dollar", "EUR": "Euro",
        "RUB": "Rubl", "GBP": "Funt",
        "TJS": "Somoni", "UZS": "So'm"
    }

    # Tugmalar
    if text in ["💵 dollar", "dollar"]:
        r = rates.get("USD", 0)
        await update.message.reply_text(f"💵 Dollar kursi:\n1 USD = {r:,.0f} so'm")
        return
    if text in ["💶 euro", "euro"]:
        r = rates.get("EUR", 0)
        await update.message.reply_text(f"💶 Euro kursi:\n1 EUR = {r:,.0f} so'm")
        return
    if text in ["🇷🇺 rubl", "rubl"]:
        r = rates.get("RUB", 0)
        await update.message.reply_text(f"🇷🇺 Rubl kursi:\n1 RUB = {r:,.2f} so'm")
        return
    if text in ["🇬🇧 funt", "funt"]:
        r = rates.get("GBP", 0)
        await update.message.reply_text(f"🇬🇧 Funt kursi:\n1 GBP = {r:,.0f} so'm")
        return
    if text in ["🇹🇯 somoni", "somoni"]:
        r = rates.get("TJS", 0)
        await update.message.reply_text(f"🇹🇯 Somoni kursi:\n1 TJS = {r:,.2f} so'm")
        return
    if "barcha" in text:
        msg = "📊 Bugungi kurslar (CBU):\n\n"
        for ccy, rate in rates.items():
            msg += f"{emojis.get(ccy, '')} 1 {ccy} = {rate:,.2f} so'm\n"
        await update.message.reply_text(msg)
        return

    # "10 dollar-somoni" formatini tahlil qilish
    parts = text.split()
    if len(parts) == 2:
        try:
            amount = float(parts[0])
            currencies = parts[1].split("-")

            # "10 dollar-somoni" — ikki valyuta
            if len(currencies) == 2:
                from_ccy = mapping.get(currencies[0].strip())
                to_ccy = mapping.get(currencies[1].strip())
                if from_ccy and to_ccy:
                    result = convert(amount, from_ccy, to_ccy, rates)
                    e1 = emojis.get(from_ccy, "")
                    e2 = emojis.get(to_ccy, "")
                    n1 = names.get(from_ccy, from_ccy)
                    n2 = names.get(to_ccy, to_ccy)
                    await update.message.reply_text(
                        f"{e1} {amount:,.2f} {n1} = {e2} {result:,.2f} {n2}"
                    )
                    return

            # "10 dollar" — so'mga hisoblash
            if len(currencies) == 1:
                from_ccy = mapping.get(currencies[0].strip())
                if from_ccy and from_ccy in rates:
                    result = convert(amount, from_ccy, "UZS", rates)
                    e1 = emojis.get(from_ccy, "")
                    await update.message.reply_text(
                        f"{e1} {amount:,.2f} {names[from_ccy]} = 🇺🇿 {result:,.0f} so'm"
                    )
                    return
        except:
            pass

    await update.message.reply_text(
        "Tushunmadim I don't understand🤔\n\n"
        "Misol:\n"
        "• 10 dollar-somoni\n"
        "• 100 euro-somoni\n"
        "• 500 somoni-dollar\n"
        "• 50000 som-dollar\n"
        "• 10 dollar (so'mga)"
    )

async def kurs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rates = get_rates()
    msg = "📊 Bugungi kurslar (CBU):\n\n"
    emojis = {"USD": "💵", "EUR": "💶", "RUB": "🇷🇺", "GBP": "🇬🇧", "TJS": "🇹🇯"}
    for ccy, rate in rates.items():
        msg += f"{emojis.get(ccy, '')} 1 {ccy} = {rate:,.2f} so'm\n"
    await update.message.reply_text(msg)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kurs", kurs))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Bot ishga tushdi! Telegramda @valyuta_calce_bot ni oching")
    app.run_polling()

if __name__ == "__main__":
    main()
