import asyncio
from collections import defaultdict
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InputMediaVideo, Message

API_ID = 16250076
API_HASH = "0c5072b4b1856afb02f740f019e1d4c8"
BOT_TOKEN = "7765232747:AAHkIHzPF09vdeLTDdTNe3YRlupLlLpuh38"

CHANNEL_ID = -1002258271828
GROUP_ID = -1002288795348

app = Client(
    name="slas",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

media_groups = defaultdict(list)
processing = set()

@app.on_message(filters.chat(CHANNEL_ID) & filters.video & filters.media_group)
async def collect_videos(c: Client, message: Message):
    """ Coleta e envia álbuns de vídeos completos. """
    try:
        media_group_id = message.media_group_id
        if not media_group_id:
            return

        media_groups[media_group_id].append(InputMediaVideo(message.video.file_id, caption=message.caption))

        await asyncio.sleep(5)

        if media_group_id not in processing:
            processing.add(media_group_id)

            if len(media_groups[media_group_id]) > 1:
                await c.send_media_group(
                    chat_id=GROUP_ID, 
                    media=media_groups[media_group_id]
                )

                print(f"✅ Álbum enviado ({message.chat.id})")
            else:
                print(f"⚠️ Álbum ignorado (só tinha 1 mídia) do tópico")

            del media_groups[media_group_id]
            processing.remove(media_group_id)

    except Exception as e:
        print(f"❌ Erro ao processar álbum de {message.chat.id}: {e}")

@app.on_message(filters.chat(CHANNEL_ID) & filters.video & ~filters.media_group)
async def forward_single_video(c: Client, message: Message):
    """ Encaminha vídeos únicos apenas dos tópicos selecionados. """
    try:
        await c.send_video(
            chat_id=GROUP_ID, 
            video=message.video.file_id
        ) 

        print(f"🎥 Vídeo único enviado do tópico")

    except Exception as e:
        print(f"❌ Erro ao enviar vídeo único do tópico: {e}")

print("running...")
app.run()
