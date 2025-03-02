import asyncio
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import InputMediaVideo, Message

API_ID = 16250076
API_HASH = "0c5072b4b1856afb02f740f019e1d4c8"
GROUP_ID = -1001529020845  # Grupo de origem
CHANNEL_ID = -1002258271828  # Canal de destino

app = Client(
    name="xd",
    api_id=API_ID,
    api_hash=API_HASH
)

media_groups = defaultdict(list)
processing = set()

@app.on_message(filters.chat(GROUP_ID) & filters.video & filters.media_group)
async def collect_videos(c: Client, message: Message):
    """ Coleta vídeos de um álbum e os envia apenas quando todos forem recebidos. """
    try:
        media_group_id = message.media_group_id
        if not media_group_id:
            return

        media_groups[media_group_id].append(InputMediaVideo(message.video.file_id, caption=message.caption))

        await asyncio.sleep(5)  

        if media_group_id not in processing:
            processing.add(media_group_id)

            if len(media_groups[media_group_id]) > 1:
                await c.send_media_group(chat_id=CHANNEL_ID, media=media_groups[media_group_id])
                print(f"✅ Álbum enviado: {media_group_id}")
            else:
                print(f"⚠️ Álbum ignorado: {media_group_id}")

            del media_groups[media_group_id]
            processing.remove(media_group_id)

    except Exception as e:
        print(f"❌ Erro ao processar álbum: {e}")

print("running...")
app.run()

