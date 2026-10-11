from supabase import create_client
from config import SUPABASE_URL, SUPABASE_KEY


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)


# =========================================================
# USERS
# =========================================================

def save_user(user):
    data = {
        "telegram_id": user.id,
        "username": user.username,
        "first_name": user.first_name
    }

    response = (
        supabase
        .table("users")
        .upsert(
            data,
            on_conflict="telegram_id"
        )
        .execute()
    )

    return response


def get_user(telegram_id):
    response = (
        supabase
        .table("users")
        .select("*")
        .eq("telegram_id", telegram_id)
        .execute()
    )

    return response.data


def update_notifications(
    telegram_id,
    enabled
):
    response = (
        supabase
        .table("users")
        .update({
            "notifications": enabled
        })
        .eq("telegram_id", telegram_id)
        .execute()
    )

    return response.data


def update_language(
    telegram_id,
    language
):
    response = (
        supabase
        .table("users")
        .update({
            "language": language
        })
        .eq("telegram_id", telegram_id)
        .execute()
    )

    return response.data


# =========================================================
# TOOL HISTORY
# =========================================================

def save_tool_history(
    telegram_id,
    tool_name,
    input_data,
    output_data
):
    data = {
        "telegram_id": telegram_id,
        "tool_name": tool_name,
        "input_data": str(input_data),
        "output_data": str(output_data)
    }

    response = (
        supabase
        .table("tool_history")
        .insert(data)
        .execute()
    )

    return response.data


def get_tool_history(
    telegram_id,
    limit=10
):
    response = (
        supabase
        .table("tool_history")
        .select("*")
        .eq("telegram_id", telegram_id)
        .order(
            "created_at",
            desc=True
        )
        .limit(limit)
        .execute()
    )

    return response.data


def clear_tool_history(
    telegram_id
):
    response = (
        supabase
        .table("tool_history")
        .delete()
        .eq("telegram_id", telegram_id)
        .execute()
    )

    return response.data


# =========================================================
# ADMIN / BROADCAST
# =========================================================

def get_all_users():
    response = (
        supabase
        .table("users")
        .select("telegram_id")
        .order("telegram_id")
        .execute()
    )

    return response.data
