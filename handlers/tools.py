import ast
import base64
import hashlib
import json
import secrets
import string
import urllib.request
import urllib.error
from datetime import datetime, timezone
from io import BytesIO

import qrcode

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from database import save_tool_history


# =========================================================
# CALCULATOR
# =========================================================

ALLOWED_OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a ** b,
}


def safe_calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Expression):
            return evaluate(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise ValueError("Invalid value")

        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)

            if isinstance(node.op, ast.USub):
                return -value

            if isinstance(node.op, ast.UAdd):
                return value

            raise ValueError("Invalid operator")

        if isinstance(node, ast.BinOp):
            left = evaluate(node.left)
            right = evaluate(node.right)
            operator = type(node.op)

            if operator not in ALLOWED_OPERATORS:
                raise ValueError("Invalid operator")

            if operator is ast.Pow and abs(right) > 100:
                raise ValueError("Exponent too large")

            return ALLOWED_OPERATORS[operator](left, right)

        raise ValueError("Invalid expression")

    return evaluate(tree)


# =========================================================
# TOOLS CENTER
# =========================================================

def tools_keyboard():
    keyboard = [
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
    ]

    return InlineKeyboardMarkup(keyboard)


async def tools_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    await update.message.reply_text(
        "🧰 DIVICORE DEVELOPER TOOLKIT\n\n"
        "A collection of useful developer utilities.\n\n"
        "Choose a tool below:",
        reply_markup=tools_keyboard()
    )


# =========================================================
# CALCULATOR
# =========================================================

async def calculator(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "🧮 CALCULATOR\n\n"
            "Usage:\n\n"
            "/calc 25 * 4\n"
            "/calc 1000 / 8\n"
            "/calc (50 + 20) * 2"
        )
        return

    expression = " ".join(context.args)

    try:
        result = safe_calculate(expression)

        save_tool_history(
            update.effective_user.id,
            "Calculator",
            expression,
            result
        )

        await update.message.reply_text(
            f"🧮 CALCULATION\n\n"
            f"Expression:\n"
            f"`{expression}`\n\n"
            f"Result:\n"
            f"`{result}`",
            parse_mode="Markdown"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Invalid calculation.\n\n"
            "Example:\n"
            "/calc (25 + 5) * 4"
        )


# =========================================================
# PASSWORD GENERATOR
# =========================================================

