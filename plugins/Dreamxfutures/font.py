import logging
from plugins.Dreamxfutures.fotnt_string import Fonts
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.enums import ParseMode, ButtonStyle

logger = logging.getLogger(__name__)

# ============================================================
# PREMIUM FONT GENERATOR — WITH COLORFUL BUTTONS (USING style)
# ============================================================

@Client.on_message(filters.private & filters.command(["font", "fonts", "style"]))
async def style_buttons(c, m, cb=False):
    """Main Font Style Menu with Colorful Buttons"""
    
    buttons = [
        [
            InlineKeyboardButton('✨ 𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('🌀 𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline', style=ButtonStyle.INFO),
            InlineKeyboardButton('📝 𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif', style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton('🌸 𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('🌊 𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('📐 Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap', style=ButtonStyle.INFO),
        ],
        [
            InlineKeyboardButton('✍️ 𝓈𝒸𝓇𝒾𝓅𝓉', callback_data='style+script', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('🔥 𝓼𝓬𝓻𝓲𝓹𝓽', callback_data='style+script_bolt', style=ButtonStyle.DANGER),
            InlineKeyboardButton('🔹 ᵗⁱⁿʸ', callback_data='style+tiny', style=ButtonStyle.INFO),
        ],
        [
            InlineKeyboardButton('🎭 ᑕOᗰIᑕ', callback_data='style+comic', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('💎 𝗦𝗮𝗻𝘀', callback_data='style+sans', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('⚡ 𝙎𝙖𝙣𝙨', callback_data='style+slant_sans', style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton('🌙 𝘚𝘢𝘯𝘴', callback_data='style+slant', style=ButtonStyle.INFO),
            InlineKeyboardButton('⭐ 𝖲𝖺𝗇𝗌', callback_data='style+sim', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('⭕ Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎', callback_data='style+circles', style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton('🅾️ 🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎', callback_data='style+circle_dark', style=ButtonStyle.INFO),
            InlineKeyboardButton('🖤 𝔊𝔬𝔱𝔥𝔦𝔠', callback_data='style+gothic', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('💠 𝕲𝖔𝖙𝖍𝖎𝖈', callback_data='style+gothic_bolt', style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton('☁️ C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡', callback_data='style+cloud', style=ButtonStyle.INFO),
            InlineKeyboardButton('😊 H̆̈ă̈p̆̈p̆̈y̆̈', callback_data='style+happy', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('😢 S̑̈ȃ̈d̑̈', callback_data='style+sad', style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton('➡️ Next Page', callback_data="nxt", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('❌ Close', callback_data="close_font", style=ButtonStyle.DANGER),
        ]
    ]
    
    # User info
    user = m.from_user.mention if hasattr(m, 'from_user') else "User"
    
    if not cb:
        if ' ' in m.text:
            title = m.text.split(" ", 1)[1]
            await m.reply_text(
                f"🎨 <b>Premium Font Generator</b>\n\n"
                f"👤 <b>User:</b> {user}\n"
                f"📝 <b>Text:</b> <code>{title}</code>\n\n"
                f"<i>Select a font style below to transform your text!</i>\n"
                f"<b>🎨 Color Guide:</b>\n"
                f"🔵 Primary • 🟢 Success • 🔴 Danger • 🔷 Info",
                reply_markup=InlineKeyboardMarkup(buttons),
                reply_to_message_id=m.id,
                parse_mode=ParseMode.HTML
            )
        else:
            await m.reply_text(
                "🎨 <b>Premium Font Generator</b>\n\n"
                "📌 <b>Usage:</b> <code>/font [your text]</code>\n"
                "📝 <b>Example:</b> <code>/font Hello World</code>\n\n"
                "✨ <i>Select a style to transform your text!</i>\n"
                "🎨 <b>Color Guide:</b>\n"
                "🔵 Primary • 🟢 Success • 🔴 Danger • 🔷 Info",
                reply_markup=InlineKeyboardMarkup(buttons),
                parse_mode=ParseMode.HTML
            )
    else:
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex('^nxt'))
async def nxt(c, m: CallbackQuery):
    """Next Page — More Font Styles with Colorful Buttons"""
    if m.data == "nxt":
        buttons = [
            [
                InlineKeyboardButton('🌟 🇸 🇵 🇪 🇨 🇮 🇦 🇱 ', callback_data='style+special', style=ButtonStyle.PRIMARY),
                InlineKeyboardButton('🔲 🅂🅀🅄🄰🅁🄴🅂', callback_data='style+squares', style=ButtonStyle.SUCCESS),
                InlineKeyboardButton('🔳 🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎', callback_data='style+squares_bold', style=ButtonStyle.INFO),
            ],
            [
                InlineKeyboardButton('🌺 ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ', callback_data='style+andalucia', style=ButtonStyle.PRIMARY),
                InlineKeyboardButton('🍜 爪卂几ᘜ卂', callback_data='style+manga', style=ButtonStyle.SUCCESS),
                InlineKeyboardButton('💩 S̾t̾i̾n̾k̾y̾', callback_data='style+stinky', style=ButtonStyle.DANGER),
            ],
            [
                InlineKeyboardButton('🫧 B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ', callback_data='style+bubbles', style=ButtonStyle.INFO),
                InlineKeyboardButton('📏 U͟n͟d͟e͟r͟l͟i͟n͟e͟', callback_data='style+underline', style=ButtonStyle.PRIMARY),
                InlineKeyboardButton('🐞 ꒒ꍏꀷꌩꌃꀎꁅ', callback_data='style+ladybug', style=ButtonStyle.SUCCESS),
            ],
            [
                InlineKeyboardButton('☀️ R҉a҉y҉s҉', callback_data='style+rays', style=ButtonStyle.PRIMARY),
                InlineKeyboardButton('🐦 B҈i҈r҈d҈s҈', callback_data='style+birds', style=ButtonStyle.INFO),
                InlineKeyboardButton('⚔️ S̸l̸a̸s̸h̸', callback_data='style+slash', style=ButtonStyle.DANGER),
            ],
            [
                InlineKeyboardButton('🚫 s⃠t⃠o⃠p⃠', callback_data='style+stop', style=ButtonStyle.DANGER),
                InlineKeyboardButton('🌃 S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆', callback_data='style+skyline', style=ButtonStyle.INFO),
                InlineKeyboardButton('🏹 A͎r͎r͎o͎w͎s͎', callback_data='style+arrows', style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton('🔮 ዪሀክቿነ', callback_data='style+qvnes', style=ButtonStyle.SUCCESS),
                InlineKeyboardButton('✂️ S̶t̶r̶i̶k̶e̶', callback_data='style+strike', style=ButtonStyle.DANGER),
                InlineKeyboardButton('❄️ F༙r༙o༙z༙e༙n༙', callback_data='style+frozen', style=ButtonStyle.INFO),
            ],
            [
                InlineKeyboardButton('⬅️ Back', callback_data='nxt+0', style=ButtonStyle.PRIMARY),
                InlineKeyboardButton('❌ Close', callback_data='close_font', style=ButtonStyle.DANGER),
            ]
        ]
        
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    else:
        await style_buttons(c, m, cb=True)


@Client.on_callback_query(filters.regex('^style'))
async def style(c, m: CallbackQuery):
    """Apply Font Style and Show Result with Colorful Buttons"""
    await m.answer()
    
    try:
        cmd, style = m.data.split('+')
    except ValueError:
        await m.answer("❌ Invalid style format", show_alert=True)
        return
    
    # ============================================================
    # FONT STYLE MAPPING
    # ============================================================
    
    style_map = {
        'typewriter': Fonts.typewriter,
        'outline': Fonts.outline,
        'serif': Fonts.serief,
        'bold_cool': Fonts.bold_cool,
        'cool': Fonts.cool,
        'small_cap': Fonts.smallcap,
        'script': Fonts.script,
        'script_bolt': Fonts.bold_script,
        'tiny': Fonts.tiny,
        'comic': Fonts.comic,
        'sans': Fonts.san,
        'slant_sans': Fonts.slant_san,
        'slant': Fonts.slant,
        'sim': Fonts.sim,
        'circles': Fonts.circles,
        'circle_dark': Fonts.dark_circle,
        'gothic': Fonts.gothic,
        'gothic_bolt': Fonts.bold_gothic,
        'cloud': Fonts.cloud,
        'happy': Fonts.happy,
        'sad': Fonts.sad,
        'special': Fonts.special,
        'squares': Fonts.square,
        'squares_bold': Fonts.dark_square,
        'andalucia': Fonts.andalucia,
        'manga': Fonts.manga,
        'stinky': Fonts.stinky,
        'bubbles': Fonts.bubbles,
        'underline': Fonts.underline,
        'ladybug': Fonts.ladybug,
        'rays': Fonts.rays,
        'birds': Fonts.birds,
        'slash': Fonts.slash,
        'stop': Fonts.stop,
        'skyline': Fonts.skyline,
        'arrows': Fonts.arrows,
        'qvnes': Fonts.rvnes,
        'strike': Fonts.strike,
        'frozen': Fonts.frozen,
    }
    
    cls = style_map.get(style)
    if not cls:
        await m.answer("❌ Style not found", show_alert=True)
        return
    
    # ============================================================
    # GET ORIGINAL TEXT
    # ============================================================
    
    if m.message.reply_to_message and m.message.reply_to_message.text:
        try:
            oldtxt = m.message.reply_to_message.text.split(None, 1)[1]
        except (IndexError, AttributeError):
            oldtxt = m.message.text
    else:
        oldtxt = m.message.text
    
    if oldtxt.startswith('/font') or oldtxt.startswith('/fonts') or oldtxt.startswith('/style'):
        parts = oldtxt.split(None, 1)
        oldtxt = parts[1] if len(parts) > 1 else ''
    
    if not oldtxt or oldtxt.strip() == '':
        await m.answer("❌ No text found to style!", show_alert=True)
        return
    
    # ============================================================
    # APPLY FONT STYLE
    # ============================================================
    
    try:
        new_text = cls(oldtxt)
    except Exception as e:
        logger.error(f"Font style error: {e}")
        await m.answer("❌ Error applying style", show_alert=True)
        return
    
    # ============================================================
    # STYLE NAME MAPPING FOR DISPLAY
    # ============================================================
    
    style_names = {
        'typewriter': '𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛',
        'outline': '𝕆𝕦𝕥𝕝𝕚𝕟𝕖',
        'serif': '𝐒𝐞𝐫𝐢𝐟',
        'bold_cool': '𝑺𝒆𝒓𝒊𝒇',
        'cool': '𝑆𝑒𝑟𝑖𝑓',
        'small_cap': 'Sᴍᴀʟʟ Cᴀᴘs',
        'script': '𝓈𝒸𝓇𝒾𝓅𝓉',
        'script_bolt': '𝓼𝓬𝓻𝓲𝓹𝓽',
        'tiny': 'ᵗⁱⁿʸ',
        'comic': 'ᑕOᗰIᑕ',
        'sans': '𝗦𝗮𝗻𝘀',
        'slant_sans': '𝙎𝙖𝙣𝙨',
        'slant': '𝘚𝘢𝘯𝘴',
        'sim': '𝖲𝖺𝗇𝗌',
        'circles': 'Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎',
        'circle_dark': '🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎',
        'gothic': '𝔊𝔬𝔱𝔥𝔦𝔠',
        'gothic_bolt': '𝕲𝖔𝖙𝖍𝖎𝖈',
        'cloud': 'C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡',
        'happy': 'H̆̈ă̈p̆̈p̆̈y̆̈',
        'sad': 'S̑̈ȃ̈d̑̈',
        'special': '🇸 🇵 🇪 🇨 🇮 🇦 🇱 ',
        'squares': '🅂🅀🅄🄰🅁🄴🅂',
        'squares_bold': '🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎',
        'andalucia': 'ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ',
        'manga': '爪卂几ᘜ卂',
        'stinky': 'S̾t̾i̾n̾k̾y̾',
        'bubbles': 'B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ',
        'underline': 'U͟n͟d͟e͟r͟l͟i͟n͟e͟',
        'ladybug': '꒒ꍏꀷꌩꌃꀎꁅ',
        'rays': 'R҉a҉y҉s҉',
        'birds': 'B҈i҈r҈d҈s҈',
        'slash': 'S̸l̸a̸s̸h̸',
        'stop': 's⃠t⃠o⃠p⃠',
        'skyline': 'S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆',
        'arrows': 'A͎r͎r͎o͎w͎s͎',
        'qvnes': 'ዪሀክቿነ',
        'strike': 'S̶t̶r̶i̶k̶e̶',
        'frozen': 'F༙r༙o༙z༙e༙n༙',
    }
    
    style_display = style_names.get(style, style.upper())
    
    # ============================================================
    # GENERATE PREVIEW BUTTONS WITH COLORS
    # ============================================================
    
    buttons = [
        [
            InlineKeyboardButton(
                '📋 Copy Text',
                callback_data=f'copy_{new_text[:50]}',
                style=ButtonStyle.SUCCESS
            ),
            InlineKeyboardButton(
                '🔄 Back to Menu',
                callback_data='back_font',
                style=ButtonStyle.PRIMARY
            ),
        ],
        [
            InlineKeyboardButton(
                '❌ Close',
                callback_data='close_font',
                style=ButtonStyle.DANGER
            ),
        ]
    ]
    
    # ============================================================
    # SEND RESULT
    # ============================================================
    
    try:
        await m.message.edit_text(
            f"🎨 <b>Font Style Applied</b>\n\n"
            f"📝 <b>Style:</b> <code>{style_display}</code>\n"
            f"🔤 <b>Original:</b> <code>{oldtxt[:100]}</code>\n\n"
            f"✨ <b>Result:</b>\n"
            f"<code>{new_text}</code>\n\n"
            f"👆 <i>Click Copy to copy the styled text!</i>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Edit message error: {e}")
        await m.message.edit_text(
            f"✨ <b>Styled Text</b>\n\n"
            f"<code>{new_text}</code>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=ParseMode.HTML
        )


@Client.on_callback_query(filters.regex('^copy_'))
async def copy_text(c, m: CallbackQuery):
    """Copy Text to Clipboard (simulated)"""
    await m.answer()
    text = m.data.replace('copy_', '')[:50]
    await m.answer(f"✅ Text copied!\n\n{text}...", show_alert=True)


@Client.on_callback_query(filters.regex('^back_font'))
async def back_to_menu(c, m: CallbackQuery):
    """Return to Main Font Menu with Colorful Buttons"""
    await m.answer()
    
    # Get original text from message
    text = m.message.text
    import re
    match = re.search(r'🔤 <b>Original:</b> <code>(.*?)</code>', text)
    if match:
        original_text = match.group(1)
    else:
        original_text = "text"
    
    buttons = [
        [
            InlineKeyboardButton('✨ 𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('🌀 𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline', style=ButtonStyle.INFO),
            InlineKeyboardButton('📝 𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif', style=ButtonStyle.PRIMARY),
        ],
        [
            InlineKeyboardButton('🌸 𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('🌊 𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('📐 Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap', style=ButtonStyle.INFO),
        ],
        [
            InlineKeyboardButton('✍️ 𝓈𝒸𝓇𝒾𝓅𝓉', callback_data='style+script', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('🔥 𝓼𝓬𝓻𝓲𝓹𝓽', callback_data='style+script_bolt', style=ButtonStyle.DANGER),
            InlineKeyboardButton('🔹 ᵗⁱⁿʸ', callback_data='style+tiny', style=ButtonStyle.INFO),
        ],
        [
            InlineKeyboardButton('🎭 ᑕOᗰIᑕ', callback_data='style+comic', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('💎 𝗦𝗮𝗻𝘀', callback_data='style+sans', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('⚡ 𝙎𝙖𝙣𝙨', callback_data='style+slant_sans', style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton('🌙 𝘚𝘢𝘯𝘴', callback_data='style+slant', style=ButtonStyle.INFO),
            InlineKeyboardButton('⭐ 𝖲𝖺𝗇𝗌', callback_data='style+sim', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('⭕ Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎', callback_data='style+circles', style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton('🅾️ 🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎', callback_data='style+circle_dark', style=ButtonStyle.INFO),
            InlineKeyboardButton('🖤 𝔊𝔬𝔱𝔥𝔦𝔠', callback_data='style+gothic', style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('💠 𝕲𝖔𝖙𝖍𝖎𝖈', callback_data='style+gothic_bolt', style=ButtonStyle.SUCCESS),
        ],
        [
            InlineKeyboardButton('☁️ C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡', callback_data='style+cloud', style=ButtonStyle.INFO),
            InlineKeyboardButton('😊 H̆̈ă̈p̆̈p̆̈y̆̈', callback_data='style+happy', style=ButtonStyle.SUCCESS),
            InlineKeyboardButton('😢 S̑̈ȃ̈d̑̈', callback_data='style+sad', style=ButtonStyle.DANGER),
        ],
        [
            InlineKeyboardButton('➡️ Next Page', callback_data="nxt", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton('❌ Close', callback_data="close_font", style=ButtonStyle.DANGER),
        ]
    ]
    
    await m.message.edit_text(
        f"🎨 <b>Premium Font Generator</b>\n\n"
        f"📝 <b>Current Text:</b> <code>{original_text[:50]}</code>\n\n"
        f"<i>Select a font style to transform your text!</i>\n"
        f"<b>🎨 Color Guide:</b>\n"
        f"🔵 Primary • 🟢 Success • 🔴 Danger • 🔷 Info",
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=ParseMode.HTML
    )


@Client.on_callback_query(filters.regex('^close_font'))
async def close_font(c, m: CallbackQuery):
    """Close Font Generator"""
    await m.answer("❌ Closed", show_alert=False)
    try:
        await m.message.delete()
    except Exception:
        await m.message.edit_text("❌ Closed", reply_markup=None)    if style == 'serif':
        cls = Fonts.serief
    if style == 'bold_cool':
        cls = Fonts.bold_cool
    if style == 'cool':
        cls = Fonts.cool
    if style == 'small_cap':
        cls = Fonts.smallcap
    if style == 'script':
        cls = Fonts.script
    if style == 'script_bolt':
        cls = Fonts.bold_script
    if style == 'tiny':
        cls = Fonts.tiny
    if style == 'comic':
        cls = Fonts.comic
    if style == 'sans':
        cls = Fonts.san
    if style == 'slant_sans':
        cls = Fonts.slant_san
    if style == 'slant':
        cls = Fonts.slant
    if style == 'sim':
        cls = Fonts.sim
    if style == 'circles':
        cls = Fonts.circles
    if style == 'circle_dark':
        cls = Fonts.dark_circle
    if style == 'gothic':
        cls = Fonts.gothic
    if style == 'gothic_bolt':
        cls = Fonts.bold_gothic
    if style == 'cloud':
        cls = Fonts.cloud
    if style == 'happy':
        cls = Fonts.happy
    if style == 'sad':
        cls = Fonts.sad
    if style == 'special':
        cls = Fonts.special
    if style == 'squares':
        cls = Fonts.square
    if style == 'squares_bold':
        cls = Fonts.dark_square
    if style == 'andalucia':
        cls = Fonts.andalucia
    if style == 'manga':
        cls = Fonts.manga
    if style == 'stinky':
        cls = Fonts.stinky
    if style == 'bubbles':
        cls = Fonts.bubbles
    if style == 'underline':
        cls = Fonts.underline
    if style == 'ladybug':
        cls = Fonts.ladybug
    if style == 'rays':
        cls = Fonts.rays
    if style == 'birds':
        cls = Fonts.birds
    if style == 'slash':
        cls = Fonts.slash
    if style == 'stop':
        cls = Fonts.stop
    if style == 'skyline':
        cls = Fonts.skyline
    if style == 'arrows':
        cls = Fonts.arrows
    if style == 'qvnes':
        cls = Fonts.rvnes
    if style == 'strike':
        cls = Fonts.strike
    if style == 'frozen':
        cls = Fonts.frozen

    if m.message.reply_to_message and m.message.reply_to_message.text:
        try:
            oldtxt = m.message.reply_to_message.text.split(None, 1)[1]
        except IndexError:
            oldtxt = m.message.text
    else:
        oldtxt = m.message.text
    new_text = cls(oldtxt)            
    try:
        await m.message.edit_text(f"`{new_text}`\n\n👆 Click To Copy", reply_markup=m.message.reply_markup)
    except Exception as e:
        logger.error("Font style edit error: %s", e)



