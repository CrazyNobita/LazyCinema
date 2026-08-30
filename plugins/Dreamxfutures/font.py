import logging
import secrets
from html import escape

from plugins.Dreamxfutures.fotnt_string import Fonts
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ParseMode

try:
    from kurigram.enums import ButtonStyle
except ImportError:
    # If your Kurigram version exposes ButtonStyle differently,
    # change only this import.
    from pyrogram.enums import ButtonStyle


logger = logging.getLogger(__name__)

# ============================================================
# TEMPORARY COPY CACHE
# ============================================================

COPY_CACHE = {}


# ============================================================
# FONT MAP
# ============================================================

STYLE_MAP = {
    "typewriter": Fonts.typewriter,
    "outline": Fonts.outline,
    "serif": Fonts.serief,
    "bold_cool": Fonts.bold_cool,
    "cool": Fonts.cool,
    "small_cap": Fonts.smallcap,
    "script": Fonts.script,
    "script_bolt": Fonts.bold_script,
    "tiny": Fonts.tiny,
    "comic": Fonts.comic,
    "sans": Fonts.san,
    "slant_sans": Fonts.slant_san,
    "slant": Fonts.slant,
    "sim": Fonts.sim,
    "circles": Fonts.circles,
    "circle_dark": Fonts.dark_circle,
    "gothic": Fonts.gothic,
    "gothic_bolt": Fonts.bold_gothic,
    "cloud": Fonts.cloud,
    "happy": Fonts.happy,
    "sad": Fonts.sad,
    "special": Fonts.special,
    "squares": Fonts.square,
    "squares_bold": Fonts.dark_square,
    "andalucia": Fonts.andalucia,
    "manga": Fonts.manga,
    "stinky": Fonts.stinky,
    "bubbles": Fonts.bubbles,
    "underline": Fonts.underline,
    "ladybug": Fonts.ladybug,
    "rays": Fonts.rays,
    "birds": Fonts.birds,
    "slash": Fonts.slash,
    "stop": Fonts.stop,
    "skyline": Fonts.skyline,
    "arrows": Fonts.arrows,
    "qvnes": Fonts.rvnes,
    "strike": Fonts.strike,
    "frozen": Fonts.frozen,
}


# ============================================================
# STYLE DISPLAY NAMES
# ============================================================

STYLE_NAMES = {
    "typewriter": "𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛",
    "outline": "𝕆𝕦𝕥𝕝𝕚𝕟𝕖",
    "serif": "𝐒𝐞𝐫𝐢𝐟",
    "bold_cool": "𝑺𝒆𝒓𝒊𝒇",
    "cool": "𝑆𝑒𝑟𝑖𝑓",
    "small_cap": "Sᴍᴀʟʟ Cᴀᴘs",
    "script": "𝓈𝒸𝓇𝒾𝓅𝓉",
    "script_bolt": "𝓼𝓬𝓻𝓲𝓹𝓽",
    "tiny": "ᵗⁱⁿʸ",
    "comic": "ᑕOᗰIᑕ",
    "sans": "𝗦𝗮𝗻𝘀",
    "slant_sans": "𝙎𝙖𝙣𝙨",
    "slant": "𝘚𝘢𝘯𝘴",
    "sim": "𝖲𝖺𝗇𝗌",
    "circles": "Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎",
    "circle_dark": "🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎",
    "gothic": "𝔊𝔬𝔱𝔥𝔦𝔠",
    "gothic_bolt": "𝕲𝖔𝖙𝖍𝖎𝖈",
    "cloud": "C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡",
    "happy": "H̆̈ă̈p̆̈p̆̈y̆̈",
    "sad": "S̑̈ȃ̈d̑̈",
    "special": "🇸 🇵 🇪 🇨 🇮 🇦 🇱 ",
    "squares": "🅂🅀🅄🄰🅁🄴🅂",
    "squares_bold": "🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎",
    "andalucia": "ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ",
    "manga": "爪卂几ᘜ卂",
    "stinky": "S̾t̾i̾n̾k̾y̾",
    "bubbles": "B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ",
    "underline": "U͟n͟d͟e͟r͟l͟i͟n͟e͟",
    "ladybug": "꒒ꍏꀷꌩꌃꀎꁅ",
    "rays": "R҉a҉y҉s҉",
    "birds": "B҈i҈r҈d҈s҈",
    "slash": "S̸l̸a̸s̸h̸",
    "stop": "s⃠t⃠o⃠p⃠",
    "skyline": "S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆",
    "arrows": "A͎r͎r͎o͎w͎s͎",
    "qvnes": "ዪሀክቿነ",
    "strike": "S̶t̶r̶i̶k̶e̶",
    "frozen": "F༙r༙o༙z༙e༙",
}


