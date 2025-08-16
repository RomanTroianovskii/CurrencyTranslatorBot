import os
import aiohttp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_URL = "https://api.frankfurter.app"
CURRENCIES = {}  # All available currencies
TOKEN = os.getenv("BOT_TOKEN")  # Railway берет токен из переменной окружения

# "/start" command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я конвертер валют 💱\n"
        "Использование: /convert <сумма> <из_валюты> <в_валюту>\n"
        "Пример: /convert 100 USD RUB\n"
        "Список валют: /currencies"
    )

# "/currencies" command handler, displays all available currencies
async def currencies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENCIES
    if not CURRENCIES:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/currencies") as resp:  # Request to API
                CURRENCIES = await resp.json()

    text = "🌍 Доступные валюты:\n" + "\n".join([f"{k} — {v}" for k, v in CURRENCIES.items()])
    await update.message.reply_text(text)

# "/convert" command handler, converts currency and displays it
async def convert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CURRENCIES
    if not CURRENCIES:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/currencies") as resp:  # Request to API
                CURRENCIES = await resp.json()

    if len(context.args) != 3:  # Checking for correct number of args
        await update.message.reply_text("❌ Формат: /convert <сумма> <из_валюты> <в_валюту>")
        return

    try:
        amount = float(context.args[0])
        from_currency = context.args[1].upper()
        to_currency = context.args[2].upper()

        if from_currency not in CURRENCIES or to_currency not in CURRENCIES:  # Checking if currency is in list of available
            await update.message.reply_text("❌ Неверный код валюты. Используй /currencies для списка.")
            return

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/latest", params={  # Request to API
                "amount": amount,
                "from": from_currency,
                "to": to_currency
            }) as resp:
                data = await resp.json()

        rate = data["rates"].get(to_currency)
        if not rate:
            await update.message.reply_text("❌ Ошибка конвертации.")
            return

        await update.message.reply_text(f"{amount} {from_currency} = {rate} {to_currency}")

    except ValueError:
        await update.message.reply_text("❌ Сумма должна быть числом.")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e}")

def main():  # Main function
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("currencies", currencies))
    app.add_handler(CommandHandler("convert", convert))

    app.run_polling()


main()
