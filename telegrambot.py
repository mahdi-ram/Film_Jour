import asyncio
import logging
import sys
import re
from aiogram import Bot, Dispatcher, html 
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message ,InlineKeyboardMarkup ,InlineKeyboardButton
import pasegs
import moviefinders.almasmovie
import moviefinders.mobomovie
# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6664665455:AAHoJRgMdNLz9aYbC2elfRHjgUlNpB7szh8"
# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()
def remove_username(text: str) -> str:
    pattern = r'@TgISTRASH$'
    result = re.sub(pattern, '', text).strip()
    return result
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"سلام, {html.bold(message.from_user.full_name)}!\n" + pasegs.start_message)


@dp.message()
async def get_name_movie(message: Message) -> None:
    # handler @imdbbot message
    try:
        if message.via_bot and message.via_bot.username == "imdbot":
            pattern = r'tt\d+'
            match = re.search(pattern,  message.entities[1].url)
            if match:
                imdb_id = match.group()
            movie_name = remove_username(message.text)
            try:
                almasmovie_page = moviefinders.almasmovie.find_movie(imdb_id)
                mobomovie_page = moviefinders.mobomovie.find_movie(movie_name,imdb_id)
                await message.answer(almasmovie_page)
                await message.answer(mobomovie_page)
                if almasmovie_page[0] is None and mobomovie_page is None:
                    await message.answer(pasegs.not_fouand)
                elif  mobomovie_page[0] is None:
                    almaslinks = moviefinders.almasmovie.find_links(almasmovie_page[0],almasmovie_page[1])
                    alllinks=almaslinks
                    keyboard = InlineKeyboardMarkup()
                    for index in alllinks.items():
                        button = InlineKeyboardButton(index, callback_data='button_clicked')
                        keyboard.add(button)
                    await message.answer(pasegs.finded,reply_markup=keyboard)
                elif almasmovie_page[0] is None:
                    mobolinks =  moviefinders.mobomovie.find_links(mobomovie_page[0],mobomovie_page[1])
                    alllinks = mobolinks
                    keyboard = InlineKeyboardMarkup()
                    for index in alllinks.items():
                        button = InlineKeyboardButton(index, callback_data='button_clicked')
                        keyboard.add(button)
                    await message.answer(pasegs.finded,reply_markup=keyboard)
                else:
                    print("12222222222")
                    almaslinks = moviefinders.almasmovie.find_links(almasmovie_page[0],almasmovie_page[1])
                    mobolinks =  moviefinders.mobomovie.find_links(mobomovie_page[0],mobomovie_page[1])
                    alllinks = almaslinks | mobolinks
                    keyboard = InlineKeyboardMarkup()
                    for index in alllinks.items():
                        button = InlineKeyboardButton(index, callback_data='button_clicked')
                        keyboard.add(button)
                    await message.answer(pasegs.finded,reply_markup=keyboard)
            except TypeError:
                ...
    except TypeError:
        await message.answer(pasegs.format_not_suport)

proxies = {
    "http": "http://127.0.0.1:2081",
    "https": "http://127.0.0.1:2081",
}

async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML),proxies=proxies)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
