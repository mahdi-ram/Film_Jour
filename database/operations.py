from .models import (Movie, Movie_engine, Quality, Season, Serial,
                    Serial_engine, Subtitle, SubtitleQuality, SubtitleType, SubtitleTypeMovie)
import json
from sqlalchemy.orm import sessionmaker

# Create a session
Session = sessionmaker(bind=Movie_engine)()
Session_s = sessionmaker(bind=Serial_engine)()

# function insert serial and movie to database
def InsertMovieOrSeriesDB(type: str, name: str, data: dict):
    if type == "movie":
        new_movie = Movie(name=name)
        for subtitle_type, qualities in data.items():
            text = (
                "زیرنویس انگلیسی 🏴󠁧󠁢󠁥󠁮󠁧󠁿" if subtitle_type == "HardSub" else
                "زیرنویس فارسی 🇮🇷" if subtitle_type == "soft-sub" else
                "دوبله فارسی 🗣" if subtitle_type == "dubbed" else
                subtitle_type
            )
            if text == "dubbed-sound":
                pass
            else:
                new_subtitle_type = SubtitleTypeMovie(type=text, movie=new_movie)
                for quality, link in qualities.items():
                    new_quality = Quality(quality=quality, link=link, subtitle_type=new_subtitle_type)

        Session.add(new_movie)
        Session.commit()
        return CheakExist(name, type)
    else:  # serial
        new_serial = Serial(name=name)
        for season, subtyps in data.items():
            new_season = Season(number=season, serial=new_serial)  # Changed variable name to new_season
            for subtyp, qualitys in subtyps.items():
                subtitle_type = SubtitleType(type=subtyp, season=new_season)
                for quality, episodes in qualitys.items():
                    subtitle_quality = SubtitleQuality(quality=quality, subtitle_type=subtitle_type)
                    subtitle1 = Subtitle(value=json.dumps(episodes), subtitle_quality=subtitle_quality)

        Session_s.add(new_serial)
        Session_s.commit()
        return CheakExist(name, type)

# function check exist name in database
def CheakExist(name: str, type: str):
    if type == "movie":
        movie_id = Session.query(Movie.id).filter(
            Movie.name == name).scalar()
        if movie_id:
            return movie_id
        else:
            return None
    else:  # serial
        serial_id = Session_s.query(Serial.id).filter(
            Serial.name == name).scalar()
        if serial_id:
            return serial_id
        else:
            return None

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
            "زیرنویس انگلیسی 🏴󠁧󠁢󠁥󠁮󠁧󠁿" if subtype.type == "HardSub" else
            "زیرنویس فارسی 🇮🇷" if subtype.type == "soft-sub" else
            "دوبله فارسی 🗣" if subtype.type == "dubbed" else
            subtype.type
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
