import logging
from flask import Flask, request
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

TOKEN = "8321461571:AAGsrRtIJivfIqdpYtp-UtuCO41iyKO8SYI"

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

(
    NAME,
    PHONE,
    TOPIC,
    DAY,
    TIME,
    TYPE,
    CONFIRM
) = range(7)

DAYS = ["شنبه", "یکشنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنجشنبه"]
TIMES = {
    "شنبه": ["10:00", "12:00", "14:00"],
    "یکشنبه": ["11:00", "13:00"],
    "دوشنبه": ["9:00", "15:00"],
    "سه‌شنبه": ["10:00", "16:00"],
    "چهارشنبه": ["12:00", "17:00"],
    "پنجشنبه": ["11:00", "14:00"],
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["شروع ثبت جلسه"]]
    await update.message.reply_text(
        "سلام 👋 برای شروع روی دکمه زیر بزنید.",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return NAME


async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("شماره تماس خود را وارد کنید:")
    return PHONE


async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.text
    await update.message.reply_text("موضوع جلسه را وارد کنید:")
    return TOPIC


async def get_topic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["topic"] = update.message.text
    keyboard = [[day] for day in DAYS]
    await update.message.reply_text(
        "روز مورد نظر را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return DAY


async def get_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selected_day = update.message.text
    context.user_data["day"] = selected_day

    time_buttons = [[t] for t in TIMES[selected_day]]
    time_buttons.append(["🔙 بازگشت"])

    await update.message.reply_text(
        "ساعت مورد نظر را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(time_buttons, resize_keyboard=True),
    )
    return TIME


async def get_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 بازگشت":
        keyboard = [[day] for day in DAYS]
        await update.message.reply_text(
            "روز جدید را انتخاب کنید:",
            reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
        )
        return DAY

    context.user_data["time"] = update.message.text

    keyboard = [["حضوری"], ["آنلاین"]]
    await update.message.reply_text(
        "نحوه برگزاری را انتخاب کنید:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )
    return TYPE


async def get_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["type"] = update.message.text

    await update.message.reply_text(
        "💳 مبلغ 1,000,000 تومان\n"
        "به شماره کارت:\n"
        "6037-XXXX-XXXX-XXXX\n"
        "به نام رضا مظلوم\n\n"
        "واریز کنید و عکس فیش را ارسال نمایید."
    )

    summary = (
        f"✅ اطلاعات شما:\n\n"
        f"نام: {context.user_data['name']}\n"
        f"تلفن: {context.user_data['phone']}\n"
        f"موضوع: {context.user_data['topic']}\n"
        f"روز: {context.user_data['day']}\n"
        f"ساعت: {context.user_data['time']}\n"
        f"نوع جلسه: {context.user_data['type']}"
    )

    await update.message.reply_text(summary)

    return ConversationHandler.END


application = ApplicationBuilder().token(TOKEN).build()

conv_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
        PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
        TOPIC: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_topic)],
        DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_day)],
        TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_time)],
        TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_type)],
    },
    fallbacks=[],
)

application.add_handler(conv_handler)


@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.update_queue.put_nowait(update)
    return "ok"


@app.route("/")
def home():
    return "Bot is running!"

import asyncio

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())
    app.run(host="0.0.0.0", port=10000)


