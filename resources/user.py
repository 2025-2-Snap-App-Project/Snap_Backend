from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection

class UserResource(Resource) :
    # 로그인 ✅
    def post(self) :
        data = request.get_json()
        if 'device_id' or 'username' not in data:
            response = {
                "error_code" : 400,
                "description" : "Bad Request",
                "message" : "필수 파라미터 누락"
            }
            return jsonify(response), 400
        
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
            response = {
                "error_code" : 503,
                "description" : e.description,
                "message" : f"MySQL connector 에러 : {str(e)}"
            }
            return jsonify(response), 503 # HTTPStatus.SERVICE_UNAVAILABLE
        
        except Exception as e :
            print(e)
            cursor.close()
            connection.close()
            response = {
                "error_code" : 500,
                "description" : e.description,
                "message" : f"서버 내부 오류 : {str(e)}"
            }
            return jsonify(response), 500
        
        return{
            "success" : True,
            "status" : 200,
            "message" : "로그인 성공"
        }, 200
    
    # 회원 탈퇴 ✅
    def delete(self) :
        data = request.get_json()
        if 'device_id' not in data:
            response = {
                "error_code" : 400,
                "description" : "Bad Request",
                "message" : "필수 파라미터 누락"
            }
            return jsonify(response), 400
        
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
                response = {
                    "error_code": 404,
                    "description": "Not Found",
                    "message": "해당 device_id의 사용자를 찾을 수 없음"
                }
                return jsonify(response), 404
            
            cursor.close()
            connection.close()
 
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            response = {
                "error_code" : 503,
                "description" : e.description,
                "message" : f"MySQL connector 에러 : {str(e)}"
            }
            return jsonify(response), 503 # HTTPStatus.SERVICE_UNAVAILABLE
        
        except Exception as e :
            print(e)
            cursor.close()
            connection.close()
            response = {
                "error_code" : 500,
                "description" : e.description,
                "message" : f"서버 내부 오류 : {str(e)}"
            }
            return jsonify(response), 500

        return{
            "success" : True,
            "status" : 200,
            "message" : "회원탈퇴 성공"
        }, 200
