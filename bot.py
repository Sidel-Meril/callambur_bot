#!/usr/bin/python
# -*- coding: UTF-8 -*-

import telegram.ext
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram.ext.dispatcher import run_async
import json
import random
import imageprocessing
import sqlcon
import os

variables = {
  "telegram": {
    "token": os.environ['TELEGRAM_TOKEN'],
    "admin_id": int(os.environ['ADMIN_ID'])
  },
  "database": {
    "link": os.environ['DATABASE_URL']}
}

#init bot
updater = Updater(variables['telegram']['token'], workers=10, use_context=True)
PORT = int(os.environ.get('PORT', '8443'))

def user(func):
    def check_user(update, contex, *args, **kwargs):
        user_id = update.message.chat.id
        db = sqlcon.Database(database_url=variables['database']['link'])
        users = db.get_users()
        users = [user[0] for user in users]
        if user_id not in users:
            print('User undefined')
            try:
                db.add_user(user_id)
            except:
                pass
        else:
            print('User recognized')
        db.close()
        func(update, contex, *args, **kwargs)

    return check_user

def admin(func):
    def wrapper(update, context, *args, **kwargs):
        user_id = update.message.chat.id
        print(user_id, variables['telegram']['admin_id'], user_id == variables['telegram']['admin_id'])
        if user_id != variables['telegram']['admin_id']:
            return None
        print('Hi, my little queen Sidel Meril')
        res = func(update, context, *args, **kwargs)
        return res
    return wrapper

@user
def welcome(update, context):
    user_id = update.message.chat.id
    user_pic = updater.dispatcher.bot.getUserProfilePhotos(user_id=user_id)
    print(user_pic)
    if len(user_pic['photos'])>0:
        file_id = user_pic['photos'][0][0]['file_id']
        file = updater.dispatcher.bot.getFile(file_id)
        file_url = file.file_path
    else:
        file_url = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRnw6GLZgBpcaA5s_idbxI23TVcc4w7DgkR9GlR8WmcXqxyC-J6S7JikTWaRfoON62gPb4&usqp=CAU"
    user_pic=imageprocessing.get_img(file_url)
    db = sqlcon.Database(variables['database']['link'])
    add = db.get_pic_by_id(12)[0]
    print(add)
    result = imageprocessing.set_pic(user_pic, add[1], (add[2], add[3]), (add[4], add[5]))
    bio = imageprocessing.convert_to_bio(result)
    welcome_message = """<b>Доброго дня, %s</b> 
     
Ви ніколи не будете на рекламі льонокомбінату "Goldi", але цей бот пропонує конкурентоспроможну альтернативу.
<b>Ви маєте це знати: /help </b>""" %update.message.chat.first_name
    updater.dispatcher.bot.send_photo(chat_id=user_id, photo=bio, caption=welcome_message, parse_mode="HTML")

@user
def help(update, context):
    user_id = update.message.chat.id
    help_message="""<b>Лорд Нероссійский Чел 2.0</b> - це справжня <a href="https://uk.wikipedia.org/wiki/%D0%86%D0%BD%D1%82%D0%B5%D1%80%D0%BD%D0%B5%D1%82">інтернет-розвага</a>, яку декілька років тому молживо було побачити лише на обкладинках зошитів <a href="https://1veresnya.com/"><b><i>"1 вересня"</i></b></a>.

З оновленням <i>2.0</i> ви маєте змогу отримати ще більше насолоди. 
Файли, що бот приймає до обробки:
- <i> Зображення </i><a href="https://uk.wikipedia.org/wiki/%D0%97%D0%BE%D0%B1%D1%80%D0%B0%D0%B6%D0%B5%D0%BD%D0%BD%D1%8F">[?]</a> <pre>  /pic</pre>
- <i> Статичні наліпки </i><a href="https://uk.wikipedia.org/wiki/%D0%9D%D0%B0%D0%BA%D0%BB%D0%B5%D0%B9%D0%BA%D0%B0">[?]</a> <pre>  /stc</pre>
- <i> Анімація </i><a href="https://uk.wikipedia.org/wiki/%D0%90%D0%BD%D1%96%D0%BC%D0%B0%D1%86%D1%96%D1%8F">[?]</a> <pre>  /gif</pre>

Для отримання видимого результату, надішліть один з вказаних вище файлів. Для чатів використовуйте вказані получ команди.

<pre>/help - отримати інструкцію
/start - розпочати користування

Якщо в вас є бажання покращити проект
/sug - пересилає повідомлення до адміна</pre>

<b>Прес-служба ООО "Вибачте, я нероссійська людина"</b>: 
@unrussianman
<b>Системний адміністратор комп'ютерного клубу</b>: 
@sidel_meril

    """

    updater.bot.send_message(chat_id=user_id, text=help_message, parse_mode='HTML')

