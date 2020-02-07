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
    league_id = Column(Integer, ForeignKey('league.id'))
    league = relationship('League', back_populates='teams')
    stats = relationship('TeamStats', back_populates='team')
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
    season_id = Column(Integer, ForeignKey('season.id'))
    season = relationship('Season', back_populates='table')
    table_entries = relationship('TableEntry', back_populates='table', cascade='delete')


class Season(database_model):
    __tablename__ = 'season'
    id = Column(Integer, primary_key=True)
    league_id = Column(Integer, ForeignKey('league.id'))
    league = relationship('League', back_populates='seasons')
    table = relationship('Table', back_populates='season', cascade='delete')
    matches = relationship('Match', back_populates='season', cascade='delete')
    teams_stats = relationship('TeamStats', back_populates='season', cascade='delete')
    name = Column(String)


class TeamStats(database_model):
    __tablename__ = 'team_stats'
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'))
    team = relationship('Team', back_populates='stats')
    season_id = Column(Integer, ForeignKey('season.id'))
    season = relationship('Season', back_populates='teams_stats')
    matches_played = Column(Integer)
    wins = Column(Integer)
    draws = Column(Integer)
    losses = Column(Integer)
    goals_scored = Column(Integer)
    goals_conceded = Column(Integer)
    points = Column(Integer)


class League(database_model):
    __tablename__ = 'league'
    id = Column(Integer, primary_key=True)
    teams = relationship('Team', back_populates='league', cascade='delete')
    seasons = relationship('Season', back_populates='league', cascade='delete')
    country = Column(String)
    name = Column(String)
