import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackContext
)
from config import Config
from extensions import app, db
from models import Сотрудник, Документ, ПрочтениеДокумента, Отдел
from datetime import datetime
from PIL import Image
from pyzbar.pyzbar import decode
import io
import traceback
from sqlalchemy import text

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Состояния разговора для регистрации
ТАБЕЛЬНЫЙ_НОМЕР, ПОДРАЗДЕЛЕНИЕ, ТЕЛЕФОН = range(3)

def check_database_connection():
    """Проверка подключения к базе данных"""
    try:
        with app.app_context():
            # Пробуем выполнить простой запрос
            db.session.execute(text('SELECT 1'))
            return True
    except Exception as e:
        logger.error(f"Ошибка подключения к базе данных: {e}")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    try:
        user = update.effective_user
        logger.info(f"Пользователь {user.id} запустил команду /start")
        
        # Проверяем подключение к базе данных
        if not check_database_connection():
            await update.message.reply_text(
                "Извините, но сейчас есть проблемы с подключением к базе данных. "
                "Пожалуйста, попробуйте позже."
            )
            return ConversationHandler.END
        
        with app.app_context():
            сотрудник = Сотрудник.query.filter_by(telegram_id=user.id).first()
            logger.info(f"Результат поиска сотрудника: {сотрудник}")
            
            if not сотрудник:
                await update.message.reply_text(
                    "Здравствуйте! Для начала работы необходимо зарегистрироваться.\n"
                    "Пожалуйста, введите ваш табельный номер:"
                )
                return ТАБЕЛЬНЫЙ_НОМЕР
            
            if not сотрудник.статус_регистрации:
                await update.message.reply_text(
                    "Для завершения регистрации необходимо указать дополнительную информацию.\n"
                    "Пожалуйста, введите ваш табельный номер:"
                )
                return ТАБЕЛЬНЫЙ_НОМЕР
            
            await update.message.reply_text(
                f"Здравствуйте, {сотрудник.полное_имя}!\n"
                "Отправьте мне QR-код документа для подтверждения ознакомления."
            )
            return ConversationHandler.END
    except Exception as e:
        error_text = f"Ошибка в команде start: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_text)
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. "
            "Мы записали информацию об ошибке и скоро её исправим. "
            "Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

async def register_employee_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка табельного номера"""
    try:
        табельный_номер = update.message.text.strip()
        logger.info(f"Получен табельный номер: {табельный_номер}")
        
        with app.app_context():
            # Поиск сотрудника по табельному номеру
            сотрудник = Сотрудник.query.filter_by(табельный_номер=табельный_номер).first()
            
            if not сотрудник:
                await update.message.reply_text(
                    "Сотрудник с таким табельным номером не найден.\n"
                    "Пожалуйста, проверьте номер и попробуйте снова:"
                )
                return ТАБЕЛЬНЫЙ_НОМЕР
            
            context.user_data['employee_id'] = сотрудник.id
            
            # Получаем список всех отделов
            отделы = Отдел.query.all()
            keyboard = [[отдел.название] for отдел in отделы]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
            
            await update.message.reply_text(
                "Выберите ваше структурное подразделение:",
                reply_markup=reply_markup
            )
            return ПОДРАЗДЕЛЕНИЕ
    except Exception as e:
        error_text = f"Ошибка при обработке табельного номера: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_text)
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. "
            "Мы записали информацию об ошибке и скоро её исправим. "
            "Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

async def register_department(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка выбора подразделения"""
    try:
        название_отдела = update.message.text
        logger.info(f"Выбрано подразделение: {название_отдела}")
        
        with app.app_context():
            отдел = Отдел.query.filter_by(название=название_отдела).first()
            
            if not отдел:
                await update.message.reply_text(
                    "Подразделение не найдено. Пожалуйста, выберите из списка:"
                )
                return ПОДРАЗДЕЛЕНИЕ
            
            сотрудник = Сотрудник.query.get(context.user_data['employee_id'])
            сотрудник.отдел_id = отдел.id
            db.session.commit()
            
            await update.message.reply_text(
                "Введите ваш рабочий телефон:",
                reply_markup=ReplyKeyboardRemove()
            )
            return ТЕЛЕФОН
    except Exception as e:
        error_text = f"Ошибка при выборе подразделения: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_text)
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. "
            "Мы записали информацию об ошибке и скоро её исправим. "
            "Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

