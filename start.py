from bot.bot import Bot
import dotenv
import os

dotenv.load_dotenv()

bot = Bot()
bot.run(os.getenv("TOKEN"))
