import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, CallbackContext
import sqlite3
from config import BOT_TOKEN
from database import conn, c
conn = sqlite3.connect('user_data.db')
c = conn.cursor()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LANGUAGE, START_APP, FULL_NAME, AGE, ADDRESS, PROFICIENCY, PHONE_NUMBER, BIRTHDATE, GENDER, STUDENT_STATUS, EDUCATION, MARITAL_STATUS, WORK_HISTORY, LANGUAGE_SKILLS, AUDIO_INTRODUCTION, POSITIVE_SKILLS, PLATFORM_EXPERIENCE, PLATFORM_DETAILS, SOFTWARE_EXPERIENCE, PHOTO_UPLOAD, SOURCE_INFO, DATA_PROCESSING_CONSENT, CONFIRM = range(23)


translations = {
    'start': {
        'uz': "In Hunter - ish bilan bog'liq agentlik va boshqalar\n\nSalom! Botimizga xush kelibsiz!",
        'ru': "In Hunter - рекрутинговое агентство и т.д.\n\nЗдравствуйте! Добро пожаловать в наш бот!",
    },
    'full_name': {
        'uz': 'Ism, sharifingizni kiriting',
        'ru': 'Введите Ф.И.О',
    },
     'age': {
        'uz': 'Yoshingizni kiriting',
        'ru': 'Введите свой возраст',
    },
    'proficiency': {
        'uz': "Boshlang'ich, o'rta, ilg'or",
        'ru': 'Начинающий, средний, продвинутый',
    },
    'phone_number': {
        'uz': 'Telefon raqamingizni kiriting',
        'ru': 'Введите свой номер телефона',
    },
    'birthdate': {
        'uz': 'Tugʻilgan kuningiz sanasi',
        'ru': 'Дата вашего рождения',
    },
    'address': {
        'uz': 'Yashash manzilingiz',
        'ru': 'Место проживания',
    },
    'gender': {
        'uz': 'Jinsingiz',
        'ru': 'Пол',
    },
    'student_status': {
        'uz': 'Siz talaba bo‘lmoqchimisiz? Ha / Yo‘q',
        'ru': 'Являетесь ли вы студентом? Да / Нет',
    },
    'education': {
        'uz': 'Maʼlumot? Universitet nomi, fakulteti?',
        'ru': 'Образование? Наименование университета, факультет?',
    },
    'marital_status': {
        'uz': 'Oilaviy holat? Uylanmoqda, ayollangan, bo‘shanib ketgan, xotin',
        'ru': 'Семейное положение? Замужем, женат, в разводе, вдова',
    },
    'work_history': {
        'uz': 'So‘nggi ish joylar (oxirgi 3 ish joyingizni yozing)',
        'ru': 'Последние места работы (распишите последние 3 места работы)',
    },
    'language_skills': {
        'uz': 'Til bilimi?',
        'ru': 'Знание языков?',
    },
    'audio_introduction': {
        'uz': 'O‘zingiz haqingizda tinglangan maʼlumot',
        'ru': 'Расскажите о себе через аудиозапись',
    },
    'positive_skills': {
        'uz': 'Sizning qo‘llab-quvvatlovchiniy ko‘nikmalariz',
        'ru': 'Напишите свои положительные навыки',
    },
    'platform_experience': {
        'uz': 'Qaysi platformalarda ishlagansiz?',
        'ru': 'В каких платформах работали?',
    },
    'platform_details': {
        'uz': 'Iltimos, tafsilotli tarzda yozing (Excel, Word, Canva)',
        'ru': 'Распишите пожалуйста детально (Excel, Word, Canva)',
    },
    'software_experience': {
        'uz': 'Qaysi dasturlarda ishlagansiz? (1C, MySQL, SAP)',
        'ru': 'В каких программах работали? (1C, MySQL, SAP)',
    },
    'photo_upload': {
        'uz': 'Iltimos, o‘zingizning rasmingizni yuboring',
        'ru': 'Отправьте пожалуйста свою фотографию',
    },
    'source_info': {
        'uz': 'Botimiz haqida qayerdan bilib oldingiz?',
        'ru': 'Откуда узнали про наш Бот?',
    },
    'data_processing_consent': {
        'uz': 'Shaxsiy maʼlumotlaringizni ishlashga ruxsat berasizmi? (Ha / Yo‘q)',
        'ru': 'Даёте ли вы разрешение на обработку личных данных? (Да / Нет)',
    },
    'confirm': {
        'uz': 'Iltimos, barchasini to‘g‘ri to‘ldirganingizni tekshiring? (Ha / Yo‘q)',
        'ru': 'Проверьте пожалуйста, правильно ли вы всё заполнили? (Да / Нет)',
    },
    'thanks': {
        'uz': "Rahmat! Sizning ma'lumotlaringiz muvaffaqiyatli saqlandi.",
        'ru': "Спасибо! Ваша информация успешно сохранена.",
    },
    'cancelled': {
        'uz': "Bekor qilindi.",
        'ru': "Отменено.",
    }
}