async def password_generator(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    length = 16

    if context.args:
        try:
            length = int(context.args[0])

        except ValueError:
            await update.message.reply_text(
                "❌ Password length must be a number.\n\n"
                "Example:\n"
                "/password 24"
            )
            return

    if length < 8:
        await update.message.reply_text(
            "⚠️ Minimum password length is 8."
        )
        return

    if length > 128:
        await update.message.reply_text(
            "⚠️ Maximum password length is 128."
        )
        return

    characters = (
        string.ascii_letters
        + string.digits
        + string.punctuation
    )

    password = "".join(
        secrets.choice(characters)
        for _ in range(length)
    )

    save_tool_history(
        update.effective_user.id,
        "Password Generator",
        f"Length: {length}",
        password
    )

    await update.message.reply_text(
        f"🔐 PASSWORD GENERATOR\n\n"
        f"Password:\n\n"
        f"`{password}`\n\n"
        f"📏 Length: {length}\n"
        f"💪 Strength: Strong\n\n"
        f"⚠️ Store it securely.",
        parse_mode="Markdown"
    )


# =========================================================
# BASE64 ENCODE
# =========================================================

async def base64_encode(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "🔤 BASE64 ENCODER\n\n"
            "Usage:\n"
            "/base64encode Hello World"
        )
        return

    text = " ".join(context.args)

    encoded = base64.b64encode(
        text.encode("utf-8")
    ).decode("utf-8")

    save_tool_history(
        update.effective_user.id,
        "Base64 Encode",
        text,
        encoded
    )

    await update.message.reply_text(
        f"🔤 BASE64 ENCODED\n\n"
        f"Input:\n"
        f"`{text}`\n\n"
        f"Output:\n"
        f"`{encoded}`",
        parse_mode="Markdown"
    )


# =========================================================
# BASE64 DECODE
# =========================================================

async def base64_decode(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "🔓 BASE64 DECODER\n\n"
            "Usage:\n"
            "/base64decode SGVsbG8="
        )
        return

    encoded = "".join(context.args)

    try:
        decoded = base64.b64decode(
            encoded,
            validate=True
        ).decode("utf-8")

        save_tool_history(
            update.effective_user.id,
            "Base64 Decode",
            encoded,
            decoded
        )

        await update.message.reply_text(
            f"🔓 BASE64 DECODED\n\n"
            f"Input:\n"
            f"`{encoded}`\n\n"
            f"Output:\n"
            f"`{decoded}`",
            parse_mode="Markdown"
        )

    except Exception:
        await update.message.reply_text(
            "❌ Invalid Base64 input."
        )


# =========================================================
# JSON FORMATTER
# =========================================================

async def json_formatter(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "📋 JSON FORMATTER\n\n"
            "Usage:\n"
            '/json {"name":"Divinity","age":20}'
        )
        return

    raw_json = " ".join(context.args)

    try:
        data = json.loads(raw_json)

        formatted = json.dumps(
            data,
            indent=2,
            ensure_ascii=False
        )

        save_tool_history(
            update.effective_user.id,
            "JSON Formatter",
            raw_json,
            formatted
        )

        await update.message.reply_text(
            f"📋 FORMATTED JSON\n\n"
            f"```json\n{formatted}\n```",
            parse_mode="Markdown"
        )

    except json.JSONDecodeError:
        await update.message.reply_text(
            "❌ Invalid JSON.\n\n"
            "Example:\n"
            '/json {"name":"Divinity","age":20}'
        )


# =========================================================
# TIMESTAMP
# =========================================================

async def timestamp_converter(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        now = datetime.now(timezone.utc)
        unix_time = int(now.timestamp())

        output = (
            f"Current UTC: "
            f"{now.strftime('%Y-%m-%d %H:%M:%S')} | "
            f"Unix: {unix_time}"
        )

        save_tool_history(
            update.effective_user.id,
            "Timestamp",
            "Current time",
            output
        )

        await update.message.reply_text(
            f"🕐 TIMESTAMP\n\n"
            f"Current UTC:\n"
            f"`{now.strftime('%Y-%m-%d %H:%M:%S')}`\n\n"
            f"Unix timestamp:\n"
            f"`{unix_time}`",
            parse_mode="Markdown"
        )

        return

    value = context.args[0]

    try:
        unix_time = int(value)

        converted = datetime.fromtimestamp(
            unix_time,
            timezone.utc
        )

        output = converted.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        save_tool_history(
            update.effective_user.id,
            "Timestamp",
            unix_time,
            output
        )

        await update.message.reply_text(
            f"🕐 TIMESTAMP CONVERTER\n\n"
            f"Unix:\n"
            f"`{unix_time}`\n\n"
            f"UTC:\n"
            f"`{output}`",
            parse_mode="Markdown"
        )

    except ValueError:
        await update.message.reply_text(
            "❌ Invalid timestamp.\n\n"
            "Example:\n"
            "/timestamp 1750000000"
        )


# =========================================================
# QR GENERATOR
# =========================================================

async def qr_generator(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "📱 QR GENERATOR\n\n"
            "Usage:\n"
            "/qr https://devdivinity.netlify.app"
        )
        return

    data = " ".join(context.args)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=4
    )

    qr.add_data(data)
    qr.make(fit=True)

    image = qr.make_image()

    image_bytes = BytesIO()

    image.save(
        image_bytes,
        format="PNG"
    )

    image_bytes.seek(0)

    save_tool_history(
        update.effective_user.id,
        "QR Generator",
        data,
        "QR code generated"
    )

    await update.message.reply_photo(
        photo=image_bytes,
        caption=f"📱 QR CODE\n\n{data}"
    )


# =========================================================
# URL CHECKER
# =========================================================

async def url_checker(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "🌐 URL CHECKER\n\n"
            "Usage:\n"
            "/url https://example.com"
        )
        return

    url = context.args[0]

    if not url.startswith(
        ("http://", "https://")
    ):
        url = "https://" + url

    try:
        request = urllib.request.Request(
            url,
            method="HEAD",
            headers={
                "User-Agent": "DiviCore/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            output = (
                f"Online | HTTP {response.status} | "
                f"{response.url}"
            )

            save_tool_history(
                update.effective_user.id,
                "URL Checker",
                url,
                output
            )

            await update.message.reply_text(
                f"🌐 URL CHECKER\n\n"
                f"URL:\n{url}\n\n"
                f"🟢 Status: Online\n"
                f"📡 HTTP Status: {response.status}\n"
                f"🔗 Final URL:\n{response.url}"
            )

    except urllib.error.HTTPError as error:
        output = f"Server responded | HTTP {error.code}"

        save_tool_history(
            update.effective_user.id,
            "URL Checker",
            url,
            output
        )

        await update.message.reply_text(
            f"🌐 URL CHECKER\n\n"
            f"URL:\n{url}\n\n"
            f"🟠 Server responded\n"
            f"📡 HTTP Status: {error.code}"
        )

    except Exception:
        await update.message.reply_text(
            f"🌐 URL CHECKER\n\n"
            f"URL:\n{url}\n\n"
            f"🔴 Could not connect."
        )


# =========================================================
# IP INFORMATION
# =========================================================

async def ip_information(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "🌍 IP INFORMATION\n\n"
            "Usage:\n"
            "/ipinfo 8.8.8.8"
        )
        return

    ip = context.args[0]

    api_url = (
        f"https://ipapi.co/{ip}/json/"
    )

    try:
        request = urllib.request.Request(
            api_url,
            headers={
                "User-Agent": "DiviCore/1.0"
            }
        )

        with urllib.request.urlopen(
            request,
            timeout=10
        ) as response:

            data = json.loads(
                response.read().decode()
            )

        if data.get("error"):
            await update.message.reply_text(
                "❌ Could not find information "
                "for that IP."
            )
            return

        output = (
            f"Country: {data.get('country_name', 'Unknown')}\n"
            f"City: {data.get('city', 'Unknown')}\n"
            f"ISP: {data.get('org', 'Unknown')}"
        )

        save_tool_history(
            update.effective_user.id,
            "IP Information",
            ip,
            output
        )

        await update.message.reply_text(
            f"""🌍 IP INFORMATION

🆔 IP: {data.get('ip', 'Unknown')}

🌎 Country: {data.get('country_name', 'Unknown')}
🏙️ City: {data.get('city', 'Unknown')}
📍 Region: {data.get('region', 'Unknown')}

🌐 ISP: {data.get('org', 'Unknown')}

🕐 Timezone: {data.get('timezone', 'Unknown')}

📡 Version: {data.get('version', 'Unknown')}"""
        )

    except Exception:
        await update.message.reply_text(
            "❌ Unable to retrieve IP "
            "information right now."
        )


# =========================================================
# SHA-256 HASH
# =========================================================

async def hash_generator(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not context.args:
        await update.message.reply_text(
            "🔢 SHA-256 HASH\n\n"
            "Usage:\n"
            "/hash Hello World"
        )
        return

    text = " ".join(context.args)

    hashed = hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()

    save_tool_history(
        update.effective_user.id,
        "SHA-256",
        text,
        hashed
    )

    await update.message.reply_text(
        f"#️⃣ SHA-256 HASH\n\n"
        f"Input:\n"
        f"`{text}`\n\n"
        f"SHA-256:\n"
        f"`{hashed}`",
        parse_mode="Markdown"
    )
