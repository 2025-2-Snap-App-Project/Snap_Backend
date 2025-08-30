from flask import request
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection

class UserResource(Resource) :
    # 로그인 ✅
    def post(self) :
        data = request.get_json()
        try :
            connection = get_connection()
            query = '''
                    insert into user
                        (device_id, username)
                    values
                        (%s, %s);
                    '''
            record = (data['device_id'], data['username'])
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
        
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE
 
        return{
            "success" : True,
            "status" : 200,
            "message" : "로그인 성공"
        }, 200
    
    # 회원 탈퇴 ✅
    def delete(self) :
        data = request.get_json()
        device_id = data.get('device_id')
        try :
            connection = get_connection()
            query = '''
                    delete from user
                    where device_id = %s;
                    '''
            record = (device_id, )
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()
            cursor.close()
            connection.close()
 
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE
 
        return{
            "success" : True,
            "status" : 200,
            "message" : "회원탈퇴 성공"
        }, 200
