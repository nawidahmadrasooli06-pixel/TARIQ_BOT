import os
import re
import logging
import threading

from fastapi import FastAPI
import uvicorn

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# CONFIG
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "Pv_Tariq"
).strip().lstrip("@").lower()

ADMIN_CHAT_ID_RAW = os.getenv(
    "ADMIN_CHAT_ID",
    ""
).strip()

try:
    ADMIN_CHAT_ID = (
        int(ADMIN_CHAT_ID_RAW)
        if ADMIN_CHAT_ID_RAW
        else None
    )
except ValueError:
    ADMIN_CHAT_ID = None


BOT_NAME = "Tariq Support Bot"
OWNER_NAME = "Tariq"
OWNER_USERNAME = "@Pv_Tariq"

CHANNEL_URL = "https://t.me/Chlesh_Dictator"
CHANNEL_USERNAME = "@Chlesh_Dictator"

PORT = int(os.getenv("PORT", "10000"))


if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN is missing. "
        "Please add BOT_TOKEN in Render Environment Variables."
    )


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# FASTAPI / RENDER WEB SERVER
# =========================================================

web_app = FastAPI()


@web_app.get("/")
async def home():
    return {
        "status": "online",
        "bot": BOT_NAME
    }


@web_app.get("/health")
async def health():
    return {
        "status": "ok",
        "bot": BOT_NAME
    }


def run_web_server():
    uvicorn.run(
        web_app,
        host="0.0.0.0",
        port=PORT,
        log_level="warning",
    )


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user) -> bool:
    if not user:
        return False

    # Best and safest method:
    # numeric Telegram user ID
    if ADMIN_CHAT_ID is not None:
        return user.id == ADMIN_CHAT_ID

    # Temporary fallback:
    # username until ADMIN_CHAT_ID is added to Render
    username = (user.username or "").strip().lower()

    return username == ADMIN_USERNAME


# =========================================================
# MAIN MENU
# =========================================================

def main_menu():
    keyboard = [
        [
            "👤 مشخصات طارق",
            "💌 ارسال پیام"
        ],
        [
            "🤖 درباره ربات",
            "❓ راهنما"
        ],
    ]

    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        is_persistent=True,
    )


# =========================================================
# CHANNEL BUTTON
# =========================================================

def channel_button():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📢 کانال طارق",
                    url=CHANNEL_URL
                )
            ]
        ]
    )


# =========================================================
# /START
# =========================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    global ADMIN_CHAT_ID

    if not update.effective_user:
        return

    if not update.message:
        return

    user = update.effective_user

    # If Tariq starts the bot, remember his numeric ID
    if is_admin(user):
        ADMIN_CHAT_ID = update.effective_chat.id

        logger.info(
            "Admin detected. Chat ID: %s",
            ADMIN_CHAT_ID
        )

    # Reset sending mode
    context.user_data["waiting_message"] = False

    text = (
        "سلام، خوش اومدی 👋🏻\n\n"
        "به ربات شخصی طارق خوش اومدی.\n\n"
        "از اینجا می‌تونی مستقیماً برای طارق "
        "پیام بفرستی.\n\n"
        "می‌تونی متن، عکس، ویدیو، فایل یا ویس "
        "ارسال کنی.\n\n"
        "از منوی پایین گزینه موردنظرت رو انتخاب کن."
    )

    await update.message.reply_text(
        text,
        reply_markup=channel_button()
    )

    await update.message.reply_text(
        "منوی ربات:",
        reply_markup=main_menu()
    )


# =========================================================
# PROFILE
# =========================================================