# ============================================================
# HELPERS
# ============================================================

def get_text_from_message(message):
    """Extract text from /font command."""

    if not message:
        return ""

    text = message.text or message.caption or ""

    if not text:
        return ""

    parts = text.split(maxsplit=1)

    if parts and parts[0].lower().split("@")[0] in {
        "/font",
        "/fonts",
        "/style",
    }:
        return parts[1] if len(parts) > 1 else ""

    return text


def create_button(text, callback_data, style):
    """Create a Kurigram styled button."""

    try:
        return InlineKeyboardButton(
            text,
            callback_data=callback_data,
            style=style,
        )
    except TypeError:
        # Fallback if the installed library does not support style.
        return InlineKeyboardButton(
            text,
            callback_data=callback_data,
        )


# ============================================================
# PAGE 1 BUTTONS
# ============================================================

def page_one_buttons():

    return [
        [
            create_button(
                "✨ 𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛",
                "style+typewriter",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "🌀 𝕆𝕦𝕥𝕝𝕚𝕟𝕖",
                "style+outline",
                ButtonStyle.INFO,
            ),
            create_button(
                "📝 𝐒𝐞𝐫𝐢𝐟",
                "style+serif",
                ButtonStyle.PRIMARY,
            ),
        ],
        [
            create_button(
                "🌸 𝑺𝒆𝒓𝒊𝒇",
                "style+bold_cool",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "🌊 𝑆𝑒𝑟𝑖𝑓",
                "style+cool",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "📐 Sᴍᴀʟʟ Cᴀᴘs",
                "style+small_cap",
                ButtonStyle.INFO,
            ),
        ],
        [
            create_button(
                "✍️ 𝓈𝒸𝓇𝒾𝓅𝓉",
                "style+script",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "🔥 𝓼𝓬𝓻𝓲𝓹𝓽",
                "style+script_bolt",
                ButtonStyle.DANGER,
            ),
            create_button(
                "🔹 ᵗⁱⁿʸ",
                "style+tiny",
                ButtonStyle.INFO,
            ),
        ],
        [
            create_button(
                "🎭 ᑕOᗰIᑕ",
                "style+comic",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "💎 𝗦𝗮𝗻𝘀",
                "style+sans",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "⚡ 𝙎𝙖𝙣𝙨",
                "style+slant_sans",
                ButtonStyle.SUCCESS,
            ),
        ],
        [
            create_button(
                "🌙 𝘚𝘢𝘯𝘴",
                "style+slant",
                ButtonStyle.INFO,
            ),
            create_button(
                "⭐ 𝖲𝖺𝗇𝗌",
                "style+sim",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "⭕ Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎",
                "style+circles",
                ButtonStyle.SUCCESS,
            ),
        ],
        [
            create_button(
                "🅾️ 🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎",
                "style+circle_dark",
                ButtonStyle.INFO,
            ),
            create_button(
                "🖤 𝔊𝔬𝔱𝔥𝔦𝔠",
                "style+gothic",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "💠 𝕲𝖔𝖙𝖍𝖎𝖈",
                "style+gothic_bolt",
                ButtonStyle.SUCCESS,
            ),
        ],
        [
            create_button(
                "☁️ C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡",
                "style+cloud",
                ButtonStyle.INFO,
            ),
            create_button(
                "😊 H̆̈ă̈p̆̈p̆̈y̆̈",
                "style+happy",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "😢 S̑̈ȃ̈d̑̈",
                "style+sad",
                ButtonStyle.DANGER,
            ),
        ],
        [
            create_button(
                "➡️ Next Page",
                "nxt",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "❌ Close",
                "close_font",
                ButtonStyle.DANGER,
            ),
        ],
    ]


# ============================================================
# PAGE 2 BUTTONS
# ============================================================

