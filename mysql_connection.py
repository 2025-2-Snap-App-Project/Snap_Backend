import mysql.connector

def get_connection():
    connection = mysql.connector.connect(
        host='localhost',        # MySQL 서버 주소
        user='root',             # root 계정
        password='0814',      # root 비밀번호
        database='snapdb'    # 사용할 DB
    )
    return connection
