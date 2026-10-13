from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import (
    get_user,
    update_notifications,
    update_language,
    get_tool_history,
    clear_tool_history,
)

from languages import get_text


# =========================================================
# LANGUAGE
# =========================================================

def get_language(user_id):
    profile = get_user(user_id)

    if profile:
        return profile[0].get("language", "English")

    return "English"


# =========================================================
# MAIN MENU KEYBOARD
# =========================================================

def main_menu_keyboard(language):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                get_text("profile_button", language),
                callback_data="profile"
            ),
            InlineKeyboardButton(
                get_text("settings_button", language),
                callback_data="settings"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text("help_button", language),
                callback_data="help"
            ),
            InlineKeyboardButton(
                get_text("about_button", language),
                callback_data="about"
            ),
        ],
        [
            InlineKeyboardButton(
                get_text("divicore_button", language),
                callback_data="divicore"
            ),
        ],
    ])


# =========================================================
# TOOLS KEYBOARD
# =========================================================

def tools_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🧮 Calculator",
                callback_data="tool_calc"
            ),
            InlineKeyboardButton(
                "🔐 Password",
                callback_data="tool_password"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔤 Base64",
                callback_data="tool_base64"
            ),
            InlineKeyboardButton(
                "📋 JSON",
                callback_data="tool_json"
            ),
        ],
        [
            InlineKeyboardButton(
                "🕐 Timestamp",
                callback_data="tool_timestamp"
            ),
            InlineKeyboardButton(
                "📱 QR Generator",
                callback_data="tool_qr"
            ),
        ],
        [
            InlineKeyboardButton(
                "🌐 URL Checker",
                callback_data="tool_url"
            ),
            InlineKeyboardButton(
                "🌍 IP Information",
                callback_data="tool_ip"
            ),
        ],
        [
            InlineKeyboardButton(
                "#️⃣ SHA-256",
                callback_data="tool_hash"
            ),
        ],
        [
            InlineKeyboardButton(
                "📚 History",
                callback_data="tool_history"
            ),
        ],
        [
            InlineKeyboardButton(
                "🔙 Main Menu",
                callback_data="back_menu"
            ),
        ],
    ])


# =========================================================
# SHOW MAIN MENU
# =========================================================

async def show_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    user = update.effective_user
    language = get_language(user.id)

    await update.message.reply_text(
        f"{get_text('menu', language)}\n\n"
        f"{get_text('choose_option', language)}",
        reply_markup=main_menu_keyboard(language)
    )


