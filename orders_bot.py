from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import pandas as pd

TOKEN = "8657044201:AAEXw0JVeLU6FAbHeKB5KxZriTJo_et99Ik"
print("BOT STARTED SUCCESSFULLY")

orders = pd.read_excel("orders.xlsx")
products = pd.read_excel("products.xlsx")

orders["phone"] = orders["phone"].astype(str)

categories = products["Раздел"].dropna().unique().tolist()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

     keyboard = [["▶️ Почати"]]

     reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

     await update.message.reply_text(
        "Вітаємо! Натисніть кнопку Меню, щоб розпочати роботу з ботом:",
        reply_markup=reply_markup
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["📦 Мої замовлення"],
        ["🛒 Каталог товарів"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Оберіть дію:",
        reply_markup=reply_markup
    )


async def orders_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [KeyboardButton("Поділитися номером", request_contact=True)],
        ["⬅️ Головне меню"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Поділіться номером телефону",
        reply_markup=reply_markup
    )


async def contact_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    phone = update.message.contact.phone_number.replace("+", "")

    client_orders = orders[orders["phone"] == phone]

    if client_orders.empty:
        await update.message.reply_text("Замовлення не знайдені")
        return

    grouped = client_orders.groupby("order")

    for order_id, group in grouped:

        first_row = group.iloc[0]

        message = (
            f"Замовлення № {order_id}\n"
            f"Дата: {first_row['date']}\n"
            f"Клієнт: {first_row['Name']}\n\n"
            f"Товари:\n"
        )

        for _, row in group.iterrows():

            message += (
                f"- {row['product']}\n"
                f"Артикул: {row['article']}\n"
                f"Кількість: {row['quantit']}\n"
                f"Ціна: {row['price']} {row['Currency']}\n"
                f"Знижка: {row['sale (%)']}%\n\n"
               
            )

        await update.message.reply_text(message)
        keyboard = [["⬅️ Головне меню"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
        "Повернутися до головного меню:",
        reply_markup=reply_markup
            )


async def catalog_button(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [[cat] for cat in categories]

    keyboard.append(["⬅️ Головне меню"])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Оберіть категорію:",
        reply_markup=reply_markup
    )


async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    category = update.message.text
    if update.message.text == "⬅️ Головне меню":
        return

    filtered = products[products["Раздел"] == category].head(10)

    if filtered.empty:
        return

    for _, row in filtered.iterrows():

        name = row["Название (ua)"]
        price = row["Цена"]
        status = row["Наличие"]

        photo = row["Фото"] if "Фото" in products.columns else None

        message = (
            f"{name}\n"
            f"Ціна: {price} грн\n"
            f"Статус: {status}"
        )

        if photo and str(photo) != "nan":
            await update.message.reply_photo(photo, caption=message)
        else:
            await update.message.reply_text(message)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))

app.add_handler(MessageHandler(filters.Regex("^▶️ Почати$"), main_menu))
app.add_handler(MessageHandler(filters.Regex("^📦 Мої замовлення$"), orders_button))
app.add_handler(MessageHandler(filters.Regex("^🛒 Каталог товарів$"), catalog_button))
app.add_handler(MessageHandler(filters.Regex("^⬅️ Головне меню$"), start))

app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

app.add_handler(MessageHandler(filters.TEXT, category_handler))


import asyncio

async def main():
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    await asyncio.Event().wait()

asyncio.run(main())

