import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
import random
from googletrans import Translator  # Импортируем Translator для перевода

from config import TOKEN  # Убедитесь, что TOKEN правильно указан

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
translator = Translator()  # Создаем экземпляр Translator


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.reply("Привет! Давай поговорим о коктейлях?")

@dp.message(Command('help'))
async def help(message: types.Message):
    await message.answer('Этот бот умеет выполнять команды:'
                         '\n /start - Приветствие'
                         '\n /help - Список команд'
                         '\n /cocktail - Вывод информации о 5 случайно выбранных коктейлях')
#    return


@dp.message(Command("cocktail"))
async def cocktail(message: types.Message):
    cocktail_list = []
    for letter in 'abcdefghijklmnopqrstuvwxyz':
        url = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}'
        response = requests.get(url)
        if response.ok:  # Проверяем, что запрос прошёл успешно
            data = response.json()  # Преобразуем ответ в JSON
            drinks = data.get('drinks')  # Получаем список коктейлей
            if drinks:  # Если коктейли есть
                cocktail_list.extend(drinks)  # Добавляем коктейли в список

    if not cocktail_list:  # Если коктейлей нет
        await message.answer("К сожалению, коктейли не найдены.")
#        return

    random.shuffle(cocktail_list)
    for i in range(min(5, len(cocktail_list))):  # Убедимся, что не выходим за пределы списка
        ct = cocktail_list[i]
        cocktail_recipe = ct['strInstructions']
        cocktail_photo_url = ct['strDrinkThumb']

        # Переводим рецепт на русский
        cocktail_recipe_ru = translator.translate(cocktail_recipe, dest='ru').text

        cocktail_Ingredients = '\n'
        for n in range(1, 16):
            name = ct[f'strIngredient{n}']
            if name:  # Проверяем, что имя ингредиента не пустое
                cocktail_Ingredients += name + '\n'

        # Переводим ингредиенты на русский
        cocktail_Ingredients_ru = translator.translate(cocktail_Ingredients, dest='ru').text

        cocktail_modified = ct.get('dateModified', 'Не указано')  # Получаем дату, если она есть

        await message.answer(f"Коктейль №{i + 1}\n\n"
                             f"Рецепт:\n{cocktail_recipe_ru}\n\n"
                             f"Ингредиенты:\n{cocktail_Ingredients_ru}\n\n"
                             f"Дата обновления рецепта: {cocktail_modified}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":  # Исправлено на правильное имя
    asyncio.run(main())