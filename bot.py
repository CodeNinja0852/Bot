import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters, \
    CallbackContext
import sqlite3
from telegram.constants import ParseMode
from config import BOT_TOKEN
from database import conn, c
import os

def setup_database():
    with sqlite3.connect('user_data.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                address TEXT NOT NULL,
                phone_number TEXT NOT NULL,
                birthdate TEXT NOT NULL,
                gender TEXT NOT NULL,
                student_status TEXT NOT NULL,
                education TEXT NOT NULL,
                marital_status TEXT NOT NULL,
                work_history TEXT NOT NULL,
                language_skills TEXT NOT NULL,
                audio_introduction TEXT NOT NULL,
                positive_skills TEXT NOT NULL,
                platform_experience TEXT NOT NULL,
                platform_details TEXT NOT NULL,
                software_experience TEXT NOT NULL,
                photo_upload TEXT,  
                source_info TEXT NOT NULL,
                data_processing_consent TEXT NOT NULL,
                completed INTEGER DEFAULT 0
            )
        ''')
        conn.commit()

setup_database()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

LANGUAGE, START_APP,  FULL_NAME, PHONE_NUMBER, BIRTHDATE, ADDRESS, GENDER, STUDENT_STATUS, EDUCATION, MARITAL_STATUS, WORK_HISTORY, LANGUAGE_SKILLS, AUDIO_INTRODUCTION, POSITIVE_SKILLS, PLATFORM_EXPERIENCE, PLATFORM_DETAILS, SOFTWARE_EXPERIENCE, PHOTO_UPLOAD, SOURCE_INFO, DATA_PROCESSING_CONSENT, CONFIRM = range(21)

translations = {
    'start': {
        'uz': "In Hunter - ish bilan bog'liq agentlik \n\nSalom! Botimizga xush kelibsiz! 👋",
        'ru': "In Hunter - рекрутинговое агентство.\n\nЗдравствуйте! Добро пожаловать в наш бот! 👋",
    },
    'full_name': {
        'uz': '👤 Ism va Familiyangizni yozing:',
        'ru': '👤 Напишите Ф.И.О:',
    },
     'phone_number': {
        'uz': '📞 Telefon raqamingizni kiriting:',
        'ru': '📞 Введите свой номер телефона:',
    },
    'birthdate': {
        'uz': "📆 Tug'ilgan kuningiz:",
        'ru': '📆 Дата вашего рождения:',
    },
    'address': {
        'uz': '🏘 Yashash manzilingiz:',
        'ru': '🏘 Место проживания:',
    },
    'gender': {
        'uz': '🧑👩 Jinsingizni tanlang:',
        'ru': '🧑👩 Выберите свой пол:',
    },
    'student_status': {
        'uz': '🧑‍🎓 Siz talabasizmi? Ha / Yo‘q',
        'ru': '🧑‍🎓 Являетесь ли вы студентом? Да / Нет',
    },
    'education': {
        'uz': '🏫 Maʼlumot? Universitet nomi, fakulteti?',
        'ru': '🏫 Образование? Наименование университета, факультет?',
    },
    'marital_status': {
        'uz': '👨‍👩‍👧‍👦 Oilaviy ahvolingiz:',
        'ru': '‍👩‍👧‍👦 Ваше семейное положение:',
    },
    'work_history': {
        'uz': 'So‘nggi ish joylar (oxirgi 3 ish joyingizni yozing) 👇',
        'ru': 'Последние места работы (распишите последние 3 места работы) 👇',
    },
    'language_skills': {
        'uz': '🇷🇺🇺🇿🇺🇸 Til bilimi:',
        'ru': '🇷🇺🇺🇿🇺🇸 Знание языков:',
    },
    'audio_introduction': {
        'uz': "🗣 Audio yozuv orqali o'zingiz haqingizda gapiring",
        'ru': '🗣 Расскажите о себе через аудиозапись',
    },
    'positive_skills': {
        'uz': "📖 Ijobiy ko'nikmalaringizni yozing",
        'ru': '📖 Напишите свои положительные навыки',
    },
    'platform_experience': {
        'uz': '🧑‍💻 Qaysi platformalarda ishlagansiz?',
        'ru': '🧑‍💻 В каких платформах работали?',
    },
    'platform_details': {
        'uz': '🔍📍 Iltimos, batafsil yozing (excel, word, canva):',
        'ru': '🔍📍 Распишите пожалуйста детально (Excel, Word, Canva):',
    },
    'software_experience': {
        'uz': '🧑‍💻 Qaysi dasturlarda ishlagansiz? (1C, MySQL, SAP)',
        'ru': '🧑‍💻 каких программах работали? (1C, MySQL, SAP)',
    },
    'photo_upload': {
        'uz': 'Iltimos, o‘zingizning rasmingizni yuboring 🖼',
        'ru': 'Отправьте пожалуйста свою фотографию 🖼',
    },
    'source_info': {
        'uz': 'Botimiz haqida qayerdan bilib oldingiz? 🤖',
        'ru': 'Откуда узнали про наш Бот? 🤖',
    },
    'data_processing_consent': {
        'uz': "Shaxsiy ma'lumotlarni qayta ishlashga ruxsat berasizmi? (Ha 👍 / Yo‘q 👎)",
        'ru': 'Даёте ли вы разрешение на обработку личных данных? (Да 👍/ Нет 👎)',
    },
    'confirm': {
        'uz': 'Iltimos, barchasini to‘g‘ri to‘ldirganingizni tekshiring? (Ha 👍/ Yo‘q 👎)',
        'ru': 'Проверьте пожалуйста, правильно ли вы всё заполнили? (Да 👍 / Нет 👎)',
    },
    'thanks': {
        'uz': "Rahmat! Sizning ma'lumotlaringiz muvaffaqiyatli saqlandi. ☺️",
        'ru': "Спасибо! Ваша информация успешно сохранена ☺️ .",
    },
    'cancelled': {
        'uz': "Bekor qilindi. ❌",
        'ru': "Отменено. ❌",
    }
}

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Iltimos tilni tanlang / Пожалуйста, выберите ваш язык 👇",
        reply_markup=ReplyKeyboardMarkup([["🇺🇿 O'zbek", "🇷🇺 Русский"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return LANGUAGE

async def set_language(update: Update, context: CallbackContext):
    user_choice = update.message.text
    if "o'zbek" in user_choice.lower():
        context.user_data['language'] = 'uz'
        message = "Anketa to'ldirish"
    elif 'русский' in user_choice.lower():
        context.user_data['language'] = 'ru'
        message = "Заполнение анкеты"
    else:
        return await start(update, context)

    await update.message.reply_text(
        message,
        reply_markup=ReplyKeyboardMarkup([[message + " ✍️"]], resize_keyboard=True, one_time_keyboard=True)
    )
    return START_APP


async def start_application(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    await update.message.reply_text(
        translations['full_name'][lang],
        reply_markup=ReplyKeyboardRemove()
    )
    return FULL_NAME


async def full_name(update: Update, context: CallbackContext):
    logger.info("Inside full_name handler")
    context.user_data['full_name'] = update.message.text
    context.user_data['last_state'] = FULL_NAME
    lang = context.user_data.get('language', 'ru')
    back_button = 'Назад 👈' if lang == 'ru' else 'Orqaga 👈'
    cancel_button = 'Отмена ❌' if lang == 'ru' else 'Bekor qilish ❌'
    await update.message.reply_text(
        translations['phone_number'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button, cancel_button]], resize_keyboard=True, one_time_keyboard=True)
    )
    return PHONE_NUMBER


def back_button(lang):
    return 'Назад 👈' if lang == 'ru' else 'Orqaga 👈'


def cancel_button(lang):
    return 'Отмена ❌' if lang == 'ru' else 'Bekor qilish ❌'


def questions(lang):
    return 'Botimiz haqida qayerdan bilib oldingiz? 🤖' if lang == 'uz' else 'Откуда узнали про наш Бот? 🤖'



async def phone_number(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    context.user_data['last_state'] = PHONE_NUMBER
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)
    else:
        context.user_data['phone_number'] = text
    await update.message.reply_text(
        translations['birthdate'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return BIRTHDATE


async def birthdate(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    context.user_data['last_state'] = BIRTHDATE
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['birthdate'] = update.message.text
    
    # Assuming translations['address'][lang] is the prompt for address
    await update.message.reply_text(
        translations['address'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return ADDRESS


async def address(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    context.user_data['last_state'] = ADDRESS
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['address'] = update.message.text
    
    gender_options = ['Мужчина', 'Женщина'] if lang == 'ru' else ['Erkak', 'Ayol']

    await update.message.reply_text(
        translations['gender'][lang],
        reply_markup=ReplyKeyboardMarkup([gender_options, [back_button(lang), cancel_button(lang)]],
                                         resize_keyboard=True, one_time_keyboard=True)
    )
    return GENDER


async def gender(update: Update, context):
    lang = context.user_data['language']
    text = update.message.text.lower()
    if text == back_button(lang).lower():
        return await start_application(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)
    context.user_data['gender'] = update.message.text
    gender_options = ['Мужчина', 'Женщина'] if lang == 'ru' else ['Erkak', 'Ayol']
    if text.lower() not in [option.lower() for option in gender_options]:
        await update.message.reply_text(
            translations['gender'][lang],
            reply_markup=ReplyKeyboardMarkup(
                [gender_options, [back_button(lang), cancel_button(lang)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return GENDER
    yes_or_no = ['Да', 'Нет'] if lang == 'ru' else ['Ha', 'Yoʻq']
    await update.message.reply_text(
        translations['student_status'][lang],
        reply_markup=ReplyKeyboardMarkup(
            [yes_or_no, [back_button(lang), cancel_button(lang)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )
    return STUDENT_STATUS



async def student_status(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = STUDENT_STATUS
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    yes_or_no = ['Да', 'Нет'] if lang == 'ru' else ['Ha', 'Yoʻq']
    
    if text.lower() not in [option.lower() for option in yes_or_no]:
        await update.message.reply_text(
            translations['student_status'][lang],
            reply_markup=ReplyKeyboardMarkup(
                [[option] for option in yes_or_no] + [[back_button(lang), cancel_button(lang)]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
        )
        return STUDENT_STATUS

    await update.message.reply_text(
        translations['education'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return EDUCATION


async def education(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = EDUCATION
    context.user_data['education'] = update.message.text
    await update.message.reply_text(
         translations['work_history'][lang],
         reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                             one_time_keyboard=True)
        )
    return MARITAL_STATUS


async def marital_status(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = MARITAL_STATUS
    
    if lang == 'ru':
        BUTTON1 = "Замужем"
        BUTTON2 = "Женат"
        BUTTON3 = "В разводе"
        BUTTON4 = "Вдова"
    elif lang == 'uz':
        BUTTON1 = "Uylangan"
        BUTTON2 = "Turmush qurgan"
        BUTTON3 = "Ajrashgan"
        BUTTON4 = "Beva"
    else:
        raise ValueError("Unsupported language")
    
    if update.message.text.lower() in [BUTTON1.lower(), BUTTON2.lower(), BUTTON3.lower(), BUTTON4.lower()]:
        context.user_data['marital_status'] = update.message.text
        await update.message.reply_text(
            translations['work_history'][lang],
            reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                             one_time_keyboard=True)
        )
        return MARITAL_STATUS
    
    await update.message.reply_text(
        translations['marital_status'][lang],
        reply_markup=ReplyKeyboardMarkup([[BUTTON1, BUTTON2], [BUTTON3, BUTTON4]], resize_keyboard=True, one_time_keyboard=True)
    )
    return WORK_HISTORY

async def work_history(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = WORK_HISTORY
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['work_history'] = update.message.text
    await update.message.reply_text(
        translations['language_skills'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return LANGUAGE_SKILLS


async def language_skills(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = LANGUAGE_SKILLS
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['language_skills'] = update.message.text
    await update.message.reply_text(
        translations['audio_introduction'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return AUDIO_INTRODUCTION


async def audio_introduction(update: Update, context: CallbackContext):
    lang = context.user_data.get('language', 'en')
    context.user_data['last_state'] = AUDIO_INTRODUCTION
    text = update.message.text.lower() if update.message.text else ''

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    if update.message.voice:
        voice_file_id = update.message.voice.file_id
        try:
            voice = await context.bot.get_file(voice_file_id)
            voice_file_path = os.path.join('audio', f'{voice_file_id}.ogg')
            os.makedirs('audio', exist_ok=True)
            await voice.download_to_drive(voice_file_path)
            context.user_data['audio_introduction'] = voice_file_path

            await update.message.reply_text(
                translations['positive_skills'][lang],
                reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                                 one_time_keyboard=True)
            )
            return POSITIVE_SKILLS

        except Exception as e:
            await update.message.reply_text(f"Failed to process the audio: {e}")
            return AUDIO_INTRODUCTION

    else:
        await update.message.reply_text(
            "Please record an audio introduction. You can send it again.",
            reply_markup=ReplyKeyboardRemove()
        )
        return AUDIO_INTRODUCTION


async def positive_skills(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = POSITIVE_SKILLS
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['positive_skills'] = update.message.text
    await update.message.reply_text(
        translations['platform_experience'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return PLATFORM_EXPERIENCE


async def platform_experience(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = PLATFORM_EXPERIENCE
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['platform_experience'] = update.message.text
    await update.message.reply_text(
        translations['platform_details'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return PLATFORM_DETAILS


async def platform_details(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = PLATFORM_DETAILS
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['platform_details'] = update.message.text
    await update.message.reply_text(
        translations['software_experience'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return SOFTWARE_EXPERIENCE


async def software_experience(update: Update, context):
    lang = context.user_data['language']
    context.user_data['last_state'] = SOFTWARE_EXPERIENCE
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['software_experience'] = update.message.text
    await update.message.reply_text(
        translations['photo_upload'][lang],
        reply_markup=ReplyKeyboardMarkup([[back_button(lang), cancel_button(lang)]], resize_keyboard=True,
                                         one_time_keyboard=True)
    )
    return PHOTO_UPLOAD


async def photo_upload(update: Update, context: CallbackContext):
    logger.info("Inside the photo_upload function")
    context.user_data['last_state'] = PHOTO_UPLOAD
    lang = context.user_data.get('language', 'en')
    text = update.message.text.lower()
    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
        try:
            file = await context.bot.get_file(file_id)
            file_path = os.path.join('photos', f'{file_id}.jpg')
            os.makedirs('photos', exist_ok=True)
            await file.download_to_drive(file_path)
            context.user_data['photo_path'] = file_path
            logger.info("Downloading the image user sent")
            logger.info("Going to the next step...")
            await update.message.reply_text(
                text='Botimiz haqida qayerdan bilib oldingiz? 🤖' if lang == 'uz' else 'Откуда узнали про наш Бот? 🤖'

            )
            return SOURCE_INFO

        except Exception as e:
            logger.error("Error occurred restarting...")
            logger.error(e)
            pass
            return PHOTO_UPLOAD

    else:
        pass
    return SOURCE_INFO


async def source_info(update: Update, context):
    logger.info("Inside source info function")
    context.user_data['last_state'] = SOURCE_INFO
    lang = context.user_data['language']
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['source_info'] = update.message.text
    yes_or_no = ['Да', 'Нет'] if lang == 'ru' else ['Yes', 'No']

    keyboard = [
        yes_or_no,
        [back_button(lang), cancel_button(lang)]
    ]

    await update.message.reply_text(
        translations['data_processing_consent'][lang],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return DATA_PROCESSING_CONSENT


async def data_processing_consent(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    context.user_data['last_state'] = DATA_PROCESSING_CONSENT
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)

    context.user_data['data_processing_consent'] = update.message.text
    yes_or_no = ['Да', 'Нет'] if lang == 'ru' else ['Yes', 'No']

    keyboard = [
        yes_or_no,
        [back_button(lang), cancel_button(lang)]
    ]

    await update.message.reply_text(
        translations['confirm'][lang],
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return CONFIRM


async def confirm(update: Update, context: CallbackContext):
    lang = context.user_data['language']
    context.user_data['last_state'] = CONFIRM
    text = update.message.text.lower()

    if text == back_button(lang).lower():
        return await back(update, context)
    elif text == cancel_button(lang).lower():
        return await cancel(update, context)
    elif text == 'yes':
        user_data = context.user_data
        photo_path = user_data.get('photo_path', None)

        c.execute('''
            INSERT INTO user_data (full_name, address, phone_number, birthdate, gender, student_status, education, marital_status, work_history, language_skills, audio_introduction, positive_skills, platform_experience, platform_details, software_experience, photo_upload, source_info, data_processing_consent, completed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['full_name'], user_data['address'], user_data['phone_number'], user_data['birthdate'],
            user_data['gender'], user_data['student_status'], user_data['education'], user_data['marital_status'],
            user_data['work_history'], user_data['language_skills'], user_data['audio_introduction'],
            user_data['positive_skills'], user_data['platform_experience'], user_data['platform_details'],
            user_data['software_experience'], photo_path, user_data['source_info'],
            user_data['data_processing_consent'], 1
        ))
        conn.commit()
        await update.message.reply_text(translations['thanks'][lang])
    else:
        await update.message.reply_text(translations['cancelled'][lang])

    return ConversationHandler.END

