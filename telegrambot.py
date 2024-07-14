import asyncio
import json
import logging
import re
import sys

from aiogram import Bot, Dispatcher, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart ,Command,CommandObject
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from Moviedatafind import infodata
# import moviefinders.almasmovie
# import moviefinders.mobomovie
import pasegs
from moviefinders import all_links
from database import (CheakExist, InsertMovieOrSeriesDB,
                      MovieFindSubtitleTypes, SerialFInderEpisodes,
                      SerialFinderSeason, SerialFInderSubtitleQuality,
                      SerialFinderSubTypes, MovieFinderQuality, userexit, userwrit, refresh_data, getname)

TOKEN = "6664665455:AAHoJRgMdNLz9aYbC2elfRHjgUlNpB7szh8"

dp = Dispatcher()

def shorten_caption(caption):
    MAX_CAPTION_LENGTH=800
    if len(caption) > MAX_CAPTION_LENGTH:
        return caption[:MAX_CAPTION_LENGTH - 3] + "..."
    return caption

def create_keyboard(data: dict, patearn: str, id: int, type: str, imdb_id: str):
    builder = InlineKeyboardBuilder()
    for x,  y in data.items():
        builder.button(text=x, callback_data=f"{patearn}_{y}")
    if type == "movie":
        builder.button(text="تازه سازی اطلاعات♻️",callback_data=f"re_{id}_M_{imdb_id}")
        builder.button(text="لینک اشتراک گزاری📡",callback_data=f"MSL_{id}_{imdb_id}")
    else:
        builder.button(text="تازه سازی اطلاعات♻️",callback_data=f"re_{id}_S_{imdb_id}")
        builder.button(text="لینک اشتراک گزاری📡",callback_data=f"SSL_{id}_{imdb_id}")
    
    builder.adjust(1, 1)
    keyboard = builder.as_markup()
    return keyboard


def clean_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    pattern = r'@TgISTRASH$'
    result = re.sub(pattern, '', text).strip()
    return result


