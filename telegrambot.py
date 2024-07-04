import asyncio
import json
import logging
import re
import sys

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

import moviefinders.almasmovie
import moviefinders.mobomovie
import pasegs

from database import (CheakExist, InsertMovieOrSeriesDB,
                       MovieFindSubtitleTypes, SerialFInderEpisodes,
                       SerialFinderSeason, SerialFInderSubtitleQuality,
                       SerialFinderSubTypes)

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




@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"سلام, {html.bold(message.from_user.full_name)}!\n" + pasegs.start_message)

@dp.message()
async def get_name_movie(message: Message) -> None:
#    try:
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
                almas={}#serial
                mobo={}#serial
                all_links = {}#movie
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
                    movie_id_DB=CheakExist(movie_name,"movie")
                    if movie_id_DB is None:
                        print("------------------------hame link ha ingast------------------------")
                        print(all_links)
                        movie_id_DB=InsertMovieOrSeriesDB("movie",movie_name,all_links)
                        subtitle_types_dict=MovieFindSubtitleTypes(movie_id_DB)
                        builder = InlineKeyboardBuilder()
                        for subtitle_types,  subtitle_type_id in subtitle_types_dict.items():
                            #MST = movie sub id 
                            builder.button(text=subtitle_types, callback_data=f"MSTid_{subtitle_type_id}")
                        builder.adjust(1,1)
                        keyboard=builder.as_markup()
                        await message.answer(pasegs.finded,reply_markup=keyboard)
                    else:
                        subtitle_types_dict=MovieFindSubtitleTypes(movie_id_DB)
                        builder = InlineKeyboardBuilder()
                        for subtitle_types,  subtitle_type_id in subtitle_types_dict.items():
                            #MSTid = movie sub type id 
                            builder.button(text=subtitle_types, callback_data=f"MSTid_{subtitle_type_id}")
                        builder.adjust(1,1)
                        keyboard=builder.as_markup()
                        await message.answer(pasegs.finded,reply_markup=keyboard)
                elif mobo or almas:
                    keyboard=create_keyboard(compnait_lists(mobo,almas))
                    await message.answer(pasegs.finded,reply_markup=keyboard)
            
#    except TypeError:
#        await message.answer(pasegs.format_not_suport)

@dp.callback_query(lambda query: query.data.startswith('MSTid_'))
async def process_callback(query: types.CallbackQuery):
    subtitle_type_id=int(query.data.split("_")[1])
    quality_dict=MovieFinderQuality(subtitle_type_id)
    builder = InlineKeyboardBuilder()
    for quality ,quality_link in quality_dict.items():
         builder.button(text=quality, url=quality_link)
    builder.adjust(1,1)
    keyboard=builder.as_markup()
    await query.answer(pasegs.wait,reply_markup=keyboard)
    await query.message.answer("You clicked the button!")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