@admin
def help_admin(update, context):
    user_id = update.message.chat.id
    help_message = """
    Команди для директору заводу:
    /a_a_usrs - розповісти всім юзерам боту анекдот
    /ad_p_adm - додати зображення до бази приколів
    /get_a_p_adm - переглянути базу зображень
    /stat_a_sid_m - статистика користування ботом
    /del_p_adm_id_(int_id) - видалити зображення за id
    """
    # set parse message mood

    #
    updater.bot.send_message(chat_id=user_id, text=help_message)



@user
def create_add_from_pic(update, context):
    user_id = update.message.chat.id
    try:
        file_id = update.message.photo[-1].file_id
    except:
        file_id = update.message.reply_to_message.photo[-1].file_id
    file = updater.dispatcher.bot.getFile(file_id)
    file_url = file.file_path
    user_pic = imageprocessing.get_img(file_url)
    db = sqlcon.Database(variables['database']['link'])
    add = db.get_random_pic()[0]
    result = imageprocessing.set_pic(user_pic, add[1], (add[2], add[3]), (add[4], add[5]))
    bio = imageprocessing.convert_to_bio(result)
    updater.dispatcher.bot.send_photo(chat_id=user_id, photo=bio)

@user
def create_add_from_gif(update, context):
    user_id = update.message.chat.id
    try:
        file_id = update.message.animation.file_id
    except:
        file_id = update.message.reply_to_message.animation.file_id
    file = updater.dispatcher.bot.getFile(file_id)
    file_url = file.file_path
    user_gif = imageprocessing.get_gif(file_url)
    db = sqlcon.Database(variables['database']['link'])
    add = db.get_random_pic()[0]
    db.close()
    frames=imageprocessing.set_frames(user_gif, add[1], (add[2], add[3]), (add[4], add[5]))
    bio = imageprocessing.conver_gif_to_bio(frames)
    updater.dispatcher.bot.send_animation(chat_id=user_id, animation=bio)

@user
def create_add_from_sticker(update, context):
    user_id = update.message.chat.id
    try:
        file_id = update.message.sticker.file_id
    except:
        file_id = update.message.reply_to_message.sticker.file_id
    file = updater.dispatcher.bot.getFile(file_id)
    file_url = file.file_path
    if 'webm' in file_url:
        user_gif = imageprocessing.get_gif(file_url)
        db = sqlcon.Database(variables['database']['link'])
        add = db.get_random_pic()[0]
        db.close()
        frames = imageprocessing.set_frames(user_gif, add[1], (add[2], add[3]), (add[4], add[5]))
        bio = imageprocessing.conver_gif_to_bio(frames)
    else:
        user_pic = imageprocessing.get_img(file_url)
        db = sqlcon.Database(variables['database']['link'])
        add = db.get_random_pic()[0]
        result = imageprocessing.set_pic(user_pic, add[1], (add[2], add[3]), (add[4], add[5]))
        bio = imageprocessing.convert_to_bio(result)
    updater.dispatcher.bot.send_photo(chat_id=user_id, photo=bio)

@user
def suggest_message(update, context):
    user_id = update.message.chat.id
    #resend to admin
    try:
        updater.bot.forward_message(variables['telegram']['admin_id'], user_id, update.message.reply_to_message.message_id)
        updater.bot.send_message(user_id, "Звернення принято до уваги")
    except:
        updater.bot.send_message(user_id, "Холера, повідомлення не принято. [?] - /help")


@admin
def send_message_to_all_users(update, context):
    db = sqlcon.Database(database_url=variables['database']['link'])
    users = db.get_users()
    users = [user[0] for user in users]
    db.close()
    res_text = update.message.text.replace('/a_a_usrs','')
    user_count = 0
    for user_id in users:
        user_count += 1
        try:
            updater.bot.send_message(chat_id=user_id, text=res_text, parse_mode='HTML')
            updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text="<pre>Повідомлення надіслано до %i користувачів</pre>" %user_count,
                                     parse_mode='HTML')
        except:
            updater.bot.send_message(chat_id=variables['telegram']['admin_id'],
                                     text="<pre>Користувач під номером %i видалив бота</pre>" % user_count,
                                     parse_mode='HTML')

@admin
def get_stats(update, context):
    stats = """
    Total user count: %i
    Total pics: %i
    """
    db = sqlcon.Database(database_url=variables['database']['link'])
    users = db.get_users()
    pics = db.get_all_pics()
    db.close()

    res_markdown = """Статистика користування ботом:
    
<pre>Унікальних користувачів</pre> - <b>%i</b>
<pre>Зображень у базі данних</pre> - <b>%i</b>""" %(len(users), len(pics))

    updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=res_markdown, parse_mode='HTML')

@admin
def add_pic_to_db(update,context):
    try:
        file_id = update.message.photo[-1].file_id
    except:
        file_id = update.message.reply_to_message.photo[-1].file_id
    file = updater.dispatcher.bot.getFile(file_id)
    file_url = file.file_path

    db = sqlcon.Database(database_url=variables['database']['link'])

    w_size, w_point = imageprocessing.get_coords(file_url)
    db.add_pic(file_url, w_size, w_point)

    db.close()

    get_stats(update, context)

