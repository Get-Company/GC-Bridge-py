from sqlalchemy.exc import IntegrityError, InvalidRequestError, SQLAlchemyError
from main import db
from loguru import logger

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
            logger.error("Error: Integrity constraint violated.")
        except InvalidRequestError:
            db.session.rollback()
            logger.info("Error: Invalid request.")
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Error: {e}")
        finally:
            db.session.close()
