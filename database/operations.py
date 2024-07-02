from models import (Movie, Movie_engine, Quality, Season, Serial,
                    Serial_engine, Subtitle, SubtitleQuality, SubtitleType)
from sqlalchemy.orm import sessionmaker

# Create a session
Session = sessionmaker(bind=Movie_engine)()
Session_s = sessionmaker(bind=Serial_engine)()
# function inset serial and movie to databse


def InsertMovieOrSeriesDB(type: str, name: str, data: dict):
    if type == "movie":
        new_movie = Movie(name=name)
        for subtitle_type, qualities in data.items():
            new_subtitle_type = SubtitleType(
                type=subtitle_type, movie=new_movie)

            for quality, link in qualities.items():
                new_quality = Quality(
                    quality=quality, link=link, subtitle_type=new_subtitle_type)

        Session.add(new_movie)
        Session.commit()
        return CheakExist(name, type)
    # serial
    else:
        new_serial = Serial(name=name)
        for season, subtyps in data_seiral.items():
            season = Season(number=season, serial=new_serial)
            for subtyp, qualitys in subtyps.items():
                subtitle_type = SubtitleType(type=subtyp, season=season)
                for quality, episodes in qualitys.items():
                    subtitle_quality = SubtitleQuality(
                        quality=quality, subtitle_type=subtitle_type)
                    subtitle1 = Subtitle(value=json.dumps(
                        episodes), subtitle_quality=subtitle_quality)
        Session_s.add(new_serial)
        Session_s.commit()
        return CheakExist(name, type)

# function cheak exist name in database


def CheakExist(name: str, type: str):
    if type == "movie":
        movie_id = Session.query(Movie.id).filter(
            Movie.name == name).scalar()
        if movie_id:
            return movie_id
        else:
            return None
    # seial
    else:
        Serial_id = Session_s.query(Serial.id).filter(
            Serial.name == name).scalar()
        if Serial_id:
            return Serial_id
        else:
            return None

# function Movie finde subtitle types by movie id


def MovieFindSubtitleTypes(movieid: int) -> dict:
    subtitle_types = Session.query(SubtitleType).filter(
        SubtitleType.movie_id == movieid).all()
    subtitle_types_dict = {}
    for subtitle_type in subtitle_types:
        subtitle_types_dict[subtitle_type.type] = subtitle_type.id
    return subtitle_types_dict

# function movie find Quality by subtitle_types.id


def MovieFinderQuality(subtitle_types_id: int) -> dict:
    qualitys = Session.query(Quality).filter(Quality.type_id == subtitle_types_id).all()
    quality_dict = {}
    for quality in qualitys:
        quality_dict[quality.quality] = quality.link
    return quality_dict

# function serial find season by serial id
def SerialFinderSeason(serialid:int)->dict:
    Seasons=Session_s.query(Season).filter(Season.serial_id==serialid).all()
    Season_dict={}
    for Season in Seasons:
        Season_dict[f"{Season.number} فصل"]=Season.id
#function serial find subtype by Season.id
def SerialFinderSubTypes(Season_id:id)->dict:
    SubTypes=Session_s.query(SubtitleType).filter(SubtitleType.season_id==Season_id).all()
    SubType_dict={}
    for SubType in SubTypes:
        text = (
        "زیرنویس انگلیسی 🏴󠁧󠁢󠁥󠁮󠁧󠁿" if SubType.type == "HardSub" else
        "زیرنویس فارسی 🇮🇷" if SubType.type == "soft-sub" else
        "دوبله فارسی 🗣" if SubType.type == "dubbed" else
        SubType.type)
        SubType_dict[text]=SubType.id
    return SubType_dict
#function serial find SubtitleQuality by subtype.id
def SerialFInderSubtitleQuality(subtype_id:int)->dict:
    SubtitleQualitys=Session_s.query(SubtitleQuality).filter(SubtitleQuality.subtitle_type_id==subtype_id).all()
    SubtitleQuality_dict={}
    for SubtitleQuality in SubtitleQualitys:
        SubtitleQuality_dict[SubtitleQuality.quality]=SubtitleQualitys.id
    return SubtitleQuality_dict
#function serial find Episodes by SubtitleQualitys.id
def SerialFInderEpisodes(Subtitle_Qualitys_id:int)->dict:
    episodes=Session_s.query(Subtitle).filter(Subtitle.subtitle_quality_id==Subtitle_Qualitys_id).one()
    return episodes
# Session close
Session.close()
Session_s.close()