@dp.message(Command("start"))
async def command_start_handler(message: Message,command:CommandObject) -> None:
    user_id = message.from_user.id
    if userexit(user_id) is None:
        username = message.from_user.username
        full_name = message.from_user.full_name
        userwrit(user_id, username, full_name)
    args = command.args
    if args:
        if args.startswith("SGL_"):
            serial_id_DB=args.split("_")[1]
            imdb_id=args.split("_")[2]
            Serial_Seasons = SerialFinderSeason(int(serial_id_DB))
            keyboard = create_keyboard(Serial_Seasons, "SSid", serial_id_DB, "serial", imdb_id)
            data = infodata(imdb_id)
            emtiaz = f"⭐️ امیتاز {data[5]} از 10"
            await message.answer_photo(photo=data[2], caption=f"{pasegs.film} {data[0]}({data[1]})\n{pasegs.sal_sakht} {data[4]}\n{emtiaz}\n\n{pasegs.kholase} {shorten_caption(data[3])}\n", show_caption_above_media=True, reply_markup=keyboard)
        elif args.startswith("MGL_"):
            movie_id_DB=args.split("_")[1]
            imdb_id=args.split("_")[2]
            subtitle_types_dict = MovieFindSubtitleTypes(movie_id_DB)
            keyboard = create_keyboard(subtitle_types_dict, "MSTid", movie_id_DB, "movie", imdb_id)
            data = infodata(imdb_id)
            emtiaz = f"⭐️ امیتاز {data[5]} از 10"
            await message.answer_photo(photo=data[2], caption=f"{pasegs.serial} {data[0]}({data[1]})\n{pasegs.sal_sakht} {data[4]}\n{emtiaz}\n\n{pasegs.kholase} {shorten_caption(data[3])}\n", show_caption_above_media=True, reply_markup=keyboard)
    else:
        builder = InlineKeyboardBuilder()
        builder.button(text="🔍جستجو با نام سریال/فیلم", callback_data="koil")
        builder.button(text="❔راهنما", callback_data="help")
        builder.button(text="📣کانال اطلاع رسانی",  url='https://t.me/your_channel')
        builder.adjust(1, 1)
        keyboard = builder.as_markup()
        await message.answer(f"سلام, {html.bold(message.from_user.full_name)}!\n" + pasegs.start_message, reply_markup=keyboard)
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
                    keyboard = create_keyboard(
                        subtitle_types_dict, "MSTid", movie_id_DB, "movie", imdb_id)
                    data = infodata(imdb_id)
                    emtiaz = f"⭐️ امیتاز {data[5]} از 10"
                    react = types.ReactionTypeEmoji(emoji="🔥")
                    await message.react([react])
                    await message.answer_photo(photo=data[2], caption=f"{pasegs.serial} {data[0]}({data[1]})\n{pasegs.sal_sakht} {data[4]}\n{emtiaz}\n\n{pasegs.kholase} {shorten_caption(data[3])}\n", show_caption_above_media=True, reply_markup=keyboard)
                elif serial_id_DB:
                    # If it's a serial
                    Serial_Seasons = SerialFinderSeason(int(serial_id_DB))
                    keyboard = create_keyboard(
                        Serial_Seasons, "SSid", serial_id_DB, "serial", imdb_id)
                    data = infodata(imdb_id)
                    emtiaz = f"⭐️ امیتاز {data[5]} از 10"
                    react = types.ReactionTypeEmoji(emoji="🔥")
                    await message.react([react])
                    await message.answer_photo(photo=data[2], caption=f"{pasegs.film} {data[0]}({data[1]})\n{pasegs.sal_sakht} {data[4]}\n{emtiaz}\n\n{pasegs.kholase} {shorten_caption(data[3])}\n", show_caption_above_media=True, reply_markup=keyboard)
                else:
                    # If not found in the database, fetch the links
                    DL_links = all_links(movie_name, imdb_id)
                    if DL_links is None:
                        react = types.ReactionTypeEmoji(emoji="😢")
                        await message.react([react])
                        await message.answer(pasegs.not_fouand)
                    elif DL_links[0] == "movie":
                        movie_id_DB = InsertMovieOrSeriesDB("movie", movie_name, DL_links[1])
                        subtitle_types_dict = MovieFindSubtitleTypes(movie_id_DB)
                        keyboard = create_keyboard(
                            subtitle_types_dict, "MSTid", movie_id_DB, "movie", imdb_id)
                        data = infodata(imdb_id)
                        emtiaz = f"⭐️ امیتاز {data[5]} از 10"
                        react = types.ReactionTypeEmoji(emoji="🔥")
                        await message.react([react])
                        await message.answer_photo(photo=data[2], caption=f"{pasegs.film} {data[0]}({data[1]})\n{pasegs.sal_sakht} {data[4]}\n{emtiaz}\n\n{pasegs.kholase} {shorten_caption(data[3])}\n", show_caption_above_media=True, reply_markup=keyboard)
                    else:
                        serial_id_DB = InsertMovieOrSeriesDB(
                            "serial", movie_name, DL_links[1])
                        Serial_Seasons = SerialFinderSeason(int(serial_id_DB))
                        keyboard = create_keyboard(
                            Serial_Seasons, "SSid", serial_id_DB, "serial", imdb_id)
                        data = infodata(imdb_id)
                        emtiaz = f"⭐️ امیتاز {data[5]} از 10"
                        react = types.ReactionTypeEmoji(emoji="🔥")
                        await message.react([react])
                        await message.answer_photo(photo=data[2], caption=f"{pasegs.serial} {data[0]}({data[1]})\n{pasegs.sal_sakht} {data[4]}\n{emtiaz}\n\n{pasegs.kholase} {shorten_caption(data[3])}\n", show_caption_above_media=True, reply_markup=keyboard)
    except TypeError:
        react = types.ReactionTypeEmoji(emoji="🤯")
        await message.react([react])
        await message.answer("مشکل پیش آمده لطفا به ادمین پیام دهید")


@dp.callback_query(lambda query: query.data.startswith('re_'))
async def process_callback(query: types.CallbackQuery):
    imdb_id = query.data.split("_")[3]
    movie_id = int(query.data.split("_")[1])
    movietype = query.data.split("_")[2]
    if movietype == "M":
        movietype = "movie"
    else:
        movietype = "serial"
    movie_name = getname(movie_id, movietype)
    DL_links = all_links(movie_name, imdb_id)
    if refresh_data(movietype, movie_id, DL_links[1]):
        await query.message.answer("بروزرسانی شد لطفا دوباره اسم فیلم/سریال خود را وارد کنید🍺")


@dp.callback_query(lambda query: query.data.startswith('SSL_'))
async def process_callback(query: types.CallbackQuery):
    movie_id_DB = int(query.data.split("_")[1])
    imdb_id=query.data.split("_")[2]
    base_link="https://t.me/connettestthis_bot?start="
    await  query.message.answer(f"{pasegs.shearlink}\n{base_link}SGL_{movie_id_DB}_{imdb_id}")


