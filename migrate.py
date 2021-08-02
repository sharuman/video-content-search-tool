import  mysql.connector
from mysql.connector import Error

class MySQLConnection:

    def __init__(self, reset):
        try:
            self.connection = None
            self.connection = mysql.connector.connect(host='localhost',
                                                database='video_search')
            if self.connection.is_connected():
                db_Info = self.connection.get_server_info()
                print("Connected to MySQL Server version ", db_Info)
                self.cursor = self.connection.cursor()
                self.cursor.execute("select database();")
                record = self.cursor.fetchone()
                print("You're connected to database: ", record)
                if reset:
                    self.migrate()

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

    def migrate(self):
        self.cursor.execute("DROP TABLE IF EXISTS keyframes;")
        self.cursor.execute("CREATE TABLE keyframes (id INT AUTO_INCREMENT PRIMARY KEY, \
                    video_id VARCHAR(255), video_path VARCHAR(255), keyframe_id VARCHAR(255), \
                    keyframe_path VARCHAR(255), concept VARCHAR(255), shot INT, \
                    confidence TINYINT)")

        self.cursor.execute("CREATE INDEX index_concept ON keyframes (concept)")
        self.cursor.execute("CREATE INDEX index_confidence ON keyframes (confidence)")

        # query = "INSERT INTO keyframes (video_id, keyframe_id, concept, confidence) VALUES (%s, %s, %s, %s)"
        # val = [
        #     (666, 666, 'booty', 100),
        #     (666, 666, 'baby', 50),
        #     (666, 666, 'baloon', 10),
        #     (666, 666, 'body', 14),
        #     (666, 666, 'shady', 100),
        #     (666, 666, 'boost', 60)
        # ]
        # self.cursor.executemany(query, val)
        # self.connection.commit()