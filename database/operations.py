from .models import (Movie, Movie_engine, Quality, Season, Serial,
                    Serial_engine, Subtitle, SubtitleQuality, SubtitleType, SubtitleTypeMovie ,User,user_engine)
import json
from sqlalchemy.orm import sessionmaker
import re
# Create a session
Session = sessionmaker(bind=Movie_engine)()
Session_s = sessionmaker(bind=Serial_engine)()
Session_u=sessionmaker(bind=user_engine)()
def userexit(user_id):
    user = Session_u.query(User).filter_by(user_id=user_id).first()
    if user is None:
        return None
    return user
def userwrit(user_id, username, full_name):
    try:
        user = User(user_id=user_id, username=username, full_name=full_name)
        Session_u.add(user)
        Session_u.commit()
    except sqlalchemy.exc.IntegrityError:
        Session_u.rollback()
        raise
# function insert serial and movie to database
def clean_text(text: str) -> str:
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    pattern = r'@TgISTRASH$'
    result = re.sub(pattern, '', text).strip()
    return result
def InsertMovieOrSeriesDB(type: str, name: str, data: dict):
    if type == "movie":
        movie = Session.query(Movie).filter_by(name=name).first()
        if movie:
            # پاک کردن زیرنویس‌های قدیمی
            Session.query(SubtitleTypeMovie).filter_by(movie_id=movie.id).delete()
        else:
            movie = Movie(name=name)
            Session.add(movie)

        for subtitle_type, qualities in data.items():
            subtitle_type = clean_text(subtitle_type)
            text = (
                "زیرنویس انگلیسی 🏴󠁧󠁢󠁥󠁮󠁧󠁿" if subtitle_type == "HardSub" else
                "زیرنویس فارسی 🇮🇷" if subtitle_type == "soft-sub" else
                "دوبله فارسی 🗣" if subtitle_type == "dubbed" else
                subtitle_type
            )
            if text not in ["dubbed-sound", "subtitle"]:
                new_subtitle_type = SubtitleTypeMovie(type=text, movie=movie)
                Session.add(new_subtitle_type)
                for quality, link in qualities.items():
                    new_quality = Quality(quality=quality, link=link, subtitle_type=new_subtitle_type)
                    Session.add(new_quality)

        Session.commit()
        return CheakExist(name, type)
    else:  # serial
        serial = Session_s.query(Serial).filter_by(name=name).first()
        if serial:
            # پاک کردن فصل‌ها و زیرنویس‌های قدیمی
            Session_s.query(Season).filter_by(serial_id=serial.id).delete()
        else:
            serial = Serial(name=name)
            Session_s.add(serial)

        for season, subtyps in data.items():
            new_season = Season(number=season, serial=serial)
            Session_s.add(new_season)
            for subtyp, qualitys in subtyps.items():
                subtitle_type = SubtitleType(type=subtyp, season=new_season)
                Session_s.add(subtitle_type)
                for quality, episodes in qualitys.items():
                    subtitle_quality = SubtitleQuality(quality=quality, subtitle_type=subtitle_type)
                    Session_s.add(subtitle_quality)
                    subtitle1 = Subtitle(value=json.dumps(episodes), subtitle_quality=subtitle_quality)
                    Session_s.add(subtitle1)

        Session_s.commit()
        return CheakExist(name, type)

# function check exist name in database
def CheakExist(name: str, type: str):
    if type == "movie":
        movie_id = Session.query(Movie.id).filter(Movie.name == name).scalar()
        if movie_id:
            return movie_id
        else:
            return None
    else:  # serial
        serial_id = Session_s.query(Serial.id).filter(Serial.name == name).scalar()
        if serial_id:
            return serial_id
        else:
            return None
def getname(id: int, type: str):
    if type == "movie":
        movie_name = Session.query(Movie.name).filter(Movie.id == id).scalar()
        if movie_name:
            return movie_name
        else:
            return None
    else:  # serial
        serial_name= Session_s.query(Serial.name).filter(Serial.id == id).scalar()
        if serial_name:
            return serial_name
        else:
            return None
def refresh_data(type, id, new_data):
    if type == 'movie':
        movie = Session.query(Movie).filter_by(id=id).first()
        if movie:
            name = movie.name
        else:
            raise ValueError("Movie not found")

        # فراخوانی تابع برای به‌روزرسانی
        InsertMovieOrSeriesDB(type, name, new_data)

    elif type == 'serial':
        serial = Session_s.query(Serial).filter_by(id=id).first()
        if serial:
            name = serial.name
        else:
            raise ValueError("Serial not found")

        # فراخوانی تابع برای به‌روزرسانی
        InsertMovieOrSeriesDB(type, name, new_data)

    else:
        raise ValueError("Invalid type. Please use 'movie' or 'serial'.")

# function movie find subtitle types by movie id
def MovieFindSubtitleTypes(movieid: int) -> dict:
    subtitle_types = Session.query(SubtitleTypeMovie).filter(
        SubtitleTypeMovie.movie_id == movieid).all()
    subtitle_types_dict = {}
    for subtitle_type in subtitle_types:
        subtitle_types_dict[subtitle_type.type] = subtitle_type.id
    return subtitle_types_dict

# function movie find quality by subtitle_types.id
def MovieFinderQuality(subtitle_types_id: int) -> dict:
    qualities = Session.query(Quality).filter(
        Quality.type_id == subtitle_types_id).all()
    quality_dict = {}
    for quality in qualities:
        quality_dict[quality.quality] = quality.link
    return quality_dict

# function serial find season by serial id
def SerialFinderSeason(serialid: int) -> dict:
    seasons = Session_s.query(Season).filter(Season.serial_id == serialid).all()  # Changed variable name to seasons
    season_dict = {}
    for season in seasons:
        season_dict[f"{season.number} فصل"] = season.id
    return season_dict

# function serial find subtype by season.id
def SerialFinderSubTypes(season_id: int) -> dict:
    subtypes = Session_s.query(SubtitleType).filter(
        SubtitleType.season_id == season_id).all()
    subtype_dict = {}
    for subtype in subtypes:
        text = (
            "زیرنویس انگلیسی 🏴󠁧󠁢󠁥󠁮󠁧󠁿" if subtype.type == "HardSob" else
            "زیرنویس فارسی 🇮🇷" if subtype.type == "soft-sub" else
            "دوبله فارسی 🗣" if subtype.type == "dubbed" else
            "زیرنویس انگلیسی 🏴󠁧󠁢󠁥󠁮󠁧󠁿"
            )
        subtype_dict[text] = subtype.id
    return subtype_dict

# function serial find subtitle quality by subtype.id
def SerialFInderSubtitleQuality(subtype_id: int) -> dict:
    subtitle_qualities = Session_s.query(SubtitleQuality).filter(
        SubtitleQuality.subtitle_type_id == subtype_id).all()  # Changed variable name to subtitle_qualities
    subtitle_quality_dict = {}
    for subtitle_quality in subtitle_qualities:
        subtitle_quality_dict[subtitle_quality.quality] = subtitle_quality.id  # Fixed assignment
    return subtitle_quality_dict

# function serial find episodes by subtitle_quality.id
def SerialFInderEpisodes(subtitle_quality_id: int) -> dict:
    episodes = Session_s.query(Subtitle).filter(Subtitle.subtitle_quality_id == subtitle_quality_id).one()
    return episodes.value


# Session close
Session.close()
Session_s.close()
