import sqlite3
from aiogram.types import Message
from loader import (router, FORBIDEN_WORDS, user_violations, MAX_VIOLATIONS, MUTE_DURATION)
from datetime import timedelta, datetime
con = sqlite3.connect("data/data.db", check_same_thread=False)
cursor = con.cursor()
message = Message
async def record_violations(user_id):
    if user_id not in user_violations:
        user_violations[user_id] = {
            'count': 0,
            'last_violations': None,
            'count_viol': 0
        }

    violations = user_violations[user_id]
    violations['count'] += 1
    violations['last_violations'] = datetime.now()


async def check_user_mut(user_id):
    if user_id in user_violations:
        violations = user_violations[user_id]
        if violations['count'] % MAX_VIOLATIONS == 0:
            mute_end = violations[('last_violations'
                                   '')] + timedelta(minutes=(1 + 5 * violations['count_viol']))

            if datetime.now() < mute_end:
                return True
            else:

                violations['count_viol'] += 1
                violations['count'] = violations['count']
                violations['last_violations'] = None

                print(violations)
            cursor.execute("INSERT INTO viols (count_violations, count, id) VALUES (?,?,?)",(violations['count_viol'], violations['count'], user_id))
            con.commit()
            if violations['count']> 10:
                await message.bot.ban_chat_member()
            else:
                return False



        return False


@router.message()
async def handle_message(message: Message):
    user_id = message.from_user.id

    if await check_user_mut(user_id):
        violations = user_violations[user_id]
        await message.delete()
        await message.answer(
            f'@{message.from_user.username}, вы временно ограничены'f'в отправке сообщений на {1 + 5 * violations["count_viol"]} минут из-за частых нарушений.')
        return

    if message.entities:
        for entity in message.entities:
            if entity.type in ['url', 'text_link']:
                await message.delete()
                await record_violations(user_id)
                await message.answer(
                    f'@{message.from_user.username}, сообщение удалено:'f"содержит ссылку. Нарушение#{user_violations[user_id]['count']}")
                return

    text = message.text.lower()
    for word in FORBIDEN_WORDS:
        if word in text:
            await message.delete()
            await record_violations(user_id)
            await message.answer(
                f'@{message.from_user.username}, сообщение удалено:'f"содержит запреьное слово. Нарушение#{user_violations[user_id]['count']}")
