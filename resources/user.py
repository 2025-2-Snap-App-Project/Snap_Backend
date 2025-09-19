from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import *
from error_handler import *

class UserResource(Resource) :
    # 로그인 ✅
    def post(self) :
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        if 'username' not in data:
            handle_value_error("사용자명 누락")
        
        query = "INSERT INTO user (device_id, username) VALUES (%s, %s)"
        record = (data['device_id'], data['username'])
        with get_db() as cursor:
            cursor.execute(query, record)
        return {
            "success" : True,
            "status" : 200,
            "message" : "로그인 성공"
        }, 200
    
    # 회원 탈퇴 ✅
    def delete(self) :
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")

        query = "DELETE FROM user WHERE device_id = %s"
        record = (data['device_id'], )
        with get_db() as cursor:
            cursor.execute(query, record)
        
        if cursor.rowcount == 0:
            handle_not_found_error("해당 디바이스 ID의 사용자를 찾을 수 없음")
        
        return {
            "success" : True,
            "status" : 200,
            "message" : "회원탈퇴 성공"
        }, 200
