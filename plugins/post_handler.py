import asyncio
import logging
import re

from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    Message,
)
from pyrogram.errors import MessageNotModified, MessageTooLong

from plugins.Dreamxfutures.Imdbposter import get_movie_detailsx
from info import ADMINS, MOVIE_UPDATE_CHANNEL, ABOVE_PREVIEW
from utils import temp


# ============================================================
# ProviderBotz — Movie Post Generator
# ============================================================

logger = logging.getLogger(__name__)
post_sessions = {}

USE_GETFILE_BUTTON_BY_DEFAULT = True

DEFAULT_WATERMARK = "Join [ProviderBotz](https://t.me/ProviderBotz)"

LANGUAGES_FORMAT = "➥ <b>Languages :</b> <code>{langs}</code>"
RESOLUTIONS_FORMAT = "\n➥ <b>Qualities :</b> <code>{resolutions}</code>"
OTT_FORMAT = "\n➥ <b>Available on :</b> <code>{otts}</code>"


# ============================================================
# Button Styles
# ============================================================

PRIMARY = enums.ButtonStyle.PRIMARY
SUCCESS = enums.ButtonStyle.SUCCESS
DANGER = enums.ButtonStyle.DANGER


BUTTON_STYLES = {
    "PRIMARY": PRIMARY,
    "SUCCESS": SUCCESS,
    "DANGER": DANGER,
}


def make_button(text, callback_data=None, url=None, style="PRIMARY"):
    """
    Create a styled Telegram button.
    """

    kwargs = {
        "text": text,
        "style": BUTTON_STYLES.get(style, PRIMARY),
    }

    if callback_data is not None:
        kwargs["callback_data"] = callback_data

    if url is not None:
        kwargs["url"] = url

    return InlineKeyboardButton(**kwargs)


def render_custom_buttons(buttons):
    """
    Convert saved custom button dictionaries into
    Pyrogram InlineKeyboardButton objects.
    """

    keyboard = []

    for row in buttons or []:
        new_row = []

        for button in row:
            if isinstance(button, dict):
                new_row.append(
                    make_button(
                        text=button.get("text", "Button"),
                        url=button.get("url"),
                        style=button.get("style", "PRIMARY"),
                    )
                )

            # Backward compatibility for old button objects
            elif isinstance(button, InlineKeyboardButton):
                new_row.append(button)

        if new_row:
            keyboard.append(new_row)

    return keyboard


def button_style_name(style):
    return {
        "PRIMARY": "🔵 Primary",
        "SUCCESS": "🟢 Success",
        "DANGER": "🔴 Danger",
    }.get(style, "🔵 Primary")


# ============================================================
# Templates
# ============================================================

TEMPLATES = {
    "classic_emoji": """<b>{title} ({year})</b>
⭐️ <b>Rating:</b> {rating}/10
🎭 <b>Genre:</b> {genres}
💬 <b>Plot:</b> {plot}""",

    "minimalist": """🎬 <b>{title}</b>
🗓 <b>Year:</b> {year}
🌟 <b>Rating:</b> {rating}""",

    "sparkle_header": """✨ <b>{title}</b> ✨

<b>🗓 Year:</b> {year} | <b>⭐️ Rating:</b> {rating}/10
<b>🎭 Genres:</b> {genres}

<i>{plot}</i>""",

    "markdown_style": """🎥 **{title}** ({year})

- **Rating**: {rating} / 10 🌟
- **Genres**: {genres}

**Plot Summary**:
{plot}""",

    "divider_list": """🎬 <b>{title} {year}</b>
━━━━━━━━━━━━━━━━━━
➥ <b>Rating :</b> <code>★ {rating}/10</code>
➥ <b>Genres :</b> <code>{genres}</code>
""",

    "dashed_box": """- - - - - - - - - - - - - - - - - -
🎥 <b>{title}</b>
- - - - - - - - - - - - - - - - - -

➛ <b>Year ∥</b> {year}
➛ <b>Rating ∥</b> {rating}/10
➛ <b>Genres ∥</b> {genres}

<b><u>Synopsis</u></b>
<i>{plot}</i>""",

    "chevron_details": """<b>{title}</b>

» <b>Year ➣</b> {year}
» <b>Rating ➣</b> ★ {rating}/10
» <b>Genres ➣</b> {genres}

<b>∥ PLOT ∥</b>
└─ <i>{plot}</i>""",

    "bullet_points": """✨ <b><u>{title} ({year})</u></b> ✨

● <b>Rating :</b> {rating}/10
● <b>Genres :</b> {genres}

<b>💬 Plot Summary ➥</b>
<i>{plot}</i>""",

    "clean_grid": """🎬 {title} ({year})

🗓️ <b>Year ∥</b> {year}
⭐️ <b>Rating ∥</b> {rating}/10
🎭 <b>Genres ∥</b> {genres}

➣ <i>{plot}</i>"""
}


# ============================================================
# Data
# ============================================================

LANGUAGES = [
    "Bengali", "English", "Gujarati", "Hindi", "Kannada",
    "Malayalam", "Marathi", "Punjabi", "Tamil", "Telugu", "Urdu",
    "Arabic", "French", "German", "Italian", "Japanese",
    "Korean", "Mandarin", "Portuguese", "Russian", "Spanish"
]

