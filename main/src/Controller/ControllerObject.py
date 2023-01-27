from sqlalchemy.exc import IntegrityError, InvalidRequestError, SQLAlchemyError
from main import db


class ControllerObject:
    def __int__(self, erp_obj):
        self.erp_obj = erp_obj

    def sync_all(self):
        pass

    def sync_changed(self):
        pass

    def commit_with_errors(self):
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            print("Error: Integrity constraint violated.")
        except InvalidRequestError:
            db.session.rollback()
            print("Error: Invalid request.")
        except SQLAlchemyError as e:
            db.session.rollback()
            print(f"Error: {e}")