async def register_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка ввода телефона"""
    try:
        телефон = update.message.text.strip()
        logger.info(f"Получен телефон: {телефон}")
        
        with app.app_context():
            сотрудник = Сотрудник.query.get(context.user_data['employee_id'])
            
            сотрудник.рабочий_телефон = телефон
            сотрудник.telegram_id = update.effective_user.id
            сотрудник.статус_регистрации = True
            db.session.commit()
            
            await update.message.reply_text(
                f"Регистрация завершена!\n\n"
                f"Ваши данные:\n"
                f"ФИО: {сотрудник.полное_имя}\n"
                f"Подразделение: {сотрудник.отдел.название}\n"
                f"Табельный номер: {сотрудник.табельный_номер}\n"
                f"Рабочий телефон: {сотрудник.рабочий_телефон}\n\n"
                f"Теперь вы можете отправлять мне QR-коды документов для подтверждения ознакомления."
            )
            return ConversationHandler.END
    except Exception as e:
        error_text = f"Ошибка при сохранении телефона: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_text)
        await update.message.reply_text(
            "Произошла ошибка при обработке команды. "
            "Мы записали информацию об ошибке и скоро её исправим. "
            "Пожалуйста, попробуйте позже."
        )
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена регистрации"""
    logger.info("Отмена регистрации")
    await update.message.reply_text(
        "Регистрация отменена. Для начала регистрации используйте команду /start",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

async def process_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик QR-кодов"""
    try:
        user = update.effective_user
        logger.info(f"Обработка QR-кода от пользователя {user.id}")
        
        with app.app_context():
            сотрудник = Сотрудник.query.filter_by(telegram_id=user.id).first()
            
            if not сотрудник or not сотрудник.статус_регистрации:
                await update.message.reply_text(
                    "Необходимо сначала завершить регистрацию. Используйте команду /start"
                )
                return
            
            # Получение фото
            photo = await update.message.photo[-1].get_file()
            photo_bytes = await photo.download_as_bytearray()
            
            # Открываем изображение с помощью Pillow
            image = Image.open(io.BytesIO(photo_bytes))
            
            # Декодирование QR-кода
            decoded_objects = decode(image)
            
            if not decoded_objects:
                await update.message.reply_text("QR-код не обнаружен. Попробуйте еще раз.")
                return
            
            document_id = int(decoded_objects[0].data.decode('utf-8'))
            документ = Документ.query.get(document_id)
            
            if not документ:
                await update.message.reply_text("Документ не найден в системе.")
                return
            
            # Проверяем, не было ли уже подтверждения
            existing = ПрочтениеДокумента.query.filter_by(
                сотрудник_id=сотрудник.id,
                документ_id=документ.id
            ).first()
            
            if existing:
                await update.message.reply_text(
                    f"Вы уже подтвердили ознакомление с документом '{документ.название}' "
                    f"({existing.дата_прочтения.strftime('%d.%m.%Y %H:%M')})"
                )
                return
            
            # Регистрация прочтения
            прочтение = ПрочтениеДокумента(
                сотрудник_id=сотрудник.id,
                документ_id=документ.id,
                подтверждено=True
            )
            db.session.add(прочтение)
            db.session.commit()
            
            await update.message.reply_text(
                f"✅ Ознакомление с документом '{документ.название}' подтверждено."
            )
    except ValueError:
        await update.message.reply_text("Некорректный QR-код. Попробуйте еще раз.")
    except Exception as e:
        error_text = f"Ошибка при обработке QR-кода: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_text)
        await update.message.reply_text(
            "Произошла ошибка при обработке QR-кода. "
            "Мы записали информацию об ошибке и скоро её исправим. "
            "Пожалуйста, попробуйте позже."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет сообщение с помощью"""
    help_text = (
        "🤖 Доступные команды:\n\n"
        "/start - Начать работу или зарегистрироваться\n"
        "/stats - Показать вашу статистику по документам\n"
        "/unread - Список непрочитанных документов\n"
        "/help - Показать это сообщение\n\n"
        "📸 Чтобы отметить документ как прочитанный, "
        "отправьте фото QR-кода документа."
    )
    await update.message.reply_text(help_text)

# Глобальная переменная для бота
application = None

def get_bot():
    """Получить экземпляр бота"""
    global application
    return application

async def notify_new_document(document_id):
    """Отправка уведомления о новом документе"""
    try:
        with app.app_context():
            документ = Документ.query.get(document_id)
            if not документ:
                logger.error(f"Документ {document_id} не найден")
                return
            
            # Получаем всех сотрудников отдела
            сотрудники = Сотрудник.query.filter_by(
                отдел_id=документ.отдел_id,
                статус_регистрации=True
            ).all()
            
            bot = get_bot()
            if not bot:
                logger.error("Бот не инициализирован")
                return
            
            for сотрудник in сотрудники:
                if сотрудник.telegram_id:
                    try:
                        await bot.bot.send_message(
                            chat_id=сотрудник.telegram_id,
                            text=(
                                f"📄 Опубликован новый документ!\n\n"
                                f"Название: {документ.название}\n"
                                f"Тип: {документ.тип_документа}\n"
                                f"Срок ознакомления: {документ.срок_ознакомления.strftime('%d.%m.%Y')}\n\n"
                                f"Пожалуйста, ознакомьтесь с документом в системе и подтвердите ознакомление, отсканировав QR-код."
                            )
                        )
                        logger.info(f"Уведомление отправлено пользователю {сотрудник.id}")
                    except Exception as e:
                        logger.error(f"Ошибка отправки уведомления пользователю {сотрудник.id}: {str(e)}")
    except Exception as e:
        logger.error(f"Ошибка в notify_new_document: {str(e)}")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику по документам"""
    try:
        with app.app_context():
            сотрудник = Сотрудник.query.filter_by(telegram_id=update.effective_user.id).first()
            if not сотрудник or not сотрудник.статус_регистрации:
                await update.message.reply_text("Пожалуйста, сначала завершите регистрацию.")
                return

            # Получаем все документы отдела
            документы = Документ.query.filter_by(отдел_id=сотрудник.отдел_id).all()
            
            total_docs = len(документы)
            if total_docs == 0:
                await update.message.reply_text("В вашем отделе пока нет документов для ознакомления.")
                return

            # Подсчитываем статистику
            read_docs = sum(1 for док in документы if any(
                прочтение.сотрудник_id == сотрудник.id for прочтение in док.прочтения
            ))
            
            # Формируем сообщение
            message = f"📊 Ваша статистика:\n\n"
            message += f"Всего документов: {total_docs}\n"
            message += f"Прочитано: {read_docs}\n"
            message += f"Осталось прочитать: {total_docs - read_docs}\n"
            message += f"Процент выполнения: {int(read_docs/total_docs*100)}%"

            await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Ошибка в команде stats: {str(e)}")
        await update.message.reply_text("Произошла ошибка при получении статистики.")

async def unread_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список непрочитанных документов"""
    try:
        with app.app_context():
            сотрудник = Сотрудник.query.filter_by(telegram_id=update.effective_user.id).first()
            if not сотрудник or not сотрудник.статус_регистрации:
                await update.message.reply_text("Пожалуйста, сначала завершите регистрацию.")
                return

            # Получаем все документы отдела
            все_документы = Документ.query.filter_by(отдел_id=сотрудник.отдел_id).all()
            
            # Фильтруем непрочитанные
            непрочитанные = [
                док for док in все_документы 
                if not any(прочтение.сотрудник_id == сотрудник.id for прочтение in док.прочтения)
            ]

            if not непрочитанные:
                await update.message.reply_text("У вас нет непрочитанных документов! 🎉")
                return

            message = "📝 Непрочитанные документы:\n\n"
            for i, док in enumerate(непрочитанные, 1):
                срок = док.срок_ознакомления.strftime('%d.%m.%Y')
                message += f"{i}. {док.название}\n"
                message += f"   Тип: {док.тип_документа}\n"
                message += f"   Срок: {срок}\n\n"

            await update.message.reply_text(message)

    except Exception as e:
        logger.error(f"Ошибка в команде unread: {str(e)}")
        await update.message.reply_text("Произошла ошибка при получении списка непрочитанных документов.")

def main():
    """Запуск бота"""
    try:
        logger.info("Запуск бота...")
        
        # Проверяем токен
        if not Config.TELEGRAM_BOT_TOKEN:
            logger.error("Токен бота не установлен в конфигурации")
            return
        
        # Проверяем подключение к базе данных
        if not check_database_connection():
            logger.error("Нет подключения к базе данных")
            return
            
        global application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Обработчик регистрации
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', start)],
            states={
                ТАБЕЛЬНЫЙ_НОМЕР: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_employee_number)],
                ПОДРАЗДЕЛЕНИЕ: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_department)],
                ТЕЛЕФОН: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_phone)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        
        # Регистрация обработчиков
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.PHOTO, process_qr))
        application.add_handler(CommandHandler('stats', stats_command))
        application.add_handler(CommandHandler('unread', unread_command))
        
        logger.info("Бот успешно настроен и запускается...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        error_text = f"Ошибка при запуске бота: {str(e)}\n{traceback.format_exc()}"
        logger.error(error_text)

if __name__ == '__main__':
    main()
