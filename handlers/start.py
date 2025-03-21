from loader import router
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
@router.message()
async def start(message: Message):
    message.chat.text('hi')