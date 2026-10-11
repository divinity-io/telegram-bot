
import asyncio
import logging

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.error import Forbidden, BadRequest, RetryAfter, TelegramError

from config import ADMIN_ID
from database import (
    get_all_users,
    save_broadcast_history,
    get_broadcast_history,
)
logger = logging.getLogger(__name__)

PENDING_BROADCAST = "admin_pending_broadcast"
WAITING_FOR_BROADCAST = "admin_waiting_for_broadcast"


def is_admin(update: Update) -> bool:
    user = update.effective_user
    return bool(user and ADMIN_ID and user.id == ADMIN_ID)


def admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "📊 Dashboard",
                callback_data="admin:stats",
            ),
        ],
        [
            InlineKeyboardButton(
                "📢 New broadcast",
                callback_data="admin:broadcast",
            ),
        ],
        [
            InlineKeyboardButton(
                "🗂️ Broadcast history",
                callback_data="admin:history",
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ Close",
                callback_data="admin:close",
            ),
        ],
    ])

async def admin_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not is_admin(update):
        await update.effective_message.reply_text(
            "⛔ You are not authorized to access this panel."
        )
        return

    context.user_data.pop(WAITING_FOR_BROADCAST, None)
    context.user_data.pop(PENDING_BROADCAST, None)

    await update.effective_message.reply_text(
        "🛡️ DiviCore Admin Panel\n\n"
        "Manage registered users and send announcements.",
        reply_markup=admin_keyboard(),
    )


async def admin_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if query is None:
        return

    if not is_admin(update):
        await query.answer("Access denied.", show_alert=True)
        return

    await query.answer()
    action = query.data

    if action == "admin:close":
        context.user_data.pop(WAITING_FOR_BROADCAST, None)
        context.user_data.pop(PENDING_BROADCAST, None)
        await query.edit_message_text("Admin panel closed.")
        return

    if action == "admin:history":
        try:
            records = get_broadcast_history(limit=10)
        except Exception:
            logger.exception("Unable to load broadcast history")
            await query.edit_message_text(
                "⚠️ Could not load broadcast history. "
                "Check your Supabase connection and table."
            )
            return

        if not records:
            await query.edit_message_text(
                "🗂️ Broadcast History\n\n"
                "No broadcasts have been recorded yet.",
                reply_markup=admin_keyboard(),
            )
            return

        lines = ["🗂️ Recent Broadcasts\n"]
        for record in records:
            created = str(record.get("created_at", "Unknown date"))
            message = record.get("message", "")
            preview = message.replace("\n", " ")[:70]
            lines.append(
                f"📅 {created}\n"
                f"💬 {preview}\n"
                f"👥 Recipients: {record.get('total_recipients', 0)}\n"
                f"✅ Sent: {record.get('sent_count', 0)} | "
                f"🚫 Blocked: {record.get('blocked_count', 0)} | "
                f"⚠️ Failed: {record.get('failed_count', 0)}\n"
                f"Status: {record.get('status', 'unknown')}\n"
            )

        text = "\n".join(lines)
        await query.edit_message_text(
            text[:4000],
            reply_markup=admin_keyboard(),
        )
        return


    if action == "admin:stats":
        try:
            users = get_all_users() or []
            total_users = len(users)

            await query.edit_message_text(
                "📊 DiviCore Dashboard\n\n"
                f"👥 Registered users: {total_users}\n"
                "📢 Broadcasts: available below\n\n"
                "Choose an action:",
                reply_markup=admin_keyboard(),
            )
        except Exception:
            logger.exception("Unable to load admin dashboard")
            await query.edit_message_text(
                "⚠️ Could not load statistics. "
                "Check the Termux log for details."
            )
        return



    if action == "admin:broadcast":
        context.user_data[WAITING_FOR_BROADCAST] = True
        context.user_data.pop(PENDING_BROADCAST, None)

        await query.edit_message_text(
            "📢 New Broadcast\n\n"
            "Send the message you want to deliver to registered users.\n"
            "It will NOT be sent until you review and confirm it.\n\n"
            "Send /cancelbroadcast to cancel."
        )
        return

    if action == "admin:broadcast_confirm":
        message = context.user_data.get(PENDING_BROADCAST)

        if not message:
            await query.edit_message_text(
                "⚠️ No pending broadcast was found. Start again with /admin."
            )
            return

        context.user_data.pop(PENDING_BROADCAST, None)
        context.user_data.pop(WAITING_FOR_BROADCAST, None)

        try:
            users = get_all_users() or []
        except Exception:
            logger.exception("Unable to retrieve broadcast recipients")
            await query.edit_message_text(
                "⚠️ Could not retrieve recipients from Supabase. "
                "Nothing was sent."
            )
            return

        recipient_ids = []
        seen = set()

        for row in users:
            try:
                telegram_id = int(row["telegram_id"])
                if telegram_id not in seen:
                    seen.add(telegram_id)
                    recipient_ids.append(telegram_id)
            except (KeyError, TypeError, ValueError):
                logger.warning("Skipping invalid user row: %r", row)

        await query.edit_message_text(
            f"📤 Broadcast started for {len(recipient_ids)} registered users..."
        )

        sent = 0
        failed = 0
        blocked_or_unavailable = 0

        for telegram_id in recipient_ids:
            try:
                await context.bot.send_message(
                    chat_id=telegram_id,
                    text=message,
                )
                sent += 1
                await asyncio.sleep(0.05)

            except RetryAfter as exc:
                wait_seconds = float(exc.retry_after) + 1
                await asyncio.sleep(wait_seconds)
                try:
                    await context.bot.send_message(
                        chat_id=telegram_id,
                        text=message,
                    )
                    sent += 1
                except Forbidden:
                    blocked_or_unavailable += 1
                except TelegramError:
                    failed += 1

            except Forbidden:
                blocked_or_unavailable += 1

            except BadRequest as exc:
                logger.warning(
                    "Broadcast failed for user %s: %s",
                    telegram_id,
                    exc,
                )
                failed += 1

            except TelegramError:
                logger.exception(
                    "Telegram delivery failed for user %s",
                    telegram_id,
                )
                failed += 1

        await query.message.reply_text(
            "✅ Broadcast finished\n\n"
            f"👥 Recipients: {len(recipient_ids)}\n"
            f"✅ Sent: {sent}\n"
            f"🚫 Blocked/unavailable: {blocked_or_unavailable}\n"
            f"⚠️ Other failures: {failed}",
            reply_markup=admin_keyboard(),
        )
        try:
            save_broadcast_history(
                admin_telegram_id=update.effective_user.id,
                message=message,
                total_recipients=len(recipient_ids),
                sent_count=sent,
                blocked_count=blocked_or_unavailable,
                failed_count=failed,
                status="completed",
            )
        except Exception:
            logger.exception("Failed to save broadcast history")
            await query.message.reply_text(
                "⚠️ Broadcast was sent, but its history could not be saved."
            )


