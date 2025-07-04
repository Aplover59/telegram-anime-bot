import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

BOT_TOKEN = "7586718057:AAFP5rBK4xmS7wbJDz98PTX4T2JsyTPKd6U"
ANILIST_API = "https://graphql.anilist.co"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    mention = user.mention_html()
    msg = f"kya re bheekh mang gaya, kya hal hai {mention}"
    await update.message.reply_html(msg)

# Anime command
async def anime_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if not context.args:
            await update.message.reply_text("❌ Please give an anime name.")
            return

        query = " ".join(context.args)
        query_data = {
            'query': '''
            query ($search: String) {
              Media(search: $search, type: ANIME) {
                id
                idMal
                title {
                  romaji
                  english
                  native
                }
                source
                type
                status
                nextAiringEpisode {
                  airingAt
                  episode
                }
                genres
                tags {
                  name
                }
                siteUrl
                trailer {
                  site
                  id
                }
              }
            }
            ''',
            'variables': {
                'search': query
            }
        }

        response = requests.post(ANILIST_API, json=query_data)
        data = response.json()["data"]["Media"]

        title_en = data["title"]["english"] or data["title"]["romaji"]
        title_jp = data["title"]["native"]
        id_ = data["id"]
        mal_id = data["idMal"]
        source = data["source"]
        a_type = data["type"]
        status = data["status"]
        site = data["siteUrl"]

        genres = ", ".join(data["genres"])
        tags = ", ".join(tag["name"] for tag in data["tags"][:5])

        if data["nextAiringEpisode"]:
            from datetime import datetime
            from time import time
            seconds = data["nextAiringEpisode"]["airingAt"] - int(time())
            from datetime import timedelta
            airing_text = str(timedelta(seconds=seconds))
            airing = f"{airing_text} | {data['nextAiringEpisode']['episode']}th eps"
        else:
            airing = "N/A"

        text = f"""[🇯🇵]{title_en}\n        {title_jp}

ID | MAL ID: {id_} | {mal_id}
➤ SOURCE: {source}
➤ TYPE: {a_type}
➤ STATUS: {status}
➤ NEXT AIRING: {airing}
➤ GENRES: {genres}
➤ TAGS: {tags}
"""

        buttons = []
        if data["trailer"]:
            site = data["trailer"]["site"]
            trailer_id = data["trailer"]["id"]
            if site == "youtube":
                buttons.append([InlineKeyboardButton("🎬 Trailer", url=f"https://youtu.be/{trailer_id}")])
        buttons.append([InlineKeyboardButton("📖 Synopsis", url=site)])
        buttons.append([InlineKeyboardButton("📖 Official Site", url=site)])

        reply_markup = InlineKeyboardMarkup(buttons)
        await update.message.reply_text(text, reply_markup=reply_markup)

    except Exception as e:
        print(e)
        await update.message.reply_text("❌ Anime not found or error occurred.")

# Main bot runner
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("anime", anime_command))
    print("✅ Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