def text_processing(update,context):
    if '/del_p_adm_id_' in update.message.text:
        del_pic_from_db(update, context)
    else:
        sample_res = [
            """
Хочу побажати тобі успіхів, щоб твій ангел-зберігач берег тебе від зла та заздрощів, ворогів і недоброзичливців, підлості і користі. Скінь якусь фотку або зроби реплай на повідомлення з фоткою і вкажи в відповіді <pre>/pic</pre> :^)
            """,
            """
День схожий на дитячу гру-головоломку пазли. Адже полотно дня виткане з маленьких кольорових фрагментів. Можеш скинути якусь гіфку або якщо вже маєш в цьому чаті таку - зроби реплай на повідомлення з gif та вкажи команду <pre>/gif</pre> 8^)
            """,
            """
Не знаю, як ти, але я завжди прокидаюся з відмінним настроєм, тому що розумію, що починається новий день, а значить, що можна встигнути стільки всього зробити за цей час, щоб потім пишатися собою. Можеш надіслати стікер або зробити реплай на повідомлення з стікером і вказати в відповіді <pre>/stc</pre> xD
            """,
            """
Дорогий, шлю тобі смс тонну гарного настрою В-) Не надсилай сюди текст, якщо не розумієш як користуватись, натисни сюди - /help
            """,
            """
Свічка не гасне, зміцнюється надія, Хай радість буде в серці і блаженний мир, нехай Завжди будуть білосніжними одягу, Щоб трубний годину Господь покликав на шлюбний бенкет. Цей бот не опрацьовує текст :-Ь
            """,
            """
Я б хотів зібрати в один букет все квіти світу, щоб кинути їх сьогодні до твоїх ніг. Подякувати Бога можна через <pre>/sug</pre>: зробіть реплай на повідомлення, яке бажаєте преслати.
            """
        ]
        updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text=random.choice(sample_res), parse_mode='HTML')

@admin
def del_pic_from_db(update, context):
    db = sqlcon.Database(variables['telegram']['link'])
    db.delete_pic_by_id(int(update.message.text.replace('/del_p_adm_id_','')))
    db.close()

    updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text="<pre>Зображення видалено.</pre>", parse_mode='HTML')
    get_stats(update, context)


@admin
def get_all_pics_from_db(update, context):
    type_msg = 'text'
    db = sqlcon.Database(database_url=variables['database']['link'])
    res = db.get_all_pics()
    if type_msg == 'text':
        res_markdown=['<pre>Зображення у базі данних</pre>\n']
        res_markdown.extend(["""<a href="%s">[id %i]</a> - /del_p_adm_id_%i """ %(line[1], line[0], line[0]) for line in res])
        db.close()
        counter = 0
        while True:
            try:
                counter+=1
                print(counter)
                updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text='\n'.join(res_markdown[20*counter:20*(counter+1)]), parse_mode='HTML')
            except:
                # updater.bot.send_message(chat_id=variables['telegram']['admin_id'], text='\n'.join(res_markdown[20*counter:]), parse_mode='HTML')
                break
    elif type_msg == 'pic':
        for line in res:
            print(line[0])
            updater.bot.send_photo(chat_id=variables['telegram']['admin_id'], photo=line[1], caption='/del_p_adm_id_%i' %(line[0]), parse_mode='HTML')


if __name__=="__main__":
    job_queue = updater.job_queue
    dp = updater.dispatcher
#user commands
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("help_admin", help_admin))
    dp.add_handler(CommandHandler("start", welcome))
    dp.add_handler(CommandHandler("pic", create_add_from_pic))
    dp.add_handler(CommandHandler("gif", create_add_from_gif))
    dp.add_handler(CommandHandler("stc", create_add_from_sticker))
    dp.add_handler(CommandHandler("sug", suggest_message))
    dp.add_handler(MessageHandler(telegram.ext.filters.Filters.photo, create_add_from_pic))
    dp.add_handler(MessageHandler(telegram.ext.filters.Filters.animation, create_add_from_gif))
    dp.add_handler(MessageHandler(telegram.ext.filters.Filters.sticker, create_add_from_sticker))

#admin commands
    dp.add_handler(CommandHandler("a_a_usrs", send_message_to_all_users))
    dp.add_handler(CommandHandler("ad_p_adm", add_pic_to_db))
    dp.add_handler(CommandHandler("get_a_p_adm", get_all_pics_from_db))
    dp.add_handler(CommandHandler("stat_a_sid_m", get_stats))
    dp.add_handler(MessageHandler(telegram.ext.filters.Filters.text, text_processing))
    """
    /a_a_usrs - розповісти всім юзерам боту анекдот
    /ad_p_adm - додати зображення до бази приколів
    /get_a_p_adm - переглянути базу зображень
    /stat_a_sid_m - статистика користування ботом
    """
    updater.start_webhook(listen="0.0.0.0",
                          port=PORT,
                          url_path=variables['telegram']['token'],
                        webhook_url = 'https://shrouded-beach-91892.herokuapp.com/' + variables['telegram']['token'])
    updater.idle()

