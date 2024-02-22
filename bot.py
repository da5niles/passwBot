import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode

API_TOKEN = '7001506676:AAHPCSFiXA7WvgJFAD1tWvD8sSwVMJawud4'

# Устанавливаем уровень логирования
#logging.basicConfig(level=logging.INFO)

# Инициализируем бот и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Создаем подключение к базе данных
conn = sqlite3.connect('passwords.db')
cursor = conn.cursor()

# Создаем таблицу в базе данных, если её еще нет
cursor.execute('''CREATE TABLE IF NOT EXISTS passwords
                (id INTEGER PRIMARY KEY, service TEXT, password TEXT)''')
conn.commit()
# Отслеживание 
async def on_start(_):
    print('Бот вышел в онлайн')

# Функция для добавления пароля в базу данных
async def add_password(message: types.Message):
    try:
        name = message.from_user.full_name
        command, service, password = message.text.split(maxsplit=2)
        cursor.execute('INSERT INTO passwords (service, password) VALUES (?, ?)', (service, password))
        conn.commit()
        await message.answer(f'Пароль для сервиса {service} успешно добавлен')
        print(f'{name} добавил(-а) пароль {password} для сервиса {service}')
    except ValueError:
        await message.answer('Некорректный формат команды. Используйте: /add <сервис> <пароль>')

# Функция для получения пароля из базы данных с проверкой кода доступа
async def get_password(message: types.Message):
    try:
        command, service, access_code = message.text.split(maxsplit=2)
        if access_code != '2007':
            await message.answer('Неверный код доступа')
            return
        
        cursor.execute('SELECT password FROM passwords WHERE service = ?', (service,))
        result = cursor.fetchone()
        if result:
            await message.answer(f'Пароль для сервиса {service}: {result[0]}')
        else:
            await message.answer(f'Пароль для сервиса {service} не найден')
    except ValueError:
        await message.answer('Некорректный формат команды. Используйте: /get <сервис> <код_доступа>')

# Чтение всех сервисов из бахы данных
async def get_services_list(message: types.Message):
    cursor.execute('SELECT DISTINCT service FROM passwords')
    result = cursor.fetchall()
    if result:
        services_list = '\n'.join([row[0] for row in result])
        await message.answer(f'*Список имеющихся сервисов:* \n{services_list}', parse_mode='Markdown')
    else:
        await message.answer('Список сервисов пуст')

# Обработчик команды /list
@dp.message_handler(commands=['list'])
async def process_get_services_list(message: types.Message):
    await get_services_list(message)


# Обработчик команды /add
@dp.message_handler(commands=['add'])
async def process_add_password(message: types.Message):
    await add_password(message)


# Обработчик команды /get
@dp.message_handler(commands=['get'])
async def process_get_password(message: types.Message):
    await get_password(message)


# Запускаем бот
if __name__ == '__main__':
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True, on_startup=on_start)