def page_two_buttons():

    return [
        [
            create_button(
                "🌟 🇸 🇵 🇪 🇨 🇮 🇦 🇱 ",
                "style+special",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "🔲 🅂🅀🅄🄰🅁🄴🅂",
                "style+squares",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "🔳 🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎",
                "style+squares_bold",
                ButtonStyle.INFO,
            ),
        ],
        [
            create_button(
                "🌺 ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ",
                "style+andalucia",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "🍜 爪卂几ᘜ卂",
                "style+manga",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "💩 S̾t̾i̾n̾k̾y̾",
                "style+stinky",
                ButtonStyle.DANGER,
            ),
        ],
        [
            create_button(
                "🫧 B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ",
                "style+bubbles",
                ButtonStyle.INFO,
            ),
            create_button(
                "📏 U͟n͟d͟e͟r͟l͟i͟n͟e͟",
                "style+underline",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "🐞 ꒒ꍏꀷꌩꌃꀎꁅ",
                "style+ladybug",
                ButtonStyle.SUCCESS,
            ),
        ],
        [
            create_button(
                "☀️ R҉a҉y҉s҉",
                "style+rays",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "🐦 B҈i҈r҈d҈s҈",
                "style+birds",
                ButtonStyle.INFO,
            ),
            create_button(
                "⚔️ S̸l̸a̸s̸h̸",
                "style+slash",
                ButtonStyle.DANGER,
            ),
        ],
        [
            create_button(
                "🚫 s⃠t⃠o⃠p⃠",
                "style+stop",
                ButtonStyle.DANGER,
            ),
            create_button(
                "🌃 S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆",
                "style+skyline",
                ButtonStyle.INFO,
            ),
            create_button(
                "🏹 A͎r͎r͎o͎w͎s͎",
                "style+arrows",
                ButtonStyle.PRIMARY,
            ),
        ],
        [
            create_button(
                "🔮 ዪሀክቿነ",
                "style+qvnes",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "✂️ S̶t̶r̶i̶k̶e̶",
                "style+strike",
                ButtonStyle.DANGER,
            ),
            create_button(
                "❄️ F༙r༙o༙z༙e༙n༙",
                "style+frozen",
                ButtonStyle.INFO,
            ),
        ],
        [
            create_button(
                "⬅️ Back",
                "back_font",
                ButtonStyle.PRIMARY,
            ),
            create_button(
                "❌ Close",
                "close_font",
                ButtonStyle.DANGER,
            ),
        ],
    ]


# ============================================================
# MAIN FONT COMMAND
# ============================================================

@Client.on_message(
    filters.private & filters.command(["font", "fonts", "style"])
)
async def style_buttons(client, message):

    text = get_text_from_message(message)

    if not text:
        await message.reply_text(
            "🎨 <b>Premium Font Generator</b>\n\n"
            "📌 <b>Usage:</b>\n"
            "<code>/font Your Text</code>\n\n"
            "📝 <b>Example:</b>\n"
            "<code>/font Hello World</code>\n\n"
            "✨ Select a style to transform your text!",
            reply_markup=InlineKeyboardMarkup(page_one_buttons()),
            parse_mode=ParseMode.HTML,
        )
        return

    user = (
        message.from_user.mention
        if message.from_user
        else "User"
    )

    await message.reply_text(
        "🎨 <b>Premium Font Generator</b>\n\n"
        f"👤 <b>User:</b> {user}\n"
        f"📝 <b>Text:</b> <code>{escape(text[:200])}</code>\n\n"
        "<i>Select a font style below to transform your text!</i>\n\n"
        "🎨 <b>Button Guide:</b>\n"
        "🔵 Primary • 🟢 Success • 🔴 Danger • 🔷 Info",
        reply_markup=InlineKeyboardMarkup(page_one_buttons()),
        reply_to_message_id=message.id,
        parse_mode=ParseMode.HTML,
    )


# ============================================================
# NEXT PAGE
# ============================================================

@Client.on_callback_query(filters.regex(r"^nxt$"))
async def next_page(client, query: CallbackQuery):

    await query.answer()

    try:
        await query.message.edit_reply_markup(
            InlineKeyboardMarkup(page_two_buttons())
        )
    except Exception as e:
        logger.error("Next page error: %s", e)


# ============================================================
# BACK TO PAGE 1
# ============================================================

