from telegram.ext import MessageHandler, filters, CommandHandler,ApplicationBuilder
from lyricsgenius import Genius
import re

genius = Genius('GENIUS-API-TOKEN')

TOKEN = "TELEGRAM-BOT-TOKEN"
async def start(update, context):
    await update.message.reply_text("Hello\! With the help of this bot, you can easily find music lyrics\.\nSimply *send an audio file* or a text in the following format:\n `ARTIST\-TRACKNAME`\nFor example, if you want the lyrics for \"Bohemian Rhapsody\" by Queen, just send *Queen\-Bohemian Rhapsody*\.",parse_mode='MarkdownV2')

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, channel_respomse))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE, private_chat_response))
    app.add_handler(MessageHandler(filters.ChatType.GROUPS, group_response))

    app.run_polling()

async def send_message(chat_id, text, bot,parse_mode=None):
    while text:
        await bot.send_message(chat_id, text[:3000], parse_mode)
        text = text[3000:]

async def edit_message(sent_message,text,bot):
    await bot.editMessageText(chat_id=sent_message.chat_id,message_id=sent_message.message_id, text=text[:3000])
    if len(text) > 3000 : await bot.send_message(sent_message.chat_id,text[3000:])

async def is_member(update, context):
    userid = update.effective_user.id
    chatid = "@AJ_Pll"  # replace with your channel username
    try:
        res = await context.bot.get_chat_member(chat_id=chatid, user_id=userid)
        print(res.status)
        if res.status in ['member', 'administrator','creator']:
            return True
    except Exception as e:
        return False


# regex pattern to match "ARTIST-TRACKNAME"
pattern = r"^[A-Za-z0-9\s]+-[A-Za-z0-9\s]+$"
def validate_message(message):
    return message.audio or (re.match(pattern, message.text) and len(message.text)<35)

async def private_chat_response(update, context):
    if not await is_member(update, context):
        await update.message.reply_text("you have to join <a href='t.me/aj_pll'>my channel</a> in order to use this bot ㄟ( ▔, ▔ )ㄏ",parse_mode='html')
        return
    if validate_message(update.message) :
        await send_lyrics(update.message,context)
    else :
        await update.message.reply_text("Please send a music file or a text in the following format:\n `ARTIST\-TRACKNAME`\nFor example, if you want the lyrics for \"Bohemian Rhapsody\" by Queen, just send *Queen\-Bohemian Rhapsody*\.",parse_mode='MarkdownV2')

async def channel_respomse(update, context):
    # await context.bot.send_message(chat_id=-1002028164723, text=f'Channel message : {update}')
    return
    
async def group_response(update, context):
    if validate_message(update.message):
        await send_lyrics(update.message,context)

async def send_lyrics(message,context):
    if message.audio :
        await context.bot.send_audio(chat_id=-1002028164723, audio=message.audio.file_id)   
        await context.bot.send_audio(chat_id=-1002145175837, audio=message.audio.file_id)   
        artist_name, track_name = message.audio.performer,message.audio.title
    else : 
        artist_name, track_name = message.text.split('-')
    await context.bot.send_message(chat_id=-1002028164723, text=f'User @{message.from_user["username"]},{message.chat_id} searched for {artist_name+" - "+track_name}')
    sent_message = await message.reply_text(f"⌛Searching for {track_name} By {artist_name} ...")
    try:
        artist = genius.search_artist(artist_name, max_songs=0)
        track = genius.search_song(track_name, artist.name)
        lyrics = clean_lyrics(track.lyrics)
        lyrics = f"🗣 : {track.artist}\n💿 : {track.title}\n🤖 : @Lyricsr_bot \n---------------------------\n{lyrics}"
        await edit_message(sent_message, text=lyrics,bot = context.bot)
        await send_message(chat_id=-1002145175837, text=f'{lyrics} \n---------------------------\n#{artist_name.strip().replace(" ","_")}',bot = context.bot)
        await log_channel(message,context,lyrics)
    except Exception as error:
        await log_channel(message,context,error)
        await edit_message(sent_message ,text=f"Could not find lyrics for : {artist_name} - {track_name}",bot = context.bot)

async def log_channel(message,context,error="None",lyrics="None"):
    await send_message(chat_id=-1002028164723,text= f'👤 : @{message.from_user["username"]},{message.chat_id} \n{error}' if error!="None" else f'👤 : @{message.from_user["username"]},{message.chat_id} \n{lyrics}',parse_mode="html",bot = context.bot)

def clean_lyrics(text):
    # Extract the lyrics
    if not "Contributor" in text:return text
    start = text.find("Lyrics") + len("Lyrics")
    end = text.rfind("Embed")
    lyrics = text[start:end].strip().removesuffix("You might also like")
    return ''.join(char for char in lyrics.rstrip() if not char.isdigit())

if __name__ == '__main__':
    main()
