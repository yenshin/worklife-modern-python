from sqlalchemy.orm import Session


class BaseRepository:
    def __init__(self, model):
        self.model = model

    def _query(self, session, *_, **kwargs):
        filters = [getattr(self.model, k) == v for k, v in kwargs.items()]
        return session.query(self.model).filter(*filters)

    def get(self, session, *_, **kwargs):
        return self._query(session, **kwargs).one_or_none()

    def get_many(self, session, *_, **kwargs):
        return self._query(session, **kwargs).all()

    def create(self, session: Session, obj_in):
        session.add(obj_in)
        return obj_in

    def update(self, session, obj_in):
        raise NotImplementedError

    def delete(self, session, id):
        session.delete(self.get(session, id=id))
