from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import json
Base = declarative_base()


class Serial(Base):
    __tablename__ = 'serials'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    seasons = relationship('Season', back_populates='serial')


class Season(Base):
    __tablename__ = 'seasons'

    id = Column(Integer, primary_key=True)
    number = Column(Integer, nullable=False)
    serial_id = Column(Integer, ForeignKey('serials.id'), nullable=False)
    serial = relationship('Serial', back_populates='seasons')
    subtitle_types = relationship('SubtitleType', back_populates='season')


class SubtitleType(Base):
    __tablename__ = 'subtitle_types'

    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    season_id = Column(Integer, ForeignKey('seasons.id'), nullable=False)
    season = relationship('Season', back_populates='subtitle_types')
    subtitle_qualities = relationship('SubtitleQuality', back_populates='subtitle_type')


class SubtitleQuality(Base):
    __tablename__ = 'subtitle_qualities'

    id = Column(Integer, primary_key=True)
    quality = Column(String, nullable=False)
    subtitle_type_id = Column(Integer, ForeignKey('subtitle_types.id'), nullable=False)

    subtitle_type = relationship('SubtitleType', back_populates='subtitle_qualities')
    subtitles = relationship('Subtitle', back_populates='subtitle_quality')


class Subtitle(Base):
    __tablename__ = 'subtitles'

    id = Column(Integer, primary_key=True)
    value = Column(String, nullable=False)
    subtitle_quality_id = Column(Integer, ForeignKey('subtitle_qualities.id'), nullable=False)
    subtitle_quality = relationship('SubtitleQuality', back_populates='subtitles')


# ایجاد یک موتور و یک جلسه
Serial_engine = create_engine('sqlite:///seirals.db')
Base.metadata.create_all(Serial_engine)

Session = sessionmaker(bind=Serial_engine)
session = Session()

def creator(name:str,data_seiral:dict):
    serial=Serial(name=name)
    for season,subtyps in  data_seiral.items():
        season=Season(number=season,serial=serial)
        for subtyp,qualitys in subtyps.items():
            subtitle_type=SubtitleType(type=subtyp,season=season)
            for quality,episodes in qualitys.items():
                subtitle_quality=SubtitleQuality(quality=quality,subtitle_type=subtitle_type)
                subtitle1 = Subtitle(value=json.dumps(episodes),subtitle_quality=subtitle_quality)
    session.add(serial)


session.commit()