async def handle_broadcast_text(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not is_admin(update):
        return

    if not context.user_data.get(WAITING_FOR_BROADCAST):
        return

    message = update.effective_message
    if message is None or not message.text:
        return

    if len(message.text) > 4096:
        await message.reply_text(
            "⚠️ Telegram messages can contain at most 4096 characters. "
            "Please shorten your broadcast."
        )
        return

    context.user_data.pop(WAITING_FOR_BROADCAST, None)
    context.user_data[PENDING_BROADCAST] = message.text

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Confirm and send",
                callback_data="admin:broadcast_confirm",
            ),
        ],
        [
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="admin:broadcast_cancel",
            ),
        ],
    ])

    await message.reply_text(
        "🔎 Broadcast Preview\n\n"
        "Review your message below. It has not been sent yet.\n\n"
        "──────────────\n"
        f"{message.text}\n"
        "──────────────\n\n"
        "Send this to all registered users?",
        reply_markup=keyboard,
    )


async def cancel_broadcast(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not is_admin(update):
        await update.effective_message.reply_text("⛔ Access denied.")
        return

    context.user_data.pop(WAITING_FOR_BROADCAST, None)
    context.user_data.pop(PENDING_BROADCAST, None)

    await update.effective_message.reply_text(
        "❌ Broadcast cancelled. Nothing was sent.",
        reply_markup=admin_keyboard(),
    )


async def cancel_broadcast_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query
    if query is None:
        return

    if not is_admin(update):
        await query.answer("Access denied.", show_alert=True)
        return

    context.user_data.pop(WAITING_FOR_BROADCAST, None)
    context.user_data.pop(PENDING_BROADCAST, None)

    await query.answer("Broadcast cancelled.")
    await query.edit_message_text(
        "❌ Broadcast cancelled. Nothing was sent.",
        reply_markup=admin_keyboard(),
    )


def register_admin_handlers(application) -> None:
    """Register DiviCore admin commands and callbacks."""
    application.add_handler(CommandHandler("admin", admin_command))
    application.add_handler(CommandHandler("cancelbroadcast", cancel_broadcast))
    application.add_handler(
        CallbackQueryHandler(
            cancel_broadcast_callback,
            pattern=r"^admin:broadcast_cancel$",
        )
    )
    application.add_handler(
        CallbackQueryHandler(
            admin_callback,
pattern=r"^admin:(stats|broadcast|history|close|broadcast_confirm)$",        )
    )

    # Use a later handler group so normal text handlers can run first.
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_broadcast_text,
        ),
        group=1,
    )

