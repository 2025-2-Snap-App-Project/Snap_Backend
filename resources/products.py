from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import *
from error_handler import *

class ProductsResource(Resource):
    # 촬영하기 - 제품 보관하기 ✅
    def post(self, purchase_id):
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        if 'storage_location' not in data:
            handle_value_error("보관 장소 누락")
        if purchase_id == None :
            handle_value_error("구매 ID 누락") 

        query = "INSERT INTO purchase (purchase_id, device_id, storage_location, is_favorite) VALUES (%s,%s,%s,%s)"
        record = (purchase_id, data['device_id'], data['storage_location'], False)
        with get_db() as cursor:
            cursor.execute(query, record)
        return {
            "success" : True,
            "status" : 200,
            "message" : "보관 장소 등록 성공"
        }, 200
    
    # 소비기한 - 소비기한 보관 장소 수정 ✅
    def patch(self, purchase_id):
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        if 'storage_location' not in data:
            handle_value_error("보관 장소 누락")
        if purchase_id == None :
            handle_value_error("구매 ID 누락") 

        # 단계 1) 디바이스 ID와 구매 ID가 일치하는 제품 먼저 찾기
        query = "SELECT * FROM purchase WHERE device_id = %s AND purchase_id = %s"
        record = (data['device_id'], purchase_id)
        with get_db() as cursor:
            cursor.execute(query, record)

        # 검색된 제품이 없는 경우
        if cursor.fetchone() is None:
            handle_not_found_error("해당하는 제품 또는 디바이스 ID를 찾을 수 없습니다.")

        # 단계 2) 디바이스 ID와 구매 ID가 일치하는 제품 -> 해당 제품의 보관 장소 업데이트
        query = "UPDATE purchase SET storage_location = %s WHERE device_id = %s AND purchase_id = %s"
        record = (data['storage_location'], data['device_id'], purchase_id)
        with get_db() as cursor:
            cursor.execute(query, record)
        
        return {
            "success" : True,
            "status" : 200,
            "message" : "보관 장소 수정 성공"
        }, 200
