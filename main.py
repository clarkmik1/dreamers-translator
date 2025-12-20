import os
import re
import discord
from discord.ext import commands
from googletrans import Translator
from dotenv import load_dotenv

# Load .env
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Discord intents
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
translator = Translator()

# Language detection via channel name
LANG_CHANNEL_KEYWORDS = {
    "en": ["english", "eng"],
    "tl": ["filipino", "tagalog", "tl"]
}


def get_language_from_channel(channel_name):
    channel_name = channel_name.lower()
    for lang, keywords in LANG_CHANNEL_KEYWORDS.items():
        for kw in keywords:
            if kw in channel_name:
                return lang
    return None


# =============================
# 🔧 PRE-TRANSLATION SLANG / SHORTCUTS / TAGLISH FIXES
# =============================
SLANG_FIXES = {
    r"\bG\b": "Maglaro",
    r"\bGG\b": "Magandang laro",
    r"\bWP\b": "Magaling na laro",
    r"\bAFK\b": "Hindi available",
    r"\bBRB\b": "Babalik agad",
    r"\bDC\b": "Nawalan ng koneksyon",
    r"\bLag\b": "Mabagal ang internet",
    r"\bPush\b": "Ituloy",
    r"\bDef\b": "Magdepensa",
    r"\bDef muna\b": "Magdepensa muna",
    r"\bWait lang\b": "Maghintay lang",
    r"\bWait\b": "Maghintay",
    r"\bSaglit\b": "Sandali",
    r"\bIRL\b": "Sa totoong buhay",
    r"\bEz\b": "Madali lang",
    r"\bAwit\b": "Nakakainis",
    r"\bAray\b": "Masakit",
    r"\bSayang\b": "Nakakainis",
    r"\bOlats\b": "Talunan",
    r"\bLupet\b": "Kahanga-hanga",
    r"\bMalupet\b": "Kahanga-hanga",
    r"\bSolid\b": "Magaling",
    r"\bTangina\b": "Nakakainis",
    r"\bPut\b": "Nakakainis",
    r"\bGago\b": "Tanga",
    r"\bUlol\b": "Tanga",
    r"\bLods\b": "Kaibigan",
    r"\bLod\b": "Kaibigan",
    r"\bTara\b": "Tara / Halina",
    r"\bBawi\b": "Bumawi",
    r"\bNice\b": "Maganda",
    r"\bWtf\b": "Ano ba",
    r"\btlga\b": "talaga",
    r"\byait\b": "nakakadisappoint",
    r"\bumay\b": "sawa na",
    r"\bCringe\b": "Nakakahiya",
    r"\bSus\b": "Susmaryosep",
    r"\bPetmalu\b": "Astig",
    r"\bWerpa\b": "Malakas",
    r"\bJowa\b": "Kasintahan",
    r"\bBes\b": "Kaibigan",
    r"\bBeshi\b": "Kaibigan",
    r"\bLodi\b": "Idol",
    r"\bHugot\b": "Malalim na damdamin",
    r"\bChika\b": "Kwento",
    r"\bChismis\b": "Balita",
    r"\bEme\b": "Walang kwenta",
    r"\bEpal\b": "Nakaka-abala",
    r"\bTakaw-tingin\b": "Na-attract agad",
    r"\bWalwal\b": "Labis na inom",
    r"\bBasag\b": "Pasaway",
    r"\bBasag ulo\b": "Pasaway",
    r"\bPabebe\b": "Pa-cute",
    r"\bJeproks\b": "Cool",
    r"\bHugot lines\b": "Malalim na linya",
    r"\bKilig\b": "Masaya sa kilig",
    r"\bKengkoy\b": "Nakakatawa",
    # Taglish shortcuts
    r"\bnmin\b": "namin",
    r"\bnamin\b": "namin",
    r"\bdin\b": "din",
    r"\bun\b": "yun",
    r"\bsows\b": "oops",
    r"\btinry\b": "sinubukan",
    r"\bbayag\b": "balls",
    r"\btiti\b": "penis",
    r"\buten\b": "penis"
}


def apply_slang_fixes(text):
    for pattern, replacement in SLANG_FIXES.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


# =============================
# Discord Events
# =============================
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.event
async def on_message(message):
    # ignore bots & embeds (prevent loop)
    if message.author.bot or message.embeds:
        return

    source_lang = get_language_from_channel(message.channel.name)
    if not source_lang:
        return

    # Apply pre-translation fixes
    fixed_text = apply_slang_fixes(message.content)

    for channel in message.guild.text_channels:
        target_lang = get_language_from_channel(channel.name)
        if not target_lang or target_lang == source_lang:
            continue

        try:
            translated = translator.translate(fixed_text,
                                              src=source_lang,
                                              dest=target_lang)

            embed = discord.Embed(description=translated.text, color=0x00ffcc)
            embed.set_author(name=message.author.display_name,
                             icon_url=message.author.avatar.url
                             if message.author.avatar else None)
            embed.set_footer(text="Dreamers's Translator 🌐")

            await channel.send(embed=embed)

        except Exception as e:
            print(f"Translation error in channel {channel.name}: {e}")

    await bot.process_commands(message)


bot.run(TOKEN)
