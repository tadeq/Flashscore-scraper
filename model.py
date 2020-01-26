from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

database_model = declarative_base()


class Team(database_model):
    __tablename__ = 'team'
    id = Column(Integer, primary_key=True)
    table_entries = relationship('TableEntry', back_populates='team')
    home_matches = relationship('Match', foreign_keys='Match.home_team_id', back_populates='home_team')
    away_matches = relationship('Match', foreign_keys='Match.away_team_id', back_populates='away_team')
    name = Column(String)


class Match(database_model):
    __tablename__ = 'match'
    id = Column(Integer, primary_key=True)
    season_id = Column(Integer, ForeignKey('season.id'))
    season = relationship('Season', back_populates='matches')
    home_team_id = Column(Integer, ForeignKey('team.id'))
    home_team = relationship('Team', foreign_keys=[home_team_id], back_populates='home_matches')
    away_team_id = Column(Integer, ForeignKey('team.id'))
    away_team = relationship('Team', foreign_keys=[away_team_id], back_populates='away_matches')
    date = Column(String)
    home_team_score = Column(Integer)
    away_team_score = Column(Integer)


class TableEntry(database_model):
    __tablename__ = 'table_entry'
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('table.id'))
    table = relationship('Table', back_populates='table_entries')
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship('Team', back_populates='table_entries')
    place = Column(Integer)


class Table(database_model):
    __tablename__ = 'table'
    id = Column(Integer, primary_key=True)
    season = relationship('Season', back_populates='table')
    table_entries = relationship('TableEntry', back_populates='table')


class Season(database_model):
    __tablename__ = 'season'
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer, ForeignKey('table.id'))
    table = relationship('Table', back_populates='season')
    matches = relationship('Match', back_populates='season')
    name = Column(String)
