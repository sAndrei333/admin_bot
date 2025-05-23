import sqlite3
from aiogram import Bot
import os
import speech_recognition as sr
from moviepy.editor import AudioFileClip
from aiogram import F
from aiogram.types import Message, KeyboardButton
from loader import (router, FORBIDEN_WORDS, user_violations, MAX_VIOLATIONS, MUTE_DURATION, MIN_VIOLATIONS, bot)
from datetime import timedelta, datetime
con = sqlite3.connect("data/data.db", check_same_thread=False)
cursor = con.cursor()
message = Message
async def send_end_mute(user_id,bot):
    await bot.send_message(text='вы снова можете писать в чат', chat_id=user_id)
#async def ban_member(user_id,bot):
#    await bot.ban_chat_member(chat_id='@+0HGdE2soYw5iMzky',user_id=user_id)




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
    print(user_violations)

    if user_id in user_violations:

        violations = user_violations[user_id]
        if violations['count'] >= MIN_VIOLATIONS:
            mute_end = violations['last_violations'] + timedelta(seconds=(1 + 1 * violations['count_viol']))

            if datetime.now() < mute_end:
                return True

            else:

                violations['count_viol'] += 1
                violations['count'] = violations['count']
                violations['last_violations'] = None
                #cursor.execute("INSERT INTO viols (count_violations, count, id) VALUES (?,?,?)",
                #               (violations['count_viol'], violations['count'], user_id))
                #con.commit()
                cursor.execute("UPDATE  viols SET count_violations = ?, count = ? WHERE id = ?",(violations['count_viol'],violations['count'] ))
                               #(violations['count_viol'], violations['count'], user_id))
                con.commit()
     #           if violations['count'] >= MAX_VIOLATIONS:
     #               return await ban_member(user_id, bot)
     #           else:
     #               return False

        return False


@router.message(F.voice)
async def handle_voice(message: Message):
    file_id = message.voice.file_id
    user_id = message.from_user.id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    ogg_path = f'temp/{message.chat.id}.ogg'
    await bot.download_file(file_path, ogg_path)
    audio_clip = AudioFileClip(ogg_path)
    wav_path = f'temp{message.chat.id}.wav'
    audio_clip.write_audiofile(wav_path, fps=44100)
    audio_clip.close()
    recognizer = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language='ru-RU')
        #await message.reply(f'Текст из гс: \n{text}')
    if os.path.exists(ogg_path):
        os.remove(ogg_path)
    if os.path.exists(wav_path):
        os.remove(wav_path)

    if await check_user_mut(user_id):
        violations = user_violations[user_id]
        await message.delete()
        await message.answer(
            f'@{message.from_user.username}, вы временно ограничены'f'в отправке сообщений на {1 + 5 * violations["count_viol"]} минут из-за частых нарушений.')
        return
    for word in FORBIDEN_WORDS:
        if word in text:
            await message.delete()
            await record_violations(user_id)
            await message.answer(
                f'@{message.from_user.username}, сообщение удалено:'f"содержит запрещённое слово. Нарушение#{user_violations[user_id]['count']}")



@router.message(F.text)
async def handle_message(message: Message):

    user_id = message.from_user.id
    #test = cursor.execute('SELECT id FROM viols')
    #if test in con:
    #    message.KeyboardButton(text="Капча")
    #    #async def capcha_compleated()

#



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
                f'@{message.from_user.username}, сообщение удалено:'f"содержит запрещённое слово. Нарушение#{user_violations[user_id]['count']}")
