import asyncio
import logging
import sys
import re
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import pasegs
import moviefinders.almasmovie
import moviefinders.mobomovie
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6664665455:AAHoJRgMdNLz9aYbC2elfRHjgUlNpB7szh8"

dp = Dispatcher() 
def compnait_lists(x:dict,y:dict)-> dict:
    x=x
    for key_x ,valu_x in x.items():
            list_v={}
            for key_y , valu_y in y.items():
                if key_x == key_y:
                    for key_valu_y,valu_valu_y in valu_y.items():
                        list_v[key_valu_y]=valu_valu_y
                    for key_valu_x,valu_valu_x in valu_x.items():
                        list_v[key_valu_x]=valu_valu_x
                    x[key_x]=list_v
    return x

def clean_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    pattern = r'@TgISTRASH$'
    result = re.sub(pattern, '', text).strip()
    return result

def create_keyboard(links):
    builder = InlineKeyboardBuilder()

    for index, value in links.items():
        text = (
        "زیرنویس انگلیسی 🏴󠁧󠁢󠁥󠁮󠁧󠁿" if index == "HardSub" else
        "زیرنویس فارسی 🇮🇷" if index == "soft-sub" else
        "دوبله فارسی 🗣" if index == "dubbed" else
        f"فصل {index} 🗂" if isinstance(index, int) or index.isdigit() else
        index)
        builder.button(text=f"{text}", callback_data=f"{value}")
    builder.adjust(1,1)
    return builder.as_markup()

@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"سلام, {html.bold(message.from_user.full_name)}!\n" + pasegs.start_message)

@dp.message()
async def get_name_movie(message: Message) -> None:
    try:
        if message.via_bot and message.via_bot.username == "imdbot":
            pattern = r'tt\d+'
            match = re.search(pattern, message.entities[1].url)
            if match:
                imdb_id = match.group()
                movie_name = clean_text(message.text)
                
            almasmovie_page = moviefinders.almasmovie.find_movie(imdb_id)
            mobomovie_page = moviefinders.mobomovie.find_movie(movie_name.strip(), imdb_id)
                
            if not almasmovie_page[0] and not mobomovie_page[0]:
                await message.answer(pasegs.not_fouand)
            else:
                almas={}
                mobo={}
                all_links = {}
                if almasmovie_page[0]:
                    almas_links = moviefinders.almasmovie.find_links(almasmovie_page[0], almasmovie_page[1])
                    if almas_links[0]=="movie":
                        all_links.update(almas_links[1])
                    else:
                        almas.update(almas_links[1])
                if mobomovie_page[0]:
                    mobo_links = moviefinders.mobomovie.find_links(mobomovie_page[0], mobomovie_page[1])
                    if mobo_links[0]=="movie":
                        all_links.update(mobo_links[1])
                    else:
                        mobo.update(mobo_links[1])
                    
                if all_links:
                    keyboard = create_keyboard(all_links)
                    await message.answer(pasegs.finded, reply_markup=keyboard)
                elif mobo or almas:
                    keyboard=create_keyboard(compnait_lists(mobo,almas))
                    await message.answer(pasegs.finded, reply_markup=keyboard)
                else:
                    await message.answer(pasegs.not_fouand)
    except TypeError:
        await message.answer(pasegs.format_not_suport)

@dp.callback_query(lambda query: query.data.startswith('Har'))
async def process_callback(query: types.CallbackQuery):
    await query.answer(pasegs.wait)
    await query.message.answer("You clicked the button!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
