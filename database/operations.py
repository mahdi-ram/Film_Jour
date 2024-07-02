from models import Movie,SubtitleType,Quality,Session
#inset serial and movie to databse
def InsertMovieOrSeriesDB(movietype: str, moviename: str, data: dict):
    if movietype == "movie":
        new_movie = Movie(name=moviename)
        for subtitle_type, qualities in data.items():
            new_subtitle_type = SubtitleType(type=subtitle_type, movie=new_movie)

            for quality, link in qualities.items():
                new_quality = Quality(quality=quality, link=link, subtitle_type=new_subtitle_type)

        Session.add(new_movie)
        Session.commit()
    #serial
    else:
        pass

#cheak exist name in database
def CheakExist(moviename:str,type:str)->bool:
    if type=="movie":
        movie_id = session.query(Movie).filter(Movie.name == moviename).first()
        if movie_id:
            return movie.id
        else:
            return None
    #seial
    else:
        pass
        
#test data
data={'soft-sub': {'720p Web-Dl x265/10 Bit': 'http://dl72.free-download-center.cfd/v2/movie/2024/tt12037194/softsub/Furiosa.A.Mad.Max.Saga.2024.720p.Web-Dl.x265.10-Bit(MoboMovies).mkv', '720p Web-Dl x264/8 Bit': 'http://dl72.free-download-center.cfd/v2/movie/2024/tt12037194/softsub/Furiosa.A.Mad.Max.Saga.2024.720p.Web-Dl.x264.8-Bit(MoboMovies).mkv', '1080p Web-Dl x265/10 Bit': 'http://dl72.free-download-center.cfd/v2/movie/2024/tt12037194/softsub/Furiosa.A.Mad.Max.Saga.2024.1080p.Web-Dl.x265.10-Bit(MoboMovies).mkv', '1080p Web-Dl x264/8 Bit': 'http://dl72.free-download-center.cfd/v2/movie/2024/tt12037194/softsub/Furiosa.A.Mad.Max.Saga.2024.1080p.Web-Dl.x264.8-Bit(MoboMovies).mkv'}}
InsertMovieOrSeriesDB("movie","Furiosa: A Mad Max Saga 2024",data)