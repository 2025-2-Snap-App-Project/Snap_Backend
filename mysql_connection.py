import mysql.connector
from contextlib import contextmanager
from error_handler import *

def get_connection():
    connection = mysql.connector.connect(
        host='localhost',        # MySQL 서버 주소
        user='root',             # root 계정
        password='0814',      # root 비밀번호
        database='snapdb'    # 사용할 DB
    )
    return connection

@contextmanager
def get_db(dictionary=False):
    connection = get_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
        connection.commit()
    except mysql.connector.errors.IntegrityError as e:
        handle_mysql_integrity_error(e)
    except mysql.connector.Error as e :
        handle_mysql_integrity_error(e)
    except Exception as e :
        server_error(e)
    finally:
        cursor.close()
        connection.close()
