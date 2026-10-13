from telegram import Update
from telegram.ext import ContextTypes

from handlers.start import dashboard_keyboard
from handlers.buttons import (
    get_language,
    main_menu_keyboard,
    tools_keyboard,
)
from database import get_user, get_tool_history


async def dashboard_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    message = update.effective_message
    user = update.effective_user
    if not message or not user:
        return

    text = (message.text or "").strip()
    language = get_language(user.id)

    if text == "🏠 Dashboard":
        profile = get_user(user.id)
        if not profile:
            await message.reply_text(
                "Please send /start first.",
                reply_markup=dashboard_keyboard(),
            )
            return

        data = profile[0]
        name = data.get("first_name") or user.first_name or "User"
        username = data.get("username")
        history = get_tool_history(user.id, 5) or []

        await message.reply_text(
            "🏠 DCORE PERSONAL DASHBOARD\n\n"
            f"👤 Welcome, {name}\n"
            f"🆔 Telegram ID: {user.id}\n"
            f"🔹 Username: @{username}" if username else
            "🏠 DCORE PERSONAL DASHBOARD\n\n"
            f"👤 Welcome, {name}\n"
            f"🆔 Telegram ID: {user.id}\n"
            "🔹 Username: Not set"
        )
        await message.reply_text(
            f"📊 Recent tool activity: {len(history)} item(s) shown in your recent history.\n\n"
            "Choose an option from the keyboard below.",
            reply_markup=dashboard_keyboard(),
        )
        return

    if text == "👤 My Profile":
        profile = get_user(user.id)
        if not profile:
            await message.reply_text(
                "Please send /start first.",
                reply_markup=dashboard_keyboard(),
            )
            return

        data = profile[0]
        username = data.get("username")
        await message.reply_text(
            "👤 MY DCORE PROFILE\n\n"
            f"Name: {data.get('first_name') or user.first_name or 'Unknown'}\n"
            f"Username: @{username}" if username else
            "👤 MY DCORE PROFILE\n\n"
            f"Name: {data.get('first_name') or user.first_name or 'Unknown'}\n"
            "Username: Not set"
        )
        await message.reply_text(
            f"🆔 Telegram ID: {user.id}\n"
            f"🌐 Language: {data.get('language', 'English')}\n"
            f"🔔 Notifications: {data.get('notifications', 'Not set')}",
            reply_markup=dashboard_keyboard(),
        )
        return

    if text == "🧰 Tools":
        await message.reply_text(
            "🧰 DCORE TOOLS\n\nChoose a tool:",
            reply_markup=tools_keyboard(),
        )
        return

    if text == "📜 History":
        history = get_tool_history(user.id, 10) or []
        if not history:
            await message.reply_text(
                "📜 Your tool history is empty.",
                reply_markup=dashboard_keyboard(),
            )
            return

        lines = ["📜 YOUR RECENT TOOL HISTORY\n"]
        for item in history:
            lines.append(
                f"• {item.get('tool_name', 'Tool')} — "
                f"{item.get('created_at', '')}"
            )
        await message.reply_text(
            "\n".join(lines),
            reply_markup=dashboard_keyboard(),
        )
        return

    if text == "⚙️ Settings":
        await message.reply_text(
            "⚙️ DCORE SETTINGS\n\nOpen /menu to manage your language and notifications.",
            reply_markup=dashboard_keyboard(),
        )
        await message.reply_text(
            "Open the detailed settings menu:",
            reply_markup=main_menu_keyboard(language),
        )
        return

    if text == "⭐ Favorites":
        await message.reply_text(
            "⭐ Favorites are not connected to the database yet.\n"
            "We'll add this after checking your existing favorites implementation.",
            reply_markup=dashboard_keyboard(),
        )
