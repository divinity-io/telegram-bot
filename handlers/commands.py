from telegram import Update
from telegram.ext import ContextTypes

from database import get_user
from languages import get_text


def get_language(user_id):
    profile = get_user(user_id)

    if profile:
        return profile[0].get("language", "English")

    return "English"


async def help_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    language = get_language(user.id)

    help_text = f"""{get_text('help', language)}

🤖 DiviCore Commands

/start
→ Register your account and start DiviCore.

/menu
→ Open the DiviCore Control Center.

/help
→ Show this help page.

/about
→ Learn about DiviCore, how it works, and its developer.

⚙️ Control Center

👤 Profile
→ View your DiviCore account information.

⚙️ Settings
→ Manage your DiviCore preferences.

🔔 Notifications
→ Turn notifications ON or OFF.

🌐 Language
→ Change the language used by DiviCore.

ℹ️ About
→ Learn more about the project and its developer.

🚀 DiviCore
→ Check the current bot status.

💡 Tip

You can use the buttons inside /menu to navigate DiviCore without typing commands.

🚀 More features will be added as DiviCore continues to grow.
"""

    await update.message.reply_text(help_text)


async def about_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    language = get_language(user.id)

    await update.message.reply_text(
        get_text("about", language)
    )
