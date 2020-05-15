from providers.db import database

Model = database.Model


def to_dict(self):
    repair = {}
    for column in self.__table__.columns:
        if column.name in getattr(self, 'hidden', []):
            """
            if model to dict should hide some attributes
            set this hidden property as a list, like:
            hidden = ['password', 'token']
            """
            continue
        if column.name in getattr(self, 'casts', {}):
            """
            if model to dict should auto convert some columns value instance type
            set this cast like:
            casts = {'id': 'int', 'created_at': 'string'}
            """
            pass
        repair[column.name] = getattr(self, column.name, None)
    return repair


Model.to_dict = to_dict