@Client.on_callback_query(filters.regex(r"^back_font$"))
async def back_to_menu(client, query: CallbackQuery):

    await query.answer()

    text = query.message.text or ""

    original_text = "text"

    marker = "🔤 <b>Original:</b> <code>"

    if marker in text:
        try:
            original_text = text.split(marker, 1)[1].split(
                "</code>",
                1
            )[0]
        except Exception:
            pass

    try:
        await query.message.edit_text(
            "🎨 <b>Premium Font Generator</b>\n\n"
            f"📝 <b>Current Text:</b> "
            f"<code>{escape(original_text[:100])}</code>\n\n"
            "<i>Select a font style to transform your text!</i>\n\n"
            "🎨 <b>Button Guide:</b>\n"
            "🔵 Primary • 🟢 Success • 🔴 Danger • 🔷 Info",
            reply_markup=InlineKeyboardMarkup(page_one_buttons()),
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        logger.error("Back menu error: %s", e)


# ============================================================
# APPLY FONT STYLE
# ============================================================

@Client.on_callback_query(filters.regex(r"^style\+"))
async def apply_style(client, query: CallbackQuery):

    try:
        await query.answer()
    except Exception:
        pass

    try:
        _, style_name = query.data.split("+", 1)
    except ValueError:
        await query.answer(
            "❌ Invalid style!",
            show_alert=True,
        )
        return

    font_function = STYLE_MAP.get(style_name)

    if not font_function:
        await query.answer(
            "❌ Style not found!",
            show_alert=True,
        )
        return

    # --------------------------------------------------------
    # GET ORIGINAL TEXT
    # --------------------------------------------------------

    original_text = ""

    message = query.message

    if message.reply_to_message:
        original_text = get_text_from_message(
            message.reply_to_message
        )

    if not original_text:
        message_text = message.text or ""

        marker = "📝 <b>Text:</b> <code>"

        if marker in message_text:
            try:
                original_text = message_text.split(
                    marker,
                    1
                )[1].split(
                    "</code>",
                    1
                )[0]
            except Exception:
                pass

    if not original_text:
        await query.answer(
            "❌ No text found!",
            show_alert=True,
        )
        return

    # --------------------------------------------------------
    # APPLY FONT
    # --------------------------------------------------------

    try:
        new_text = font_function(original_text)
    except Exception as e:
        logger.exception(
            "Font conversion error: %s",
            e,
        )

        await query.answer(
            "❌ Error applying font!",
            show_alert=True,
        )
        return

    if not new_text:
        await query.answer(
            "❌ Font returned empty text!",
            show_alert=True,
        )
        return

    # --------------------------------------------------------
    # COPY CACHE
    # --------------------------------------------------------

    copy_id = secrets.token_hex(8)

    COPY_CACHE[copy_id] = new_text

    # Prevent unlimited memory growth.
    if len(COPY_CACHE) > 1000:
        oldest_key = next(iter(COPY_CACHE))
        COPY_CACHE.pop(oldest_key, None)

    # --------------------------------------------------------
    # RESULT BUTTONS
    # --------------------------------------------------------

    buttons = [
        [
            create_button(
                "📋 Copy Text",
                f"copy_{copy_id}",
                ButtonStyle.SUCCESS,
            ),
            create_button(
                "🔄 Back to Menu",
                "back_font",
                ButtonStyle.PRIMARY,
            ),
        ],
        [
            create_button(
                "❌ Close",
                "close_font",
                ButtonStyle.DANGER,
            ),
        ],
    ]

    # --------------------------------------------------------
    # RESULT MESSAGE
    # --------------------------------------------------------

    style_display = STYLE_NAMES.get(
        style_name,
        style_name.upper(),
    )

    try:
        await message.edit_text(
            "🎨 <b>Font Style Applied</b>\n\n"
            f"📝 <b>Style:</b> "
            f"<code>{escape(style_display)}</code>\n"
            f"🔤 <b>Original:</b> "
            f"<code>{escape(original_text[:100])}</code>\n\n"
            "✨ <b>Result:</b>\n"
            f"<code>{escape(new_text)}</code>\n\n"
            "👆 <i>Click Copy Text to get the styled text.</i>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML,
        )

    except Exception as e:
        logger.exception(
            "Result message edit error: %s",
            e,
        )


# ============================================================
# COPY TEXT
# ============================================================

@Client.on_callback_query(filters.regex(r"^copy_"))
async def copy_text(client, query: CallbackQuery):

    copy_id = query.data[5:]

    text = COPY_CACHE.get(copy_id)

    if not text:
        await query.answer(
            "❌ Copy data expired. Apply the style again.",
            show_alert=True,
        )
        return

    # Telegram cannot directly put arbitrary bot text
    # into the user's clipboard.
    # So show the actual generated text.

    preview = text

    if len(preview) > 180:
        preview = preview[:180] + "..."

    await query.answer(
        f"📋 Styled Text:\n\n{preview}",
        show_alert=True,
    )


# ============================================================
# CLOSE
# ============================================================

@Client.on_callback_query(filters.regex(r"^close_font$"))
async def close_font(client, query: CallbackQuery):

    await query.answer("❌ Closed")

    try:
        await query.message.delete()
    except Exception as e:
        logger.debug(
            "Message deletion failed: %s",
            e,
        )

        try:
            await query.message.edit_text(
                "❌ <b>Closed</b>",
                reply_markup=None,
                parse_mode=ParseMode.HTML,
            )
        except Exception:
            pass
