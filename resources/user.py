from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection
from error_handler import *

class UserResource(Resource) :
    # 로그인 ✅
    def post(self) :
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        if 'username' not in data:
            handle_value_error("사용자명 누락")
        
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

        except mysql.connector.errors.IntegrityError as e:
            cursor.close()
            connection.close()
            handle_mysql_integrity_error(e, "동일 디바이스 ID가 이미 존재합니다. 다시 시도해주세요.")
        
        except mysql.connector.Error as e :
            cursor.close()
            connection.close()
            handle_mysql_integrity_error(e)
        
        except Exception as e :
            cursor.close()
            connection.close()
            server_error(e)
        
        return{
            "success" : True,
            "status" : 200,
            "message" : "로그인 성공"
        }, 200
    
    # 회원 탈퇴 ✅
    def delete(self) :
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        
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

            if cursor.rowcount == 0:
                handle_not_found_error("해당 디바이스 ID의 사용자를 찾을 수 없음")
            
            cursor.close()
            connection.close()

        except mysql.connector.errors.IntegrityError as e:
            cursor.close()
            connection.close()
            handle_mysql_integrity_error(e, "회원 탈퇴에 실패했습니다. 다시 시도해주세요.")

        except mysql.connector.Error as e :
            cursor.close()
            connection.close()
            handle_mysql_connect_error(e)
        
        except Exception as e :
            cursor.close()
            connection.close()
            server_error(e)

        return{
            "success" : True,
            "status" : 200,
            "message" : "회원탈퇴 성공"
        }, 200