RESOLUTIONS = [
    "144p", "240p", "480p", "720p", "1080p", "1440p",
    "2160p", "4320p",
    "BluRay", "BDRip", "WEB-DL", "VOD", "WEBRip", "HDTV",
    "DVDRip", "DVDScr", "TS", "CAM",
    "AV1", "HEVC", "x264"
]

OTT_PLATFORMS = [
    "Aha",
    "ALTBalaji",
    "JioHotstar",
    "Eros Now",
    "Hoichoi",
    "JioCinema",
    "MX Player",
    "SonyLIV",
    "Sun NXT",
    "Voot",
    "Zee5",
    "Amazon Prime Video",
    "Apple TV+",
    "Crunchyroll",
    "Discovery+",
    "HBO Max",
    "Hulu",
    "Netflix",
    "Paramount+",
    "Peacock",
    "YouTube Premium"
]


# ============================================================
# /post
# ============================================================

@Client.on_message(filters.command("post") & filters.user(ADMINS), group=-4)
async def post_command(client: Client, message: Message):

    if len(message.command) == 1:
        return await message.reply_text(
            "Please provide a movie name.\n\n"
            "Usage: `/post The Dark Knight`"
        )

    movie_name = " ".join(message.command[1:])
    user_id = message.from_user.id

    logger.info(
        f"User {user_id} initiated post for '{movie_name}'"
    )

    await start_post_session(
        client,
        message,
        user_id,
        movie_name
    )


# ============================================================
# Start Session
# ============================================================

async def start_post_session(
    client: Client,
    message: Message,
    user_id: int,
    movie_name: str
):

    movie_details = await get_movie_detailsx(movie_name)

    if not movie_details:
        return await message.reply_text(
            "Could not fetch details for the movie."
        )

    logger.info(
        f"User {user_id} is starting post session for '{movie_name}'."
    )

    if (
        user_id in post_sessions
        and post_sessions[user_id].get("last_preview_message_id")
    ):
        try:
            await client.delete_messages(
                message.chat.id,
                post_sessions[user_id]["last_preview_message_id"]
            )
        except Exception:
            pass

    post_sessions[user_id] = {
        "movie_name": movie_name,
        "caption": None,

        # Custom buttons are now dictionaries.
        "buttons": [],

        "photo_mode": False,

        "use_landscape": (
            True if movie_details.get("backdrop_url") else False
        ),

        "custom_languages": [],
        "custom_resolutions": [],
        "custom_otts": [],

        "last_preview_message_id": None,
        "original_message_id": message.id,

        "custom_poster": None,

        "watermark": DEFAULT_WATERMARK,

        "lang_format": LANGUAGES_FORMAT,
        "ott_format": OTT_FORMAT,
        "res_format": RESOLUTIONS_FORMAT,

        "active_template": "divider_list",

        "movie_details": movie_details,
    }

    # --------------------------------------------------------
    # Default Get Files Button
    # --------------------------------------------------------

    if USE_GETFILE_BUTTON_BY_DEFAULT:

        title = movie_details.get("title", "movie")
        year = movie_details.get("year", "")

        movie_year = f"{title} {year}".strip()
        movie_year = re.sub(r"[ *:\.]", "-", movie_year)

        url = (
            f"https://telegram.me/{temp.U_NAME}"
            f"?start=getfile-{movie_year}"
        )

        post_sessions[user_id]["buttons"].append([
            {
                "text": "📥 Get Files 📥",
                "url": url,
                "style": "SUCCESS",
            }
        ])

        logger.info(
            f"Default Get Files button added for session {user_id}"
        )

    await update_post_preview(
        client,
        user_id,
        message.chat.id,
        force_resend=True
    )


# ============================================================
# Final Caption
# ============================================================

async def _build_final_post_content(
    session: dict,
    session_id: int
):

    movie_details = session["movie_details"]

    if not movie_details:
        return None, None, None

    if not session.get("caption"):

        session["caption"] = TEMPLATES[
            session["active_template"]
        ].format(
            title=movie_details.get("title", "N/A"),
            year=movie_details.get("year", "N/A"),
            rating=movie_details.get("rating", "N/A"),
            genres=", ".join(
                movie_details.get("genres", [])
                if movie_details.get("genres")
                else []
            ),
            plot=movie_details.get("plot", "N/A"),
        )

    final_caption = session["caption"]

    if session.get("custom_languages"):
        final_caption += session["lang_format"].format(
            langs=", ".join(session["custom_languages"])
        )

    if session.get("custom_resolutions"):
        final_caption += session["res_format"].format(
            resolutions=", ".join(
                session["custom_resolutions"]
            )
        )

    if session.get("custom_otts"):
        final_caption += session["ott_format"].format(
            otts=", ".join(session["custom_otts"])
        )

    if session.get("watermark"):
        final_caption += (
            f"\n\n{session['watermark']}"
        )

    keyboard = build_keyboard(
        session,
        session_id
    )

    poster_to_use = (
        session.get("custom_poster")
        or (
            movie_details.get("backdrop_url")
            if session.get("use_landscape")
            else movie_details.get("poster_url")
        )
    )

    return (
        final_caption,
        keyboard,
        poster_to_use
    )


# ============================================================
# Preview
# ============================================================

