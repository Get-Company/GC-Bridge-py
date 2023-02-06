import sys
import logging

class DbInterface:
    def __init__(self, db_type, config):
        self.logger = logging.getLogger(__name__)
        self.db_options = config["db_options"]
        self.db_type = db_type
        self.connection = self.__getConnection()
        self.cursor = self.connection.cursor(buffered=True) if self.connection else None

    def __getConnection(self):
        if self.db_type == "mysql":
            try:
                self.logger.info("__getConnection - Getting new mysqldb connection")
                connection = mysql.connector.connect(
                    host=self.db_options['mysql']['host'],
                    user=self.db_options['mysql']['user'],
                    password=self.db_options['mysql']['password'],
                    database=self.db_options['mysql']['database']
                )
                self.logger.info(f"__getConnection - Connection params: {connection}")
                return connection
            except mysql.connector.Error as error:
                self.logger.error(f"__getConnection - Failed to connect {self.db_options['host']} mysql server - {format(error)}")
                sys.exit(1)

    def closeConnection(self):
        self.logger.info("closeConnection - Closing connection")
        try:
            self.cursor.close()
            self.connection.close()
            self.logger.info("closeConnection - Connection closed")
        except (mysql.connector.Error) as error:
            self.logger.error(f"closeConnection - Failed to close the connection - {format(error)}")