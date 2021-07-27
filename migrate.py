import  mysql.connector
from mysql.connector import Error

try:
    connection = None
    connection = mysql.connector.connect(host='localhost',
                                         database='video_search')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)
        
        cursor.execute("CREATE TABLE keyframes (id INT AUTO_INCREMENT PRIMARY KEY, \
            video_id VARCHAR(255), video_path VARCHAR(255), keyframe_id VARCHAR(255), \
            keyframe_path VARCHAR(255), concept VARCHAR(255), confidence FLOAT(2))")

        cursor.execute("CREATE INDEX index_concept ON keyframes (concept)")
        cursor.execute("CREATE INDEX index_confidence ON keyframes (confidence)")

except Error as e:
    print("Error while connecting to MySQL", e)
    raise
finally:
    if connection is not None and connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")