async def back(update: Update, context):
    current_state = context.user_data.get('last_state', None)
    previous_state = {
        PHONE_NUMBER: FULL_NAME,
        BIRTHDATE: PHONE_NUMBER,
        ADDRESS: BIRTHDATE,
        GENDER: ADDRESS,
        STUDENT_STATUS: GENDER,
        EDUCATION: STUDENT_STATUS,
        MARITAL_STATUS: EDUCATION,
        WORK_HISTORY: MARITAL_STATUS,
        LANGUAGE_SKILLS: WORK_HISTORY,
        AUDIO_INTRODUCTION: LANGUAGE,
        POSITIVE_SKILLS: AUDIO_INTRODUCTION,
        PLATFORM_EXPERIENCE: POSITIVE_SKILLS,
        PLATFORM_DETAILS: PLATFORM_EXPERIENCE,
        SOFTWARE_EXPERIENCE: PLATFORM_DETAILS,
        PHOTO_UPLOAD: SOFTWARE_EXPERIENCE,
        SOURCE_INFO: PHOTO_UPLOAD,
        DATA_PROCESSING_CONSENT: SOURCE_INFO
    }.get(current_state)

    context.user_data['last_state'] = previous_state
    if previous_state == FULL_NAME:
        return await start_application(update, context)
    elif previous_state == PHONE_NUMBER:
        return await full_name(update, context)
    elif previous_state == BIRTHDATE:
        return await phone_number(update, context)
    elif previous_state == ADDRESS:
        return await birthdate(update, context)
    elif previous_state == GENDER:
        return await address(update, context)
    elif previous_state == STUDENT_STATUS:
        return await gender(update, context)
    elif previous_state == EDUCATION:
        return await student_status(update, context)
    elif previous_state == MARITAL_STATUS:
        return await education(update, context)
    elif previous_state == WORK_HISTORY:
        return await marital_status(update, context)
    elif previous_state == LANGUAGE_SKILLS:
        return await work_history(update, context)
    elif previous_state == AUDIO_INTRODUCTION:
        return await language_skills(update, context)
    elif previous_state == POSITIVE_SKILLS:
        return await audio_introduction(update, context)
    elif previous_state == PLATFORM_EXPERIENCE:
        return await positive_skills(update, context)
    elif previous_state == PLATFORM_DETAILS:
        return await platform_experience(update, context)
    elif previous_state == SOFTWARE_EXPERIENCE:
        return await platform_experience(update, context)
    elif previous_state == PHOTO_UPLOAD:
        return await software_experience(update, context)
    elif previous_state == SOURCE_INFO:
        return await photo_upload(update, context)
    elif previous_state == DATA_PROCESSING_CONSENT:
        return await source_info(update, context)
    else:
        pass
    


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
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone_number)],
            BIRTHDATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birthdate)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            STUDENT_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, student_status)],
            EDUCATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, education)],
            MARITAL_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, marital_status)],
            WORK_HISTORY: [MessageHandler(filters.TEXT & ~filters.COMMAND, work_history)],
            LANGUAGE_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, language_skills)],
            AUDIO_INTRODUCTION: [MessageHandler(filters.VOICE & ~filters.COMMAND, audio_introduction)],
            POSITIVE_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, positive_skills)],
            PLATFORM_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, platform_experience)],
            PLATFORM_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, platform_details)],
            SOFTWARE_EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, software_experience)],
            PHOTO_UPLOAD: [MessageHandler(filters.PHOTO & ~filters.COMMAND, photo_upload)],
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