async def update_post_preview(
    client: Client,
    session_id: int,
    chat_id: int,
    force_resend: bool = False
):

    session = post_sessions.get(session_id)

    if not session:
        return

    is_new = not session.get(
        "last_preview_message_id"
    )

    if is_new or force_resend:

        if not is_new:
            try:
                await client.delete_messages(
                    chat_id,
                    session["last_preview_message_id"]
                )
            except Exception:
                pass

        status_msg = await client.send_message(
            chat_id,
            "<i>Fetching details...</i>",
            reply_to_message_id=session[
                "original_message_id"
            ]
        )

        session["last_preview_message_id"] = status_msg.id

    final_caption, keyboard, poster_to_use = (
        await _build_final_post_content(
            session,
            session_id
        )
    )

    if not final_caption:
        return await client.edit_message_text(
            chat_id,
            session["last_preview_message_id"],
            "Could not find details for this movie."
        )

    try:

        if session["photo_mode"] and poster_to_use:

            if force_resend:

                await client.delete_messages(
                    chat_id,
                    session["last_preview_message_id"]
                )

                sent_message = await client.send_photo(
                    chat_id,
                    photo=poster_to_use,
                    caption=final_caption,
                    reply_markup=keyboard,
                    reply_to_message_id=session[
                        "original_message_id"
                    ]
                )

                session["last_preview_message_id"] = (
                    sent_message.id
                )

            else:

                await client.edit_message_caption(
                    chat_id,
                    session["last_preview_message_id"],
                    caption=final_caption,
                    reply_markup=keyboard
                )

        else:

            text_content = (
                f"<a href='{poster_to_use}'>&#8205;</a>"
                f"{final_caption}"
                if poster_to_use
                else final_caption
            )

            await client.edit_message_text(
                chat_id,
                session["last_preview_message_id"],
                text_content,
                reply_markup=keyboard,
                disable_web_page_preview=False
            )

    except MessageNotModified:
        pass

    except Exception as e:

        logger.error(
            f"Error updating preview: {e}",
            exc_info=True
        )


# ============================================================
# Main Keyboard
# ============================================================

def build_keyboard(
    session: dict,
    session_id: int
):

    rows = []

    # Custom buttons
    custom_buttons = render_custom_buttons(
        session.get("buttons", [])
    )

    if custom_buttons:
        rows.extend(custom_buttons)

    # --------------------------------------------------------
    # Main Controls
    # --------------------------------------------------------

    rows.extend([

        [
            make_button(
                "✏️ Buttons",
                callback_data=f"post:buttons_menu:{session_id}",
                style="PRIMARY"
            ),

            make_button(
                "✏️ Caption",
                callback_data=f"post:edit_caption:{session_id}",
                style="PRIMARY"
            ),
        ],

        [
            make_button(
                "🖼️ Poster",
                callback_data=f"post:set_poster:{session_id}",
                style="PRIMARY"
            ),

            make_button(
                "✨ Templates",
                callback_data=f"post:templates:{session_id}",
                style="PRIMARY"
            ),

            make_button(
                "💧 Watermark",
                callback_data=f"post:set_watermark:{session_id}",
                style="PRIMARY"
            ),
        ],

        [
            make_button(
                "🗣️ Languages",
                callback_data=f"post:languages:{session_id}",
                style="PRIMARY"
            ),

            make_button(
                "📺 Qualities",
                callback_data=f"post:resolutions:{session_id}",
                style="PRIMARY"
            ),

            make_button(
                "🌐 OTT",
                callback_data=f"post:otts:{session_id}",
                style="PRIMARY"
            ),
        ],

        [
            make_button(
                f"Mode: {'Photo' if session['photo_mode'] else 'Text'}",
                callback_data=f"post:toggle_preview:{session_id}",
                style="PRIMARY"
            ),

            make_button(
                f"Poster: {'Landscape' if session['use_landscape'] else 'Portrait'}",
                callback_data=f"post:toggle_poster:{session_id}",
                style="PRIMARY"
            ),
        ],

        [
            make_button(
                "🚀 Post",
                callback_data=f"post:finalize:{session_id}",
                style="SUCCESS"
            ),

            make_button(
                "❌ Cancel",
                callback_data=f"post:cancel:{session_id}",
                style="DANGER"
            ),
        ],
    ])

    return InlineKeyboardMarkup(rows)


# ============================================================
# Callback Handler
# ============================================================

