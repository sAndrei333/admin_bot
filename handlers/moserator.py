from aiogram.types import Message
from loader import (router, FORBIDEN_WORDS, user_violations, MAX_VIOLATIONS, MUTE_DURATION )
from datetime import timedelta, datetime

async def record_violations(user_id):
    if user_id not in user_violations:
        user_violations[user_id] = {
            'count': 0,
            'last_violations': None
        }

        violations = user_violations[user_id]
        violations['count'] += 1
        violations['last_violations'] = datetime.now()

async def check_user_mut(user_id):
    if user_id in user_violations:
        violations = user_violations[user_id]
        if violations['count'] == MAX_VIOLATIONS[1]:
            mute_end = violations['last_violations']+ timedelta(minutes=MUTE_DURATION[1])
            if datetime.now()< mute_end:
                return True
            else:
                user_violations[user_id]= {'count':0, 'last_violations': None}
       #if violations['count'] == MAX_VIOLATIONS[2]:
       #    mute_end = violations['last_violations']+ timedelta(minutes=MUTE_DURATION[2])
       #    if datetime.now()< mute_end:
       #        return True
       #    else:
       #        user_violations[user_id]= {'count':0, 'last_violations': None}
       #if violations['count'] == MAX_VIOLATIONS[3]:
       #    mute_end = violations['last_violations']+ timedelta(minutes=MUTE_DURATION[3])
       #    if datetime.now()< mute_end:
       #        return True
       #    else:
       #        user_violations[user_id]= {'count':0, 'last_violations': None}
    return False
@router.message()

async def handle_message(message: Message):
    user_id = message.from_user.id
    if await check_user_mut(user_id):
        await message.delete()
        await message.answer(f'@{message.from_user.username}, вы временно ограничены'f'в отправке сообщений на {MUTE_DURATION} минут из-за частых нарушений.')
        return

    if message.entities:
        for entity in message.entities:
             if  entity.type in ['url', 'text_link']:
                await message.delete()
                await record_violations(user_id)
                await message.answer(f'@{message.from_user.username}, сообщение удалено:'f"содержит ссылку. Нарушение#{user_violations[user_id]['count']}")
                return

    text = message.text.lower()
    for word in FORBIDEN_WORDS:
        if word in text:
            await message.delete()
            await record_violations(user_id)
            await message.answer(f'@{message.from_user.username}, сообщение удалено:'f"содержит запреьное слово. Нарушение#{user_violations[user_id]['count']}")

