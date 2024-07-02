from sqlalchemy.orm import sessionmaker
from models import Movie, SubtitleType, Quality, Movie_engine
# Create a session
Session = sessionmaker(bind=Movie_engine)()
# function inset serial and movie to databse


def InsertMovieOrSeriesDB(movietype: str, moviename: str, data: dict):
    if movietype == "movie":
        new_movie = Movie(name=moviename)
        for subtitle_type, qualities in data.items():
            new_subtitle_type = SubtitleType(
                type=subtitle_type, movie=new_movie)

            for quality, link in qualities.items():
                new_quality = Quality(
                    quality=quality, link=link, subtitle_type=new_subtitle_type)

        Session.add(new_movie)
        Session.commit()
        return CheakExist(moviename, movietype)
    # serial
    else:
        pass

# function cheak exist name in database


def CheakExist(moviename: str, type: str):
    if type == "movie":
        movie_id = Session.query(Movie.id).filter(
            Movie.name == moviename).scalar()
        if movie_id:
            return movie_id
        else:
            return None
    # seial
    else:
        pass
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
    qualitys = Session.query(Quality).filter(
        Quality.type_id == subtitle_types_id).all()
    quality_dict = {}
    for quality in qualitys:
        quality_dict[quality.quality] = quality.link
    return quality_dict


# Session close
Session.close()
