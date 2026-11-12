import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.environ.get("API_ID", "24799187"))
API_HASH = os.environ.get("API_HASH", "4baef40b8f24b66a25ccd232861186ed")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "9112714195:AAHV8FyuG2l26QbNYNlxRAdenZbq1p_sDIA")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://kishanshiratti229_db_user:yfZlxgMTwtD5Pm2i@cinhub4u.fe0zi4f.mongodb.net/")
DB_NAME = "TjBotDB"

# מנהלים: ניתן להוסיף כמה מנהלים מופרדים ברווח או פסיק
ADMINS = [int(x) for x in os.environ.get("ADMINS", "5000162773").replace(",", " ").split()]

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1004389792638"))
UPDATE_CHANNEL = "Cinhub4u"
REQUEST_GROUP = "https://t.me/Cinhub4uDisc"

PHOTO_URL = "https://i.ibb.co/NdD7dvfn/11f780e1bdc0.jpg"

AUTH_CHANNEL_FORCE = os.environ.get("AUTH_CHANNEL_FORCE", "False").lower() == "true"
