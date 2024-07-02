from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    subtitle_types = relationship("SubtitleType", back_populates='movie')

class SubtitleType(Base):
    __tablename__ = "subtitle_types"
    id = Column(Integer, primary_key=True)
    type = Column(String, nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id"), nullable=False)
    movie = relationship("Movie", back_populates="subtitle_types")
    qualities = relationship("Quality", back_populates="subtitle_type")

class Quality(Base):
    __tablename__ = "qualities"
    id = Column(Integer, primary_key=True)
    quality = Column(String, nullable=False)
    link = Column(String, nullable=False)
    type_id = Column(Integer, ForeignKey("subtitle_types.id"), nullable=False)
    subtitle_type = relationship("SubtitleType", back_populates="qualities")

# Create an engine
Movie_engine = create_engine('sqlite:///movie.db')
Base.metadata.create_all(Movie_engine)

# Create a session
Session = sessionmaker(bind=Movie_engine)()