@Client.on_callback_query(
    filters.regex(r"^post:"),
    group=-4
)
async def post_callbacks(
    client: Client,
    query: CallbackQuery
):

    data_parts = query.data.split(":")

    action = data_parts[1]
    session_id = int(data_parts[2])
    extra_data = data_parts[3:]

    if query.from_user.id != session_id:

        return await query.answer(
            "This is not for you!",
            show_alert=True
        )

    session = post_sessions.get(session_id)

    if not session:

        await query.answer(
            "Session expired or was cancelled.",
            show_alert=True
        )

        try:
            await query.message.delete()
        except Exception:
            pass

        return

    force_resend = False

    # --------------------------------------------------------
    # Back
    # --------------------------------------------------------

    if action == "back":

        await query.answer()

    # --------------------------------------------------------
    # Main Menus
    # --------------------------------------------------------

    elif action in [
        "languages",
        "resolutions",
        "templates",
        "buttons_menu",
        "remove_buttons_menu",
        "otts",
    ]:

        await query.answer()

        if action == "languages":

            await show_selection_menu(
                query,
                session_id,
                "languages"
            )

        elif action == "resolutions":

            await show_selection_menu(
                query,
                session_id,
                "resolutions"
            )

        elif action == "otts":

            await show_selection_menu(
                query,
                session_id,
                "otts"
            )

        elif action == "templates":

            await handle_templates_menu(
                query,
                session
            )

        elif action == "buttons_menu":

            await handle_buttons_menu(
                query,
                session_id
            )

        elif action == "remove_buttons_menu":

            await handle_remove_buttons_menu(
                query,
                session
            )

        return

    # --------------------------------------------------------
    # Selection
    # --------------------------------------------------------

    elif action in [
        "select_lang",
        "select_res",
        "select_ott"
    ]:

        await query.answer()

        item = extra_data[0]

        if action == "select_lang":

            if item not in session["custom_languages"]:
                session["custom_languages"].append(item)
            else:
                session["custom_languages"].remove(item)

            await show_selection_menu(
                query,
                session_id,
                "languages"
            )

        elif action == "select_res":

            if item not in session["custom_resolutions"]:
                session["custom_resolutions"].append(item)
            else:
                session["custom_resolutions"].remove(item)

            await show_selection_menu(
                query,
                session_id,
                "resolutions"
            )

        elif action == "select_ott":

            if item not in session["custom_otts"]:
                session["custom_otts"].append(item)
            else:
                session["custom_otts"].remove(item)

            await show_selection_menu(
                query,
                session_id,
                "otts"
            )

        return

    # --------------------------------------------------------
    # Other Actions
    # --------------------------------------------------------

    else:

        if action == "edit_buttons":

            await handle_edit_buttons(
                client,
                query,
                session
            )

        elif action == "add_button":

            await handle_add_button(
                client,
                query,
                session
            )

            return

        elif action == "add_get_files":

            await handle_add_get_files(
                session
            )

            await query.answer(
                "Get Files button added!"
            )

        elif action == "change_button_color":

            await handle_change_button_color_menu(
                query,
                session
            )

            return

        elif action == "select_color":

            await handle_select_color(
                query,
                session
            )

            return

        elif action == "select_change_color":

            await handle_select_change_color(
                query,
                session
            )

            return

        elif action == "edit_caption":

            await handle_edit_caption(
                client,
                query,
                session
            )

        elif action == "set_poster":

            force_resend = await handle_set_poster(
                client,
                query,
                session
            )

        elif action == "remove_button":

            await handle_remove_button(
                session,
                extra_data
            )

            await handle_remove_buttons_menu(
                query,
                session
            )

            return

        elif action == "select_template":

            await handle_select_template(
                session,
                extra_data[0]
            )

        elif action == "toggle_preview":

            force_resend = await handle_toggle_preview(
                query,
                session
            )

        elif action == "toggle_poster":

            force_resend = await handle_toggle_poster(
                session
            )

        elif action == "set_watermark":

            await handle_set_watermark(
                client,
                query,
                session
            )

        elif action == "format_lang":

            await handle_format_lang(
                client,
                query,
                session
            )

        elif action == "format_res":

            await handle_format_res(
                client,
                query,
                session
            )

        elif action == "format_ott":

            await handle_format_ott(
                client,
                query,
                session
            )

        elif action == "finalize":

            return await finalize_and_post(
                client,
                query,
                session_id
            )

        elif action == "cancel":

            return await handle_cancel(
                client,
                query,
                session_id
            )

    await update_post_preview(
        client,
        session_id,
        query.message.chat.id,
        force_resend
    )


# ============================================================
# Language / Resolution / OTT Menu
# ============================================================

async def show_selection_menu(
    query: CallbackQuery,
    session_id: int,
    menu_type: str
):

    session = post_sessions[session_id]

    if menu_type == "languages":

        items = LANGUAGES
        selected = session["custom_languages"]
        action_prefix = "select_lang"
        format_action = "format_lang"

    elif menu_type == "resolutions":

        items = RESOLUTIONS
        selected = session["custom_resolutions"]
        action_prefix = "select_res"
        format_action = "format_res"

    elif menu_type == "otts":

        items = OTT_PLATFORMS
        selected = session["custom_otts"]
        action_prefix = "select_ott"
        format_action = "format_ott"

    else:
        return

    buttons = []

    for item in items:

        if item in selected:

            button = make_button(
                f"✅ {item}",
                callback_data=(
                    f"post:{action_prefix}:"
                    f"{session_id}:{item}"
                ),
                style="SUCCESS"
            )

        else:

            button = make_button(
                item,
                callback_data=(
                    f"post:{action_prefix}:"
                    f"{session_id}:{item}"
                ),
                style="PRIMARY"
            )

        buttons.append(button)

    keyboard = [
        buttons[i:i + 3]
        for i in range(0, len(buttons), 3)
    ]

    keyboard.append([
        make_button(
            "⚙️ Change Format",
            callback_data=(
                f"post:{format_action}:{session_id}"
            ),
            style="PRIMARY"
        )
    ])

    keyboard.append([
        make_button(
            "✅ Done",
            callback_data=f"post:back:{session_id}",
            style="SUCCESS"
        )
    ])

    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(keyboard)
    )


# ============================================================
# User Input
# ============================================================

