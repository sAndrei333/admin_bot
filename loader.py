from aiogram import Bot, Dispatcher,Router
from config.token import TOKEN
router = Router()
dp = Dispatcher()
dp.include_router(router)
bot= Bot(TOKEN)
id=[485296374]


FORBIDEN_WORDS  =['спам', 'реклама', 'взлом']
user_violations = {}
MIN_VIOLATIONS = 1
MID_VIOLATIONS = 2
MAX_VIOLATIONS = 1
MUTE_DURATION  = [1, 2, 3]