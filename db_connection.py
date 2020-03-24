import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from model import database_model, Team, TeamStats, League


class DatabaseConnection:
    def __init__(self, database_name):
        self.database_name = database_name
        self.database_model = database_model
        self.db_engine = create_engine('sqlite:///{}'.format(self.database_name))
        if not os.path.exists(database_name):
            self.database_model.metadata.create_all(self.db_engine)
        self.session = sessionmaker(bind=self.db_engine)()

    def get_teams_by_league_and_names(self, league, names):
        teams = []
        for name in names:
            result = self.session.query(Team).filter(Team.league == league).filter(Team.name == name).first()
            teams.append(result if result is not None else Team(league=league, name=name))
        return teams

    def get_teams_by_season(self, season):
        teams_stats = self.session.query(TeamStats).filter(TeamStats.season == season).all()
        return [stats.team for stats in teams_stats]

    def save_league(self, league):
        self.session.add(league)
        self.session.commit()

    def save_table_entries(self, table_entries):
        self.session.add_all(table_entries)
        self.session.commit()

    def save_team_stats(self, team_stats):
        self.session.add_all(team_stats)
        self.session.commit()

    def save_teams(self, teams):
        self.session.add_all(teams)
        self.session.commit()

    def save_matches(self, matches):
        self.session.add_all(matches)
        self.session.commit()

    def delete_league_by_name(self, league_name):
        league = self.session.query(League).filter(League.name == league_name).first()
        if league is not None:
            self.session.delete(league)
            self.session.commit()