async def start(update: Update, context):
    await update.message.reply_text(
        "Please choose your language / Пожалуйста, выберите ваш язык",
        reply_markup=ReplyKeyboardMarkup([["Uzbek", "Russian"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return LANGUAGE

async def set_language(update: Update, context):
    logger.info("Inside set_language handler")
    user_choice = update.message.text
    if user_choice.lower() in ['uzbek', 'russian']:
        context.user_data['language'] = 'uz' if user_choice.lower() == 'uzbek' else 'ru'
        await update.message.reply_text(
            translations['start'][context.user_data['language']],
            reply_markup=ReplyKeyboardMarkup([["Start ✍️"]], resize_keyboard=True, one_time_keyboard=True)
        )
        return START_APP
    else:
        return await start(update, context)


async def start_application(update: Update, context: CallbackContext):
    logger.info("Inside start_application handler")
    lang = context.user_data['language']
    await update.message.reply_text(
        translations['full_name'][lang],
        reply_markup=ReplyKeyboardRemove()
    )
    return FULL_NAME


async def full_name(update: Update, context):
    logger.info("Inside full_name handler")
    print("Inside full_name function")
    context.user_data['full_name'] = update.message.text
    lang = context.user_data.get('language')
    
    await update.message.reply_text(
        translations['age'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return AGE



async def age(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()
    
    if text == 'back 👈':
        return await start_application(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    try:
        age = int(update.message.text)
        if age <= 0 or age >= 150:
            raise ValueError
        context.user_data['age'] = age
        await update.message.reply_text(
            translations['address'][lang],
            reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
        )
        return ADDRESS
    except ValueError:
        await update.message.reply_text(
            translations['age'][lang],
            reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
        )
        return AGE

async def address(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()
    
    if text == 'back 👈':
        return await age(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['address'] = update.message.text
    await update.message.reply_text(
        translations['proficiency'][lang],
        reply_markup=ReplyKeyboardMarkup([['Beginner', 'Intermediate', 'Advanced'], ['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return PROFICIENCY

async def proficiency(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()
    
    if text == 'back 👈':
        return await address(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['proficiency'] = update.message.text
    await update.message.reply_text(
        translations['phone_number'][lang],
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton('Share Contact', request_contact=True)], ['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return PHONE_NUMBER

async def phone_number(update: Update, context):
    lang = context.user_data['language']
    if update.message.contact:
        context.user_data['phone_number'] = update.message.contact.phone_number
    else:
        text = update.message.text.lower()
        if text == 'cancel ❌':
            return await cancel(update, context)
        elif text == 'back 👈':
            return await proficiency(update, context)
        else:
            context.user_data['phone_number'] = update.message.text

    await update.message.reply_text(
        translations['birthdate'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return BIRTHDATE


async def birthdate(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await phone_number(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['birthdate'] = update.message.text
    await update.message.reply_text(
        translations['gender'][lang],
        reply_markup=ReplyKeyboardMarkup([['Male', 'Female'], ['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return GENDER

async def gender(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await birthdate(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['gender'] = update.message.text
    await update.message.reply_text(
        translations['student_status'][lang],
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No'], ['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return STUDENT_STATUS

async def student_status(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await gender(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['student_status'] = update.message.text
    await update.message.reply_text(
        translations['education'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return EDUCATION

async def education(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await student_status(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['education'] = update.message.text
    await update.message.reply_text(
        translations['marital_status'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return MARITAL_STATUS

async def marital_status(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await education(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['marital_status'] = update.message.text
    await update.message.reply_text(
        translations['work_history'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return WORK_HISTORY

async def work_history(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await marital_status(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['work_history'] = update.message.text
    await update.message.reply_text(
        translations['language_skills'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return LANGUAGE_SKILLS

async def language_skills(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await work_history(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['language_skills'] = update.message.text
    await update.message.reply_text(
        translations['audio_introduction'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return AUDIO_INTRODUCTION

async def audio_introduction(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await language_skills(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['audio_introduction'] = update.message.text
    await update.message.reply_text(
        translations['positive_skills'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return POSITIVE_SKILLS

async def positive_skills(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await audio_introduction(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['positive_skills'] = update.message.text
    await update.message.reply_text(
        translations['platform_experience'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return PLATFORM_EXPERIENCE

async def platform_experience(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await positive_skills(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['platform_experience'] = update.message.text
    await update.message.reply_text(
        translations['platform_details'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return PLATFORM_DETAILS

async def platform_details(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await platform_experience(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['platform_details'] = update.message.text
    await update.message.reply_text(
        translations['software_experience'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return SOFTWARE_EXPERIENCE

async def software_experience(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await platform_details(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['software_experience'] = update.message.text
    await update.message.reply_text(
        translations['photo_upload'][lang],
        reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return PHOTO_UPLOAD

async def photo_upload(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await software_experience(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        new_file = context.bot.get_file(file_id)
        
        photo_path = f'photos/{file_id}.jpg' 
        new_file.download(photo_path)
        context.user_data['photo_upload'] = photo_path  #

        await update.message.reply_text(
            translations['source_info'][lang],
            reply_markup=ReplyKeyboardMarkup([['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
        )
        return SOURCE_INFO  
    else:
        await update.message.reply_text(
            "Please upload a photo. You can send it again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return PHOTO_UPLOAD  


async def source_info(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await photo_upload(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['source_info'] = update.message.text
    await update.message.reply_text(
        translations['data_processing_consent'][lang],
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No'], ['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return DATA_PROCESSING_CONSENT

async def data_processing_consent(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await source_info(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)

    context.user_data['data_processing_consent'] = update.message.text
    await update.message.reply_text(
        translations['confirm'][lang],
        reply_markup=ReplyKeyboardMarkup([['Yes', 'No'], ['Back 👈', 'Cancel ❌']], resize_keyboard=True, one_time_keyboard=True)
    )
    return CONFIRM

async def confirm(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == 'back 👈':
        return await data_processing_consent(update, context)
    elif text == 'cancel ❌':
        return await cancel(update, context)
    elif text == 'yes':
        user_data = context.user_data
        
        photo_path = user_data.get('photo_upload', None) 

        c.execute('''
            INSERT INTO users (full_name, age, address, proficiency, phone_number, birthdate, gender, student_status, education, marital_status, work_history, language_skills, audio_introduction, positive_skills, platform_experience, platform_details, software_experience, photo_upload, source_info, data_processing_consent, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['full_name'], user_data['age'], user_data['address'], user_data['proficiency'], user_data['phone_number'], user_data['birthdate'],
            user_data['gender'], user_data['student_status'], user_data['education'], user_data['marital_status'], user_data['work_history'], 
            user_data['language_skills'], user_data['audio_introduction'], user_data['positive_skills'], user_data['platform_experience'], 
            user_data['platform_details'], user_data['software_experience'], photo_path, user_data['source_info'], user_data['data_processing_consent'], 1
        ))
        conn.commit()
        await update.message.reply_text(translations['thanks'][lang])
    else:
        await update.message.reply_text(translations['cancelled'][lang])

    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    await update.message.reply_text(
        translations['cancelled'][lang],
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, set_language)],
            START_APP: [MessageHandler(filters.TEXT & ~filters.COMMAND, start_application)],
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, age)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            PROFICIENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, proficiency)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number)],
            BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthdate)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            STUDENT_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_status)],
            EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, education)],
            MARITAL_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, marital_status)],
            WORK_HISTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, work_history)],
            LANGUAGE_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_skills)],
            AUDIO_INTRODUCTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, audio_introduction)],
            POSITIVE_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, positive_skills)],
            PLATFORM_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, platform_experience)],
            PLATFORM_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, platform_details)],
            SOFTWARE_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, software_experience)],
            PHOTO_UPLOAD: [MessageHandler(filters.TEXT & ~filters.COMMAND, photo_upload)],
            SOURCE_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, source_info)],
            DATA_PROCESSING_CONSENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, data_processing_consent)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirm)],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    application.add_handler(conversation_handler)
    application.run_polling()

if __name__ == '__main__':
    main()
