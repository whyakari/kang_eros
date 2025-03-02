import asyncio
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import InputMediaVideo, Message


API_ID = 16250076
API_HASH = "0c5072b4b1856afb02f740f019e1d4c8"
GROUP_IDS = [-1001569019041, -1001529020845]  # Lista de grupos
TOPIC_IDS = [8692, 15942]
CHANNEL_ID = -1002258271828  # Canal de destino

app = Client(
    name="xd",
    api_id=API_ID,
    api_hash=API_HASH
)

media_groups = defaultdict(list)
processing = set()  # Evita envios duplicados

def get_topic_id(message: Message):
    return getattr(message, "reply_to_message_id", None)

def topic_filter(_, __, message: Message):
    topic_id = get_topic_id(message)
    return topic_id in TOPIC_IDS if topic_id else False

@app.on_message(filters.chat(GROUP_IDS) & filters.text)
async def test(c: Client, m: Message):
    print(get_topic_id(m))

@app.on_message(filters.chat(GROUP_IDS) & filters.video & filters.media_group & filters.create(topic_filter))
async def collect_videos(c: Client, message: Message):
    """ Coleta e envia álbuns de vídeos completos. """
    try:
        media_group_id = message.media_group_id
        if not media_group_id:
            return  # Ignora se não for um álbum

        media_groups[media_group_id].append(InputMediaVideo(message.video.file_id, caption=message.caption))

        await asyncio.sleep(5)  # Aguarda todas as mídias chegarem

        if media_group_id not in processing:
            processing.add(media_group_id)

            if len(media_groups[media_group_id]) > 1:
                await c.send_media_group(chat_id=CHANNEL_ID, media=media_groups[media_group_id])
                print(f"✅ Álbum enviado do tópico {get_topic_id(message)} ({message.chat.id})")
            else:
                print(f"⚠️ Álbum ignorado (só tinha 1 mídia) do tópico {get_topic_id(message)}")

            del media_groups[media_group_id]
            processing.remove(media_group_id)

    except Exception as e:
        print(f"❌ Erro ao processar álbum de {message.chat.id}: {e}")

@app.on_message(filters.chat(GROUP_IDS) & filters.video & ~filters.media_group & filters.create(topic_filter))
async def forward_single_video(c: Client, message: Message):
    """ Encaminha vídeos únicos apenas dos tópicos selecionados. """
    try:
        await c.send_video(chat_id=CHANNEL_ID, video=message.video.file_id, caption=message.caption)
        print(f"🎥 Vídeo único enviado do tópico {get_topic_id(message)}")

    except Exception as e:
        print(f"❌ Erro ao enviar vídeo único do tópico {get_topic_id(message)}: {e}")

print("running...")
app.run()
