import  mysql.connector
from mysql.connector import Error
import settings
import os

class MySQLConnection:

    def __init__(self, reset):
        try:
            host = os.getenv('DB_HOST')
            port = os.getenv('DB_PORT')
            user = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            database = os.getenv('DB_DATABASE')

            self.connection = None
            self.connection = mysql.connector.connect(host=host, port=port, user=user,
                                                password=password)
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                self.cursor = self.connection.cursor()
                self.migrate(database)
                self.cursor.execute("SELECT DATABASE() FROM DUAL;")
                record = self.cursor.fetchone()[0]
                print("You're connected to database: ", record)
                if reset:
                    self.reset(database)

        except Error as e:
            print("Error while connecting to MySQL", e)
            raise
    
    def __enter__(self):
       return self

    def __exit__(self, exception_type, exception_value, traceback):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            self.cursor.close()
            print("MySQL connection is closed")
    
    def migrate(self, database):
        self.cursor.execute("CREATE DATABASE IF NOT EXISTS {};".format(database))
        self.cursor.execute("USE {};".format(database))
        
        self.cursor.execute("CREATE TABLE IF NOT EXISTS keyframes (id INT AUTO_INCREMENT PRIMARY KEY, \
                    video_id VARCHAR(255), video_path VARCHAR(255), keyframe_id VARCHAR(255), \
                    keyframe_path VARCHAR(255), concept VARCHAR(255), shot INT, \
                    confidence TINYINT)")

        self.cursor.execute("ALTER TABLE keyframes ADD INDEX (concept)")
        self.cursor.execute("ALTER TABLE keyframes ADD INDEX (confidence)")

    def reset(self, database):
        """Drops and recreates the keyframes table.
        """

        self.cursor.execute("DROP TABLE IF EXISTS keyframes;")
        self.migrate(database)