async def get_user_input(
    client,
    query,
    session,
    prompt_text
):

    ask_msg = await query.message.reply_text(
        prompt_text,
        reply_to_message_id=session.get(
            "original_message_id"
        )
    )

    try:

        response = await client.listen(
            chat_id=query.message.chat.id,
            user_id=query.from_user.id,
            timeout=300
        )

        try:
            await ask_msg.delete()
        except Exception:
            pass

        if response:

            try:
                await response.delete()
            except Exception:
                pass

            return response

    except asyncio.TimeoutError:

        await ask_msg.edit(
            "Timeout (5 minutes). The operation was cancelled."
        )

        await asyncio.sleep(5)

        try:
            await ask_msg.delete()
        except Exception:
            pass

    return None


# ============================================================
# Buttons Main Menu
# ============================================================

async def handle_buttons_menu(
    query,
    session_id
):

    buttons = [

        [
            make_button(
                "➕ Add Button",
                callback_data=(
                    f"post:add_button:{session_id}"
                ),
                style="SUCCESS"
            ),

            make_button(
                "✏️ Add/Edit Layout",
                callback_data=(
                    f"post:edit_buttons:{session_id}"
                ),
                style="PRIMARY"
            ),
        ],

        [
            make_button(
                "🎨 Change Button Color",
                callback_data=(
                    f"post:change_button_color:{session_id}"
                ),
                style="PRIMARY"
            ),
        ],

        [
            make_button(
                "📥 Add Get Files",
                callback_data=(
                    f"post:add_get_files:{session_id}"
                ),
                style="SUCCESS"
            ),
        ],

        [
            make_button(
                "🗑️ Remove Button",
                callback_data=(
                    f"post:remove_buttons_menu:{session_id}"
                ),
                style="DANGER"
            ),
        ],

        [
            make_button(
                "⬅️ Back",
                callback_data=f"post:back:{session_id}",
                style="PRIMARY"
            )
        ],
    ]

    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(buttons)
    )


# ============================================================
# Add New Button
# ============================================================

async def handle_add_button(
    client,
    query,
    session
):

    response = await get_user_input(
        client,
        query,
        session,
        (
            "Send the <b>button text</b>.\n\n"
            "Example:\n"
            "<code>🎬 1080p</code>"
        )
    )

    if not response or not response.text:
        return

    button_text = response.text.strip()

    if len(button_text) > 64:

        await query.message.reply_text(
            "Button text is too long. Please use 64 characters or less."
        )

        return

    response = await get_user_input(
        client,
        query,
        session,
        (
            "Now send the <b>button URL</b>.\n\n"
            "Example:\n"
            "<code>https://example.com</code>"
        )
    )

    if not response or not response.text:
        return

    button_url = response.text.strip()

    if not (
        button_url.startswith("http://")
        or button_url.startswith("https://")
        or button_url.startswith("tg://")
    ):

        await query.message.reply_text(
            "Invalid URL.\n\n"
            "Please use a valid http://, https:// or tg:// URL."
        )

        return

    # Temporary button data
    session["_pending_button"] = {
        "text": button_text,
        "url": button_url,
    }

    # Color selection
    keyboard = InlineKeyboardMarkup([

        [
            make_button(
                "🔵 Primary",
                callback_data=(
                    f"post:select_color:"
                    f"{query.from_user.id}:PRIMARY"
                ),
                style="PRIMARY"
            )
        ],

        [
            make_button(
                "🟢 Success",
                callback_data=(
                    f"post:select_color:"
                    f"{query.from_user.id}:SUCCESS"
                ),
                style="SUCCESS"
            )
        ],

        [
            make_button(
                "🔴 Danger",
                callback_data=(
                    f"post:select_color:"
                    f"{query.from_user.id}:DANGER"
                ),
                style="DANGER"
            )
        ],

        [
            make_button(
                "❌ Cancel",
                callback_data=f"post:back:{query.from_user.id}",
                style="DANGER"
            )
        ],

    ])

    await query.message.reply_text(
        (
            "<b>🎨 Choose Button Color</b>\n\n"
            f"<b>Text:</b> <code>{button_text}</code>\n"
            f"<b>URL:</b> <code>{button_url}</code>\n\n"
            "Select the color for this button:"
        ),
        reply_markup=keyboard
    )


# ============================================================
# Save New Button Color
# ============================================================

async def handle_select_color(
    query,
    session
):

    style = query.data.split(":")[3]

    pending = session.get("_pending_button")

    if not pending:

        return await query.answer(
            "No pending button found.",
            show_alert=True
        )

    pending["style"] = style

    # Default row: each new button gets its own row.
    session["buttons"].append([
        pending.copy()
    ])

    session.pop("_pending_button", None)

    await query.answer(
        f"Button added with {button_style_name(style)}."
    )

    await query.message.delete()

    await update_post_preview(
        query._client,
        query.from_user.id,
        query.message.chat.id,
        force_resend=False
    )


# ============================================================
# Change Existing Button Color Menu
# ============================================================

