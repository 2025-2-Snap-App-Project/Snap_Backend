from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import *
from datetime import datetime
from error_handler import *

class DateListResource(Resource):
    # 소비기한 - 소비기한 리스트 조회 ✅
    def get(self):
        device_id = request.args.get('device_id')
        category = request.args.get('category')
        if device_id == None:
            handle_value_error("디바이스 ID 누락")
        if category == None:
            handle_value_error("카테고리 구분 누락")
        
        query = '''
            SELECT 
                ProductItem.item_id,
                Product.product_name,
                ProductItem.expiration_date,
                Purchase.is_favorite
            FROM Purchase
            JOIN ProductItem ON Purchase.purchase_id = ProductItem.item_id
            JOIN Product ON ProductItem.product_id = Product.product_id
            JOIN Purchase.device_id = %s;
        '''

        with get_db(dictionary=True) as cursor:
            cursor.execute(query, (device_id, ))
            result_list = cursor.fetchall()
            filtered_list = []

        for result in result_list:
            now_date = datetime.now()
            db_date = datetime.strptime(result['expiration_date'], "%Y%m%d")
            day_diff = (db_date - now_date).days
            if category == '날짜지남' and day_diff < 0:
                filtered_list.append(result)
            elif category == '기한임박' and day_diff < 7:
                filtered_list.append(result)
            elif category == '기한여유' and day_diff < 14:
                filtered_list.append(result)
            else:
                pass

        return {
            "success" : True,
            "status" : 200,
            "message" : "리스트 조회 성공",
            "data" : filtered_list
        }, 200
    
    # 소비기한 - 소비기한 특정 제품 삭제 ✅
    def delete(self):
        data = request.get_json()
        handle_value_error(data, ['device_id', 'purchase_ids'])

        device_id = data.get('device_id')
        purchase_ids = data.get('purchase_ids')

        query = "DELETE FROM purchase WHERE device_id = %s AND purchase_id = %s"
        for purchase_id in purchase_ids:
            with get_db(dictionary=True) as cursor:
                cursor.execute(query, (device_id, purchase_id))
                if cursor.rowcount == 0:
                    handle_not_found_error("삭제할 제품을 찾을 수 없음")
        return {
            "success" : True,
            "status" : 200,
            "message" : "제품 삭제 성공"
        }, 200
    
class DateItemResource(Resource):
    # 소비기한 - 소비기한 상세 정보 조회 ✅
    def get(self, purchase_id):
        device_id = request.args.get('device_id')
        if device_id == None :
            handle_value_error("디바이스 ID 누락")
        if purchase_id == None :
            handle_value_error("구매 ID 누락") 

        query = '''
            SELECT 
                ProductItem.item_id,
                Product.product_name,
                ProductItem.expiration_date,
                Purchase.storage_location,
                ProductItem.ingredients,
                ProductItem.summary
            FROM Purchase
            JOIN ProductItem ON Purchase.purchase_id = ProductItem.item_id
            JOIN Product ON ProductItem.product_id = Product.product_id
            WHERE Purchase.purchase_id = %s AND Purchase.device_id = %s;
        '''

        with get_db(dictionary=True) as cursor:
            cursor.execute(query, (purchase_id, device_id))
            result = cursor.fetchone()
        
        if result is None:
            handle_not_found_error("해당하는 제품을 찾을 수 없습니다.")

        return {
            "success" : True,
            "status" : 200,
            "message" : "상세 조회 성공",
            "data" : result
        }, 200
    
    # 소비기한 - 소비기한 즐겨찾기 업데이트 ✅
    def patch(self, purchase_id):
        data = request.get_json()
        handle_value_error(data, ['device_id', 'is_favorite'])
        if purchase_id == None :
            handle_value_error("구매 ID 누락")

        select_query = "SELECT * FROM purchase WHERE device_id = %s AND purchase_id = %s"
        update_query = "UPDATE purchase SET is_favorite = %s WHERE device_id = %s AND purchase_id = %s"
        
        with get_db() as cursor:
            cursor.execute(select_query, (data['device_id'], purchase_id))
            if cursor.fetchone() is None:
                handle_not_found_error("해당하는 제품 또는 디바이스 ID를 찾을 수 없습니다.")
            cursor.execute(update_query, (data['is_favorite'], data['device_id'], purchase_id))
            
        return {
            "success" : True,
            "status" : 200,
            "message" : "즐겨찾기 업데이트 성공"
        }, 200
