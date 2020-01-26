import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from model import database_model, Team, Match, TableEntry, Table, Season


class DatabaseConnection:
    def __init__(self, database_name):
        if os.path.exists(database_name):
            os.remove(database_name)
        self.database_name = database_name
        self.database_model = database_model
        self.db_engine = create_engine('sqlite:///{}'.format(self.database_name))
        self.database_model.metadata.create_all(self.db_engine)
        self.session = sessionmaker(bind=self.db_engine)()

    def get_teams_by_names(self, names):
        self.session.query(Team).filter(Team.name.in_(names))