async def handle_change_button_color_menu(
    query,
    session
):

    buttons = []

    for row_i, row in enumerate(
        session.get("buttons", [])
    ):

        for col_i, button in enumerate(row):

            if isinstance(button, dict):

                text = button.get(
                    "text",
                    "Button"
                )

                style = button.get(
                    "style",
                    "PRIMARY"
                )

            else:

                text = button.text
                style = "PRIMARY"

            buttons.append([
                make_button(
                    (
                        f"🎨 {text}\n"
                        f"({button_style_name(style)})"
                    ),
                    callback_data=(
                        f"post:select_change_color:"
                        f"{query.from_user.id}:"
                        f"{row_i}:{col_i}"
                    ),
                    style=style
                )
            ])

    if not buttons:

        buttons.append([
            make_button(
                "No buttons available",
                callback_data=(
                    f"post:back:{query.from_user.id}"
                ),
                style="PRIMARY"
            )
        ])

    buttons.append([
        make_button(
            "⬅️ Back",
            callback_data=(
                f"post:buttons_menu:{query.from_user.id}"
            ),
            style="PRIMARY"
        )
    ])

    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(buttons)
    )


# ============================================================
# Select New Color For Existing Button
# ============================================================

async def handle_select_change_color(
    query,
    session
):

    parts = query.data.split(":")

    try:

        row_i = int(parts[3])
        col_i = int(parts[4])

        button = session["buttons"][
            row_i
        ][col_i]

    except (
        IndexError,
        ValueError,
        KeyError,
        TypeError
    ):

        return await query.answer(
            "Button no longer exists.",
            show_alert=True
        )

    if isinstance(button, dict):

        button_text = button.get(
            "text",
            "Button"
        )

    else:

        button_text = button.text

        # Convert old-style object to dict
        button_url = getattr(
            button,
            "url",
            None
        )

        button = {
            "text": button_text,
            "url": button_url,
            "style": "PRIMARY",
        }

        session["buttons"][
            row_i
        ][col_i] = button

    color_keyboard = InlineKeyboardMarkup([

        [
            make_button(
                "🔵 Primary",
                callback_data=(
                    f"post:set_existing_color:"
                    f"{query.from_user.id}:"
                    f"{row_i}:{col_i}:PRIMARY"
                ),
                style="PRIMARY"
            )
        ],

        [
            make_button(
                "🟢 Success",
                callback_data=(
                    f"post:set_existing_color:"
                    f"{query.from_user.id}:"
                    f"{row_i}:{col_i}:SUCCESS"
                ),
                style="SUCCESS"
            )
        ],

        [
            make_button(
                "🔴 Danger",
                callback_data=(
                    f"post:set_existing_color:"
                    f"{query.from_user.id}:"
                    f"{row_i}:{col_i}:DANGER"
                ),
                style="DANGER"
            )
        ],

        [
            make_button(
                "⬅️ Back",
                callback_data=(
                    f"post:change_button_color:"
                    f"{query.from_user.id}"
                ),
                style="PRIMARY"
            )
        ],

    ])

    await query.edit_message_reply_markup(
        color_keyboard
    )


# ============================================================
# Existing Button Color Setter
# ============================================================

async def set_existing_button_color(
    query,
    session
):

    parts = query.data.split(":")

    try:

        row_i = int(parts[3])
        col_i = int(parts[4])
        style = parts[5]

        button = session["buttons"][
            row_i
        ][col_i]

    except (
        IndexError,
        ValueError,
        KeyError,
        TypeError
    ):

        return await query.answer(
            "Button no longer exists.",
            show_alert=True
        )

    if isinstance(button, dict):

        button["style"] = style

    else:

        old_text = button.text
        old_url = getattr(
            button,
            "url",
            None
        )

        session["buttons"][
            row_i
        ][col_i] = {
            "text": old_text,
            "url": old_url,
            "style": style,
        }

    await query.answer(
        f"Color changed to {button_style_name(style)}."
    )

    await update_post_preview(
        query._client,
        query.from_user.id,
        query.message.chat.id,
        False
    )


# ============================================================
# Add / Edit Bulk Layout
# ============================================================

async def handle_edit_buttons(
    client,
    query,
    session
):

    response = await get_user_input(
        client,
        query,
        session,
        (
            "<b>Send the button layout.</b>\n\n"
            "<code>Button 1 - URL1 | Button 2 - URL2</code>\n"
            "<i>Same row</i>\n\n"
            "<code>Button 3 - URL3</code>\n"
            "<i>New row</i>\n\n"
            "All new buttons will start as "
            "<b>Primary</b>.\n"
            "You can change their colors afterward "
            "from 🎨 Change Button Color."
        )
    )

    if response and response.text:

        new_layout = []

        for row_str in response.text.strip().split("\n"):

            row_btns = []

            for btn_str in row_str.split("|"):

                if " - " not in btn_str:
                    continue

                text, url = btn_str.split(
                    " - ",
                    1
                )

                text = text.strip()
                url = url.strip()

                if not text or not url:
                    continue

                row_btns.append({
                    "text": text,
                    "url": url,
                    "style": "PRIMARY",
                })

            if row_btns:
                new_layout.append(row_btns)

        session["buttons"] = new_layout


# ============================================================
# Add Get Files
# ============================================================

async def handle_add_get_files(
    session
):

    movie_details = session["movie_details"]

    if not movie_details:
        return

    title = movie_details.get(
        "title",
        "movie"
    )

    year = movie_details.get(
        "year",
        ""
    )

    movie_year = (
        f"{title} {year}"
        .strip()
        .replace(" ", "-")
    )

    movie_year = re.sub(
        r"[ *:\.]",
        "-",
        movie_year
    )

    url = (
        f"https://telegram.me/{temp.U_NAME}"
        f"?start=getfile-{movie_year}"
    )

    session["buttons"].append([
        {
            "text": "📥 Get Files 📥",
            "url": url,
            "style": "SUCCESS",
        }
    ])