# =========================================================
# BUTTON HANDLER
# =========================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    query = update.callback_query

    await query.answer()

    user = query.from_user
    language = get_language(user.id)


    # =====================================================
    # CALCULATOR
    # =====================================================

    if query.data == "tool_calc":

        await query.edit_message_text(
            "🧮 CALCULATOR\n\n"
            "Use:\n\n"
            "`/calc 25 * 4`\n\n"
            "Examples:\n"
            "`/calc 1000 / 8`\n"
            "`/calc (50 + 20) * 2`",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # PASSWORD
    # =====================================================

    if query.data == "tool_password":

        await query.edit_message_text(
            "🔐 PASSWORD GENERATOR\n\n"
            "Generate a secure password:\n\n"
            "`/password 20`\n\n"
            "Length can be between 8 and 128 characters.",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # BASE64
    # =====================================================

    if query.data == "tool_base64":

        await query.edit_message_text(
            "🔤 BASE64 TOOLS\n\n"
            "Encode:\n"
            "`/base64encode Hello World`\n\n"
            "Decode:\n"
            "`/base64decode SGVsbG8=`",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # JSON
    # =====================================================

    if query.data == "tool_json":

        await query.edit_message_text(
            "📋 JSON FORMATTER\n\n"
            "Format JSON with:\n\n"
            '`/json {"name":"Divinity","age":20}`',
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # TIMESTAMP
    # =====================================================

    if query.data == "tool_timestamp":

        await query.edit_message_text(
            "🕐 TIMESTAMP CONVERTER\n\n"
            "Current timestamp:\n\n"
            "`/timestamp`\n\n"
            "Convert a Unix timestamp:\n\n"
            "`/timestamp 1750000000`",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # QR GENERATOR
    # =====================================================

    if query.data == "tool_qr":

        await query.edit_message_text(
            "📱 QR GENERATOR\n\n"
            "Generate a QR code:\n\n"
            "`/qr https://devdivinity.netlify.app`",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # URL CHECKER
    # =====================================================

    if query.data == "tool_url":

        await query.edit_message_text(
            "🌐 URL CHECKER\n\n"
            "Check a website:\n\n"
            "`/url https://example.com`",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # IP INFORMATION
    # =====================================================

    if query.data == "tool_ip":

        await query.edit_message_text(
            "🌍 IP INFORMATION\n\n"
            "Check an IP address:\n\n"
            "`/ipinfo 8.8.8.8`",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # SHA-256
    # =====================================================

    if query.data == "tool_hash":

        await query.edit_message_text(
            "#️⃣ SHA-256 HASH\n\n"
            "Generate a SHA-256 hash:\n\n"
            "`/hash Hello World`",
            parse_mode="Markdown",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # TOOL HISTORY
    # =====================================================

    if query.data == "tool_history":

        history = get_tool_history(
            user.id,
            10
        )

        if not history:

            await query.edit_message_text(
                "📚 TOOL HISTORY\n\n"
                "You haven't used any tools yet.",
                reply_markup=tools_keyboard()
            )

            return


        lines = [
            "📚 TOOL HISTORY",
            "",
            "Your latest 10 activities:",
            ""
        ]


        for item in history:

            tool = item.get(
                "tool_name",
                "Unknown"
            )

            input_data = item.get(
                "input_data",
                ""
            )

            created_at = item.get(
                "created_at",
                ""
            )


            if len(str(input_data)) > 60:
                input_data = (
                    str(input_data)[:57]
                    + "..."
                )


            lines.append(
                f"🔹 {tool}\n"
                f"   {input_data}\n"
                f"   🕐 {created_at}\n"
            )


        keyboard = [
            [
                InlineKeyboardButton(
                    "🗑️ Clear History",
                    callback_data="clear_history"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Tools",
                    callback_data="back_tools"
                )
            ],
        ]


        await query.edit_message_text(
            "\n".join(lines),
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


    # =====================================================
    # CLEAR HISTORY
    # =====================================================

    if query.data == "clear_history":

        clear_tool_history(
            user.id
        )

        await query.answer(
            "History cleared! 🗑️"
        )


        await query.edit_message_text(
            "📚 TOOL HISTORY\n\n"
            "✅ Your tool history has been cleared.",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # BACK TO TOOLS
    # =====================================================

    if query.data == "back_tools":

        await query.edit_message_text(
            "🧰 DCORE DEVELOPER TOOLKIT\n\n"
            "A collection of useful developer utilities.\n\n"
            "Choose a tool below:",
            reply_markup=tools_keyboard()
        )

        return


    # =====================================================
    # PROFILE
    # =====================================================

    if query.data == "profile":

        profile = get_user(
            user.id
        )


        if not profile:

            await query.edit_message_text(
                "⚠️ Profile not found.\n\n"
                "Please use /start first."
            )

            return


        data = profile[0]


        username = data.get(
            "username"
        ) or "Not set"

        first_name = data.get(
            "first_name"
        ) or "Unknown"

        telegram_id = data.get(
            "telegram_id"
        )

        created_at = data.get(
            "created_at",
            "Unknown"
        )


        await query.edit_message_text(
            f"{get_text('profile', language)}\n\n"
            "━━━━━━━━━━━━━━━━\n"
            f"👤 Name: {first_name}\n"
            f"🔹 Username: @{username}\n"
            f"🆔 Telegram ID: {telegram_id}\n"
            f"📅 Joined: {created_at}\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "🟢 Account Status: Active",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        get_text(
                            "back_button",
                            language
                        ),
                        callback_data="back_menu"
                    )
                ]
            ])
        )

        return


    # =====================================================
    # SETTINGS
    # =====================================================

    if query.data == "settings":

        keyboard = [
            [
                InlineKeyboardButton(
                    get_text(
                        "notifications",
                        language
                    ),
                    callback_data="notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text(
                        "language",
                        language
                    ),
                    callback_data="language"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text(
                        "back_button",
                        language
                    ),
                    callback_data="back_menu"
                )
            ],
        ]


        await query.edit_message_text(
            f"{get_text('settings', language)}\n\n"
            f"{get_text('choose_option', language)}",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


    # =====================================================
    # NOTIFICATIONS
    # =====================================================

    if query.data == "notifications":

        profile = get_user(
            user.id
        )


        if not profile:

            await query.edit_message_text(
                "⚠️ Profile not found.\n\n"
                "Please use /start first."
            )

            return


        enabled = profile[0].get(
            "notifications",
            True
        )


        status = (
            get_text(
                "notifications_on",
                language
            )
            if enabled
            else get_text(
                "notifications_off",
                language
            )
        )


        button_text = (
            get_text(
                "turn_off",
                language
            )
            if enabled
            else get_text(
                "turn_on",
                language
            )
        )


        keyboard = [
            [
                InlineKeyboardButton(
                    button_text,
                    callback_data="toggle_notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text(
                        "back_button",
                        language
                    ),
                    callback_data="settings"
                )
            ],
        ]


        await query.edit_message_text(
            f"{get_text('notifications', language)}\n\n"
            f"Status: {status}\n\n"
            f"{get_text('choose_option', language)}",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


    # =====================================================
    # TOGGLE NOTIFICATIONS
    # =====================================================

    if query.data == "toggle_notifications":

        profile = get_user(
            user.id
        )


        if not profile:

            await query.answer(
                "Profile not found."
            )

            return


        current = profile[0].get(
            "notifications",
            True
        )

        new_value = not current


        update_notifications(
            user.id,
            new_value
        )


        status = (
            get_text(
                "notifications_on",
                language
            )
            if new_value
            else get_text(
                "notifications_off",
                language
            )
        )


        button_text = (
            get_text(
                "turn_off",
                language
            )
            if new_value
            else get_text(
                "turn_on",
                language
            )
        )


        keyboard = [
            [
                InlineKeyboardButton(
                    button_text,
                    callback_data="toggle_notifications"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text(
                        "back_button",
                        language
                    ),
                    callback_data="settings"
                )
            ],
        ]


        await query.answer(
            "✅ Saved!"
        )


        await query.edit_message_text(
            f"{get_text('notifications', language)}\n\n"
            f"Status: {status}\n\n"
            f"{get_text('saved', language)}",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


    # =====================================================
    # LANGUAGE
    # =====================================================

    if query.data == "language":

        keyboard = [
            [
                InlineKeyboardButton(
                    "🇬🇧 English",
                    callback_data="language_English"
                )
            ],
            [
                InlineKeyboardButton(
                    "🇳🇬 Igbo",
                    callback_data="language_Igbo"
                )
            ],
            [
                InlineKeyboardButton(
                    "🇳🇬 Hausa",
                    callback_data="language_Hausa"
                )
            ],
            [
                InlineKeyboardButton(
                    "🇳🇬 Yoruba",
                    callback_data="language_Yoruba"
                )
            ],
            [
                InlineKeyboardButton(
                    get_text(
                        "back_button",
                        language
                    ),
                    callback_data="settings"
                )
            ],
        ]


        await query.edit_message_text(
            f"{get_text('language', language)}\n\n"
            f"{get_text('select_language', language)}",
            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return


    # =====================================================
    # CHANGE LANGUAGE
    # =====================================================

    if query.data.startswith(
        "language_"
    ):

        new_language = query.data.replace(
            "language_",
            ""
        )


        update_language(
            user.id,
            new_language
        )


        language = new_language


        await query.answer(
            "Language saved! ✅"
        )


        await query.edit_message_text(
            f"{get_text('language', language)}\n\n"
            f"{get_text('select_language', language)}\n\n"
            f"{get_text('language_saved', language)}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        get_text(
                            "back_button",
                            language
                        ),
                        callback_data="back_menu"
                    )
                ]
            ])
        )

        return


    # =====================================================
    # HELP
    # =====================================================

    if query.data == "help":

        await query.edit_message_text(
            f"{get_text('help', language)}\n\n"
            "/start — Start DCORE\n"
            "/help — Show help\n"
            "/about — About DCORE\n"
            "/menu — Open the control center\n"
            "/tools — Open Developer Toolkit",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        get_text(
                            "back_button",
                            language
                        ),
                        callback_data="back_menu"
                    )
                ]
            ])
        )

        return


    # =====================================================
    # ABOUT
    # =====================================================

    if query.data == "about":

        await query.edit_message_text(
            get_text(
                "about",
                language
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🌐 Portfolio",
                        url="https://devdivinity.netlify.app/"
                    ),
                    InlineKeyboardButton(
                        "💻 GitHub",
                        url="https://github.com/divinity-io"
                    )
                ],
                [
                    InlineKeyboardButton(
                        get_text(
                            "back_button",
                            language
                        ),
                        callback_data="back_menu"
                    )
                ]
            ])
        )

        return


    # =====================================================
    # DCORE STATUS
    # =====================================================

    if query.data == "divicore":

        await query.edit_message_text(
            f"{get_text('online', language)}\n\n"
            "System status: 🟢 Online",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        get_text(
                            "back_button",
                            language
                        ),
                        callback_data="back_menu"
                    )
                ]
            ])
        )

        return


    # =====================================================
    # BACK TO MAIN MENU
    # =====================================================

    if query.data == "back_menu":

        language = get_language(
            user.id
        )


        await query.edit_message_text(
            f"{get_text('menu', language)}\n\n"
            f"{get_text('choose_option', language)}",
            reply_markup=main_menu_keyboard(
                language
            )
        )

        return
