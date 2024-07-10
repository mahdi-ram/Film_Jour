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
from Moviedatafind import infodata
import moviefinders.almasmovie
import moviefinders.mobomovie
import pasegs
from moviefinders import all_links
from database import (CheakExist, InsertMovieOrSeriesDB,
                       MovieFindSubtitleTypes, SerialFInderEpisodes,
                       SerialFinderSeason, SerialFInderSubtitleQuality,
                       SerialFinderSubTypes,MovieFinderQuality,userexit,userwrit)

TOKEN = "6664665455:AAHoJRgMdNLz9aYbC2elfRHjgUlNpB7szh8"

dp = Dispatcher() 
def creat_keboard(data:dict,patearn:str):
    builder = InlineKeyboardBuilder()
    for x,  y in data.items():
        builder.button(text=x, callback_data=f"{patearn}_{y}")
    builder.adjust(1,1)
    keyboard=builder.as_markup()
    return keyboard

def clean_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    pattern = r'@TgISTRASH$'
    result = re.sub(pattern, '', text).strip()
    return result




@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    user_id = message.from_user.id
    username = message.from_user.username
    full_name = message.from_user.full_name
    if userexit(user_id) is None:
        userwrit(user_id,username,full_name)
        
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

                # Check if the movie or series exists in the database
                movie_id_DB = CheakExist(movie_name, "movie")
                serial_id_DB = CheakExist(movie_name, "serial")

                if movie_id_DB:
                    # If it's a movie
                    subtitle_types_dict = MovieFindSubtitleTypes(movie_id_DB)
                    keyboard = create_keyboard(subtitle_types_dict, "MSTid")
                    data=infodata(imdb_id)
                    await message.answer_photo(photo=data[2], caption=f"{data[0]} ({data[1]})\n\n:توضیحات\n{data[3]}", reply_markup=keyboard)
                elif serial_id_DB:
                    # If it's a serial
                    Serial_Seasons = SerialFinderSeason(int(serial_id_DB))
                    keyboard = create_keyboard(Serial_Seasons, "SSid")
                    data=infodata(imdb_id)
                    await message.answer_photo(photo=data[2], caption=f"{data[0]} ({data[1]})\n\n:توضیحات\n{data[3]}", reply_markup=keyboard)
                else:
                    # If not found in the database, fetch the links
                    DL_links = all_links(movie_name, imdb_id)
                    if DL_links is None:
                        await message.answer(pasegs.not_found)
                    elif DL_links[0] == "movie":
                        movie_id_DB = InsertMovieOrSeriesDB("movie", movie_name, DL_links)
                        subtitle_types_dict = MovieFindSubtitleTypes(movie_id_DB)
                        keyboard = create_keyboard(subtitle_types_dict, "MSTid")
                        data=infodata(imdb_id)
                        await message.answer_photo(photo=data[2], caption=f"{data[0]} ({data[1]})\n\n:توضیحات\n{data[3]}", reply_markup=keyboard)
                    else:
                        serial_id_DB = InsertMovieOrSeriesDB("serial", movie_name, DL_links)
                        Serial_Seasons = SerialFinderSeason(int(serial_id_DB))
                        keyboard = create_keyboard(Serial_Seasons, "SSid")
                        data=infodata(imdb_id)
                        await message.answer_photo(photo=data[2], caption=f"{data[0]} ({data[1]})\n\n:توضیحات\n{data[3]}", reply_markup=keyboard)
    except TypeError:
        await message.answer("مشکل پیش آمده لطفا به ادمین پیام دهید")

@dp.callback_query(lambda query: query.data.startswith('MSTid_'))
async def process_callback(query: types.CallbackQuery):
    subtitle_type_id=int(query.data.split("_")[1])
    quality_dict=MovieFinderQuality(subtitle_type_id)
    builder = InlineKeyboardBuilder()
    for quality ,quality_link in quality_dict.items():
         builder.button(text=quality, url=quality_link)
    builder.adjust(1,1)
    keyboard=builder.as_markup()
    await query.message.answer("لطفا کیفیت را مشخص کنید",reply_markup=keyboard)
    await query.answer(pasegs.wait)

@dp.callback_query(lambda query: query.data.startswith('SSid_'))
async def process_callback(query: types.CallbackQuery):
    serial_season_id=int(query.data.split("_")[1])
    SubTypes_dict=SerialFinderSubTypes(serial_season_id)
    builder = InlineKeyboardBuilder()
    for SubType ,SubType_id in SubTypes_dict.items():
        #SSTid serial subtitel type id
        builder.button(text=SubType,  callback_data=f"SSTid_{SubType_id}")
    builder.adjust(1,1)
    keyboard=builder.as_markup()
    await query.message.answer("لطفا نوع زیرنویس  را مشخص کنید",reply_markup=keyboard)
    await query.answer(pasegs.wait)

@dp.callback_query(lambda query: query.data.startswith('SSTid_'))
async def process_callback(query: types.CallbackQuery):
    subtype_id=int(query.data.split("_")[1])
    SubtitleQualitys_dict=SerialFInderSubtitleQuality(subtype_id)
    builder = InlineKeyboardBuilder()
    for Quality ,Quality_id in SubtitleQualitys_dict.items():
        #SSQid seiral sub quality id
        builder.button(text=Quality,  callback_data=f"SSQid_{Quality_id}")
    builder.adjust(1,1)
    keyboard=builder.as_markup()
    await query.message.answer("لطفا نوع کیفیت  را مشخص کنید",reply_markup=keyboard)
    await query.answer(pasegs.wait)

@dp.callback_query(lambda query: query.data.startswith('SSQid_'))
async def process_callback(query: types.CallbackQuery):
    quality_id=int(query.data.split("_")[1])
    episod_dict=SerialFInderEpisodes(quality_id)
    builder = InlineKeyboardBuilder()
    for episode ,link in json.loads(episod_dict).items():
        builder.button(text=episode, url=link)
    builder.adjust(2,2)
    keyboard=builder.as_markup()
    inline_message_id = query.inline_message_id
    await query.message.edit_text("لطفا قسمت  را انتخاب کنید",reply_markup=keyboard ,inline_message_id=inline_message_id)
    await query.answer(pasegs.wait)

async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