async def profile(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    text = (
        "👤 مشخصات طارق\n\n"
        f"نام: {OWNER_NAME}\n"
        f"Username: {OWNER_USERNAME}\n\n"
        "برای ارتباط مستقیم می‌تونی از گزینه "
        "«💌 ارسال پیام» استفاده کنی.\n\n"
        "ساخته شده برای ارتباط راحت‌تر با طارق."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================================================
# ABOUT BOT
# =========================================================

async def about_bot(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    text = (
        "🤖 درباره ربات\n\n"
        "این ربات برای ارتباط مستقیم و راحت‌تر "
        "با طارق ساخته شده.\n\n"
        "می‌تونی از طریق ربات پیام، عکس، ویدیو، "
        "فایل یا ویس بفرستی.\n\n"
        "پیام تو مستقیماً برای طارق ارسال میشه "
        "و طارق می‌تونه از طریق همین ربات بهت پاسخ بده."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================================================
# HELP
# =========================================================

async def help_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    text = (
        "❓ راهنمای ربات\n\n"
        "👤 مشخصات طارق\n"
        "اطلاعات مربوط به طارق را نمایش می‌دهد.\n\n"
        "💌 ارسال پیام\n"
        "با این گزینه می‌تونی پیام خودت رو برای "
        "طارق ارسال کنی.\n\n"
        "🤖 درباره ربات\n"
        "توضیحات مربوط به ربات را نمایش می‌دهد.\n\n"
        "📢 کانال طارق\n"
        "از دکمه کانال در صفحه اصلی می‌تونی وارد "
        "کانال طارق بشی."
    )

    await update.message.reply_text(
        text,
        reply_markup=main_menu()
    )


# =========================================================
# /MYID
# =========================================================

async def my_id(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.effective_user:
        return

    if not update.message:
        return

    if not is_admin(update.effective_user):
        return

    await update.message.reply_text(
        "🆔 اطلاعات شما\n\n"
        f"User ID:\n{update.effective_user.id}\n\n"
        f"Chat ID:\n{update.effective_chat.id}"
    )


# =========================================================
# START SENDING MODE
# =========================================================

async def start_sending(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    context.user_data["waiting_message"] = True

    await update.message.reply_text(
        "💌 پیام خودت رو برای طارق بفرست.\n\n"
        "می‌تونی متن، عکس، ویدیو، فایل یا ویس بفرستی.\n\n"
        "پیامت مستقیماً برای طارق ارسال میشه.\n\n"
        "برای لغو و برگشت به منوی اصلی، /start رو بزن.",
        reply_markup=main_menu()
    )


# =========================================================
# SEND USER MESSAGE TO TARIQ
# =========================================================

async def send_user_message_to_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    global ADMIN_CHAT_ID

    if not update.message:
        return

    if not update.effective_user:
        return

    # Admin must be configured
    if ADMIN_CHAT_ID is None:
        await update.message.reply_text(
            "⚠️ ربات هنوز توسط طارق فعال نشده.\n\n"
            "لطفاً طارق یک‌بار وارد ربات شود و "
            "/start را بزند."
        )
        return

    user = update.effective_user

    username_text = (
        f"@{user.username}"
        if user.username
        else "ندارد"
    )

    # -----------------------------------------------------
    # IMPORTANT
    #
    # The numeric User ID is placed inside this header.
    # Tariq must Reply to this header message.
    # -----------------------------------------------------

    header = (
        "📩 پیام جدید از کاربر\n\n"
        f"👤 نام: {user.full_name}\n"
        f"🔹 Username: {username_text}\n"
        f"🆔 User ID: {user.id}\n\n"
        "↩️ برای پاسخ دادن، روی همین پیام Reply بزن."
    )

    try:

        # First send the information header
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=header
        )

        # Then copy the actual message
        await update.message.copy(
            chat_id=ADMIN_CHAT_ID
        )

        # Stop waiting mode
        context.user_data["waiting_message"] = False

        await update.message.reply_text(
            "✅ پیامت با موفقیت برای طارق ارسال شد.",
            reply_markup=main_menu()
        )

        logger.info(
            "Message from user %s sent to admin.",
            user.id
        )

    except Exception:
        logger.exception(
            "Could not send user message to admin."
        )

        await update.message.reply_text(
            "❌ ارسال پیام انجام نشد.\n\n"
            "لطفاً کمی بعد دوباره امتحان کن.",
            reply_markup=main_menu()
        )


# =========================================================
# EXTRACT USER ID FROM ADMIN REPLY
# =========================================================

def extract_user_id_from_admin_message(message):
    if not message.reply_to_message:
        return None

    replied_text = (
        message.reply_to_message.text
        or message.reply_to_message.caption
        or ""
    )

    match = re.search(
        r"User ID:\s*(-?\d+)",
        replied_text
    )

    if not match:
        return None

    try:
        return int(match.group(1))
    except ValueError:
        return None


# =========================================================
# SEND TARIQ'S REPLY BACK TO USER
# =========================================================

async def send_admin_reply_to_user(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return False

    if not update.effective_user:
        return False

    if not is_admin(update.effective_user):
        return False

    if not update.message.reply_to_message:
        return False

    target_user_id = extract_user_id_from_admin_message(
        update.message
    )

    if not target_user_id:
        await update.message.reply_text(
            "⚠️ این Reply به پیام یک کاربر متصل نیست.\n\n"
            "لطفاً روی پیام «📩 پیام جدید از کاربر» "
            "Reply بزن."
        )
        return True

    try:

        # Copy Tariq's reply to the original user.
        await update.message.copy(
            chat_id=target_user_id
        )

        await update.message.reply_text(
            "✅ پاسخ برای کاربر ارسال شد."
        )

        logger.info(
            "Admin reply sent to user %s.",
            target_user_id
        )

    except Exception:
        logger.exception(
            "Could not send admin reply to user."
        )

        await update.message.reply_text(
            "❌ ارسال پاسخ انجام نشد.\n\n"
            "ممکن است کاربر ربات را بلاک کرده باشد "
            "یا حساب او در دسترس نباشد."
        )

    return True


# =========================================================
# MAIN MESSAGE ROUTER
# =========================================================

async def message_router(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message:
        return

    if not update.effective_user:
        return

    # -----------------------------------------------------
    # 1. ADMIN REPLY
    # -----------------------------------------------------

    if is_admin(update.effective_user):

        handled = await send_admin_reply_to_user(
            update,
            context
        )

        if handled:
            return

    # -----------------------------------------------------
    # 2. MENU BUTTONS
    # -----------------------------------------------------

    text = update.message.text or ""

    if text == "👤 مشخصات طارق":
        await profile(update, context)
        return

    if text == "💌 ارسال پیام":
        await start_sending(update, context)
        return

    if text == "🤖 درباره ربات":
        await about_bot(update, context)
        return

    if text == "❓ راهنما":
        await help_menu(update, context)
        return

    # -----------------------------------------------------
    # 3. USER MESSAGE
    # -----------------------------------------------------

    if context.user_data.get(
        "waiting_message",
        False
    ):
        await send_user_message_to_admin(
            update,
            context
        )
        return

    # -----------------------------------------------------
    # 4. UNKNOWN MESSAGE
    # -----------------------------------------------------

    await update.message.reply_text(
        "برای ارسال پیام به طارق، "
        "از گزینه «💌 ارسال پیام» استفاده کن.",
        reply_markup=main_menu()
    )


# =========================================================
# BOT POST INIT
# =========================================================

async def post_init(
    application: Application
):

    await application.bot.set_my_commands(
        [
            (
                "start",
                "شروع ربات"
            ),
            (
                "help",
                "راهنما"
            ),
            (
                "myid",
                "شناسه کاربری"
            ),
        ]
    )

    logger.info(
        "Bot commands configured successfully."
    )


# =========================================================
# MAIN
# =========================================================

def main():

    # -----------------------------------------------------
    # Start HTTP server for Render
    # -----------------------------------------------------

    server_thread = threading.Thread(
        target=run_web_server,
        daemon=True
    )

    server_thread.start()

    logger.info(
        "HTTP server started on port %s",
        PORT
    )

    # -----------------------------------------------------
    # Create Telegram application
    # -----------------------------------------------------

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # -----------------------------------------------------
    # Commands
    # -----------------------------------------------------

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CommandHandler(
            "help",
            help_menu
        )
    )

    application.add_handler(
        CommandHandler(
            "myid",
            my_id
        )
    )

    # -----------------------------------------------------
    # All normal Telegram messages
    # -----------------------------------------------------

    application.add_handler(
        MessageHandler(
            filters.ALL & ~filters.COMMAND,
            message_router
        )
    )

    logger.info(
        "%s is starting...",
        BOT_NAME
    )

    # -----------------------------------------------------
    # Telegram long polling
    # -----------------------------------------------------

    application.run_polling(
        drop_pending_updates=False
    )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()