# ============================================================
# Caption
# ============================================================

async def handle_edit_caption(
    client,
    query,
    session
):

    response = await get_user_input(
        client,
        query,
        session,
        "Send the new caption text."
    )

    if response and response.text:
        session["caption"] = response.text


# ============================================================
# Poster
# ============================================================

async def handle_set_poster(
    client,
    query,
    session
):

    response = await get_user_input(
        client,
        query,
        session,
        (
            "Send a photo or an image URL.\n\n"
            "Send `/reset` to use the default poster."
        )
    )

    if response:

        if response.photo:

            session["custom_poster"] = (
                response.photo.file_id
            )

            if not session["photo_mode"]:

                session["photo_mode"] = True

                await query.answer(
                    "Switched to Photo mode.",
                    show_alert=True
                )

        elif (
            response.text
            and response.text.startswith("http")
        ):

            session["custom_poster"] = (
                response.text
            )

        elif (
            response.text
            and response.text == "/reset"
        ):

            session["custom_poster"] = None

    return True


# ============================================================
# Watermark
# ============================================================

async def handle_set_watermark(
    client,
    query,
    session
):

    prompt_text = (
        "Send the watermark text.\n\n"
        "• `/reset` — Remove watermark\n"
        "• `/default` — Use ProviderBotz watermark"
    )

    response = await get_user_input(
        client,
        query,
        session,
        prompt_text
    )

    if response and response.text:

        if response.text == "/reset":

            session["watermark"] = ""

        elif response.text == "/default":

            session["watermark"] = (
                DEFAULT_WATERMARK
            )

        else:

            session["watermark"] = (
                response.text
            )


# ============================================================
# Formats
# ============================================================

async def handle_format_lang(
    client,
    query,
    session
):

    response = await get_user_input(
        client,
        query,
        session,
        (
            "Send the format for languages.\n"
            "Use `{langs}` as placeholder.\n\n"
            "Send `/reset` for default.\n\n"
            f"Current:\n{session['lang_format']}"
        )
    )

    if response and response.text:

        session["lang_format"] = (
            LANGUAGES_FORMAT
            if response.text == "/reset"
            else response.text
        )


async def handle_format_res(
    client,
    query,
    session
):

    response = await get_user_input(
        client,
        query,
        session,
        (
            "Send the format for qualities.\n"
            "Use `{resolutions}` as placeholder.\n\n"
            "Send `/reset` for default.\n\n"
            f"Current:\n{session['res_format']}"
        )
    )

    if response and response.text:

        session["res_format"] = (
            RESOLUTIONS_FORMAT
            if response.text == "/reset"
            else response.text
        )


async def handle_format_ott(
    client,
    query,
    session
):

    response = await get_user_input(
        client,
        query,
        session,
        (
            "Send the format for OTT.\n"
            "Use `{otts}` as placeholder.\n\n"
            "Send `/reset` for default.\n\n"
            f"Current:\n{session['ott_format']}"
        )
    )

    if response and response.text:

        session["ott_format"] = (
            OTT_FORMAT
            if response.text == "/reset"
            else response.text
        )


# ============================================================
# Templates
# ============================================================

async def handle_templates_menu(
    query,
    session
):

    buttons = []

    for name in TEMPLATES:

        text = (
            f"✅ {name}"
            if session.get("active_template") == name
            else name
        )

        style = (
            "SUCCESS"
            if session.get("active_template") == name
            else "PRIMARY"
        )

        buttons.append([
            make_button(
                text,
                callback_data=(
                    f"post:select_template:"
                    f"{query.from_user.id}:{name}"
                ),
                style=style
            )
        ])

    buttons.append([
        make_button(
            "⬅️ Back",
            callback_data=(
                f"post:back:{query.from_user.id}"
            ),
            style="PRIMARY"
        )
    ])

    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(buttons)
    )


async def handle_select_template(
    session,
    template_name
):

    if template_name not in TEMPLATES:
        return

    session["active_template"] = (
        template_name
    )

    session["caption"] = None


# ============================================================
# Remove Buttons
# ============================================================

async def handle_remove_buttons_menu(
    query,
    session
):

    buttons = []

    for row_i, row in enumerate(
        session.get("buttons", [])
    ):

        for col_i, button in enumerate(row):

            if isinstance(button, dict):

                text = button.get(
                    "text",
                    "Button"
                )

                style = button.get(
                    "style",
                    "PRIMARY"
                )

            else:

                text = button.text
                style = "PRIMARY"

            buttons.append([
                make_button(
                    f"❌ {text}",
                    callback_data=(
                        f"post:remove_button:"
                        f"{query.from_user.id}:"
                        f"{row_i}:{col_i}"
                    ),
                    style="DANGER"
                )
            ])

    if not buttons:

        buttons.append([
            make_button(
                "No buttons to remove",
                callback_data=(
                    f"post:back:{query.from_user.id}"
                ),
                style="PRIMARY"
            )
        ])

    buttons.append([
        make_button(
            "⬅️ Back",
            callback_data=(
                f"post:buttons_menu:"
                f"{query.from_user.id}"
            ),
            style="PRIMARY"
        )
    ])

    await query.edit_message_reply_markup(
        InlineKeyboardMarkup(buttons)
    )


