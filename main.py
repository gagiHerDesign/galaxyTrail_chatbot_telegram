from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from bot.config import TOKEN, BOT_USERNAME
from bot.commands import start, help_command, park, sky, menu_handler, location_handler, future_events, lightpollution
from bot.messages import handle_response
from telegram.ext import ContextTypes
from telegram import Update
import os
from aiohttp import web


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type} sent: {text}')

    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response: str = handle_response(new_text, BOT_USERNAME)
        else:
            return
    else:
        response: str = handle_response(text, BOT_USERNAME)

    print('Bot:', response)
    await update.message.reply_text(response)


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("park", park))
    app.add_handler(CommandHandler("sky", sky))
    app.add_handler(CommandHandler("future", future_events))
    app.add_handler(CommandHandler("lightpollution", lightpollution))


    # callback query (inline keyboard) handler
    app.add_handler(CallbackQueryHandler(menu_handler))

    # location handler for replies that request location
    app.add_handler(MessageHandler(filters.LOCATION, location_handler))

    # message handler
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # error handler
    app.add_error_handler(error)

    # ✅ 新增一個 /healthz endpoint
    async def healthz(request):
        return web.Response(text="ok")  # 只回傳 ok 代表健康狀態正常

    # web_app = app.web_app
    # web_app.router.add_get("/healthz", healthz)
    print("Bot with /healthz endpoint is running...")

    # decide between webhook or polling based on environment
    use_webhook = os.getenv("USE_WEBHOOK", "").lower() == "true"

    if use_webhook:
        port = int(os.getenv("PORT", "8080"))
        webhook_url = os.getenv("WEBHOOK_URL")
        webhook_path = os.getenv("WEBHOOK_PATH", "webhook")
        if not webhook_url:
            raise RuntimeError("WEBHOOK_URL is required when USE_WEBHOOK=true")

        print("Starting bot with webhook...")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            url_path=webhook_path,
            webhook_url=f"{webhook_url}/{webhook_path}"
        )
    else:
        print("Starting bot locally with polling...")
        app.run_polling()


if __name__ == '__main__':
    print('Starting bot...')
    main()