@dp.callback_query(lambda query: query.data.startswith('MSL_'))
async def process_callback(query: types.CallbackQuery):
    movie_id_DB = int(query.data.split("_")[1])
    imdb_id=query.data.split("_")[2]
    base_link="https://t.me/connettestthis_bot?start="
    await  query.message.answer(f"{pasegs.shearlink}\n{base_link}MGL_{movie_id_DB}_{imdb_id}")

@dp.callback_query(lambda query: query.data.startswith('MSTid_'))
async def process_callback(query: types.CallbackQuery):
    subtitle_type_id = int(query.data.split("_")[1])
    quality_dict = MovieFinderQuality(subtitle_type_id)
    builder = InlineKeyboardBuilder()
    for quality, quality_link in quality_dict.items():
        builder.button(text=quality, url=quality_link)
    builder.adjust(1, 1)
    keyboard = builder.as_markup()
    await query.message.answer("لطفا کیفیت را مشخص کنید", reply_markup=keyboard)
    await query.answer(pasegs.wait)


@dp.callback_query(lambda query: query.data.startswith('SSid_'))
async def process_callback(query: types.CallbackQuery):
    serial_season_id = int(query.data.split("_")[1])
    SubTypes_dict = SerialFinderSubTypes(serial_season_id)
    builder = InlineKeyboardBuilder()
    for SubType, SubType_id in SubTypes_dict.items():
        # SSTid serial subtitel type id
        builder.button(text=SubType,  callback_data=f"SSTid_{SubType_id}")
    builder.adjust(1, 1)
    keyboard = builder.as_markup()
    await query.message.answer("لطفا نوع زیرنویس  را مشخص کنید", reply_markup=keyboard)
    await query.answer(pasegs.wait)


@dp.callback_query(lambda query: query.data.startswith('SSTid_'))
async def process_callback(query: types.CallbackQuery):
    subtype_id = int(query.data.split("_")[1])
    SubtitleQualitys_dict = SerialFInderSubtitleQuality(subtype_id)
    builder = InlineKeyboardBuilder()
    for Quality, Quality_id in SubtitleQualitys_dict.items():
        # SSQid seiral sub quality id
        builder.button(text=Quality,  callback_data=f"SSQid_{Quality_id}")
    builder.adjust(1, 1)
    keyboard = builder.as_markup()
    await query.message.answer("لطفا نوع کیفیت  را مشخص کنید", reply_markup=keyboard)
    await query.answer(pasegs.wait)


@dp.callback_query(lambda query: query.data.startswith('SSQid_'))
async def process_callback(query: types.CallbackQuery):
    quality_id = int(query.data.split("_")[1])
    episod_dict = SerialFInderEpisodes(quality_id)
    builder = InlineKeyboardBuilder()
    for episode, link in json.loads(episod_dict).items():
        builder.button(text=episode, url=link)
    builder.adjust(2, 2)
    keyboard = builder.as_markup()
    inline_message_id = query.inline_message_id
    await query.message.edit_text("لطفا قسمت  را انتخاب کنید", reply_markup=keyboard, inline_message_id=inline_message_id)
    await query.answer(pasegs.wait)


@dp.callback_query(lambda query: query.data == "help")
async def process_callback(query: types.CallbackQuery):
    builder = InlineKeyboardBuilder()
    builder.button(text=pasegs.oilo, callback_data="vidio")
    builder.adjust(1, 1)
    keyboard = builder.as_markup()
    await query.message.answer(pasegs.help, reply_markup=keyboard)
    await query.answer(pasegs.wait)


@dp.callback_query(lambda query: query.data == "vidio")
async def process_callback(query: types.CallbackQuery):
    try:
        video_url="https://eu-central.storage.cloudconvert.com/tasks/009c2520-013e-4b79-87ad-f6ae68851d7d/Screencast%20from%202024-07-11%2017-55-47.mp4?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=cloudconvert-production%2F20240711%2Ffra%2Fs3%2Faws4_request&X-Amz-Date=20240711T142749Z&X-Amz-Expires=86400&X-Amz-Signature=bd6c545bbe85ca1f5a140a9fff21b9e30e7d9652eb50617d5679a36be3b3071d&X-Amz-SignedHeaders=host&response-content-disposition=inline%3B%20filename%3D%22Screencast%20from%202024-07-11%2017-55-47.mp4%22&response-content-type=video%2Fmp4&x-id=GetObject"
        await bot.send_video(message.chat.id, video_url)
    except Exception as e:
        await  query.message.answer(f"مشکلی در ارسال فیلم پیش آمد")


@dp.callback_query(lambda query: query.data == "koil")
async def process_callback(query: types.CallbackQuery):
    await query.message.answer(pasegs.searcher)
    await query.answer(pasegs.wait)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