async def handle_remove_button(
    session,
    extra_data
):

    try:

        row_i = int(extra_data[0])
        col_i = int(extra_data[1])

        session["buttons"][
            row_i
        ].pop(col_i)

        if not session["buttons"][row_i]:
            session["buttons"].pop(row_i)

    except (
        IndexError,
        ValueError
    ):

        logger.warning(
            "Tried to remove a button that does not exist."
        )


# ============================================================
# Preview Toggle
# ============================================================

async def handle_toggle_preview(
    query,
    session
):

    if (
        session.get("custom_poster")
        and not session["custom_poster"].startswith("http")
    ):

        await query.answer(
            "Cannot switch to Text mode with an uploaded photo.",
            show_alert=True
        )

        return False

    session["photo_mode"] = (
        not session["photo_mode"]
    )

    return True


async def handle_toggle_poster(
    session
):

    session["use_landscape"] = (
        not session["use_landscape"]
    )

    return True


# ============================================================
# Cancel
# ============================================================

async def handle_cancel(
    client,
    query,
    session_id,
    _=None
):

    session = post_sessions.pop(
        session_id,
        None
    )

    if session:

        if session.get(
            "last_preview_message_id"
        ):

            try:
                await client.delete_messages(
                    query.message.chat.id,
                    session[
                        "last_preview_message_id"
                    ]
                )
            except Exception:
                pass

    await query.message.reply_to_message.reply_text(
        "Post creation cancelled."
    )


# ============================================================
# Finalize / Post
# ============================================================

async def finalize_and_post(
    client,
    query,
    session_id,
    _=None
):

    session = post_sessions.pop(
        session_id,
        None
    )

    if not session:

        logger.warning(
            f"Finalize called for expired session: "
            f"{session_id}"
        )

        return

    try:

        await client.delete_messages(
            query.message.chat.id,
            session[
                "last_preview_message_id"
            ]
        )

    except Exception:
        pass

    status_msg = await (
        query.message.reply_to_message.reply_text(
            "<i>Finalizing and posting...</i>"
        )
    )

    final_caption, _, poster_to_use = (
        await _build_final_post_content(
            session,
            session_id
        )
    )

    # --------------------------------------------------------
    # IMPORTANT:
    # Use custom button renderer so selected colors
    # remain in the final channel post.
    # --------------------------------------------------------

    final_keyboard_buttons = (
        render_custom_buttons(
            session.get("buttons", [])
        )
    )

    final_keyboard = (
        InlineKeyboardMarkup(
            final_keyboard_buttons
        )
        if final_keyboard_buttons
        else None
    )

    if not final_caption:

        return await status_msg.edit(
            "Could not fetch movie details to post. Aborting."
        )

    mode = (
        "Photo"
        if session["photo_mode"]
        and poster_to_use
        else "Text"
    )

    logger.info(
        f"Finalizing post for "
        f"'{session['movie_name']}'. Mode: {mode}"
    )

    logger.info(
        f"Poster to use: {poster_to_use}"
    )

    logger.info(
        f"Final Caption Length: "
        f"{len(final_caption)} characters."
    )

    try:

        if mode == "Photo":

            await client.send_photo(
                chat_id=MOVIE_UPDATE_CHANNEL,
                photo=poster_to_use,
                caption=final_caption,
                reply_markup=final_keyboard
            )

        else:

            text_content = (
                f"<a href='{poster_to_use}'>&#8205;</a>"
                f"{final_caption}"
                if poster_to_use
                else final_caption
            )

            await client.send_message(
                chat_id=MOVIE_UPDATE_CHANNEL,
                text=text_content,
                reply_markup=final_keyboard,
                disable_web_page_preview=False,
                invert_media=ABOVE_PREVIEW
            )

        await status_msg.edit(
            "✅ Post has been sent to the update channel."
        )

        logger.info(
            f"Successfully posted "
            f"'{session['movie_name']}'"
        )

    except MessageTooLong:

        error_text = (
            "<b>Post Failed</b>\n\n"
            "The final caption is too long for "
            "a Telegram message. Please shorten "
            "the plot or other text and try again."
        )

        await status_msg.edit(
            error_text
        )

        logger.error(
            "MessageTooLong error.",
            exc_info=True
        )

    except Exception as e:

        error_text = (
            "Failed to post to update channel.\n"
            f"<b>Error:</b> <code>{e}</code>"
        )

        await status_msg.edit(
            error_text
        )

        logger.error(
            "Unexpected posting error.",
            exc_info=True
        )


# ============================================================
# Extra Callback Handler
# ============================================================

@Client.on_callback_query(
    filters.regex(r"^post:set_existing_color:"),
    group=-3
)
async def existing_color_callback(
    client,
    query
):

    data = query.data.split(":")

    session_id = int(data[2])

    if query.from_user.id != session_id:

        return await query.answer(
            "This is not for you!",
            show_alert=True
        )

    session = post_sessions.get(
        session_id
    )

    if not session:

        return await query.answer(
            "Session expired.",
            show_alert=True
        )

    await set_existing_button_color(
        query,
        session
    )


# ============================================================
# No-op callback
# ============================================================

@Client.on_callback_query(
    filters.regex(r"^noop$"),
    group=-3
)
async def noop_callback(
    client,
    query
):

    await query.answer()
