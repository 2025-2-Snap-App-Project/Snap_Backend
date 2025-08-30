from flask import request
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection
from datetime import datetime

class DateResource(Resource):
    def get(self, purchase_id=None):
        # 소비기한 - 소비기한 상세 정보 조회 ✅
        if purchase_id:
            device_id = request.args.get('device_id')
            try:
                connection = get_connection()
                query = '''
                    select 
                        ProductItem.item_id,
                        Product.product_name,
                        ProductItem.expiration_date,
                        Purchase.storage_location,
                        ProductItem.ingredients,
                        ProductItem.summary
                    from Purchase
                    join ProductItem on Purchase.purchase_id = ProductItem.item_id
                    join Product on ProductItem.product_id = Product.product_id
                    where Purchase.purchase_id = %s and Purchase.device_id = %s;
                '''
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, (purchase_id, device_id))
                result = cursor.fetchone()
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
                "message" : "상세 조회 성공",
                "data" : result
            }, 200

        # 소비기한 - 소비기한 리스트 조회 ✅
        else:
            device_id = request.args.get('device_id')
            category = request.args.get('category')
            
            try:
                connection = get_connection()
                query = '''
                    select 
                        ProductItem.item_id,
                        Product.product_name,
                        ProductItem.expiration_date,
                        Purchase.is_favorite
                    from Purchase
                    join ProductItem on Purchase.purchase_id = ProductItem.item_id
                    join Product on ProductItem.product_id = Product.product_id
                    where Purchase.device_id = %s;
                '''
                record = (device_id, )
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                result_list = cursor.fetchall()
                filtered_list = []

                for result in result_list:
                    now_date = datetime.now()
                    db_date = datetime.strptime(result['expiration_date'], "%Y%m%d")
                    day_diff = (now_date - db_date).days
                    if category == '날짜 지남' and day_diff < 0:
                        filtered_list.append(result)
                    elif category == '기한 임박' and day_diff < 7:
                        filtered_list.append(result)
                    elif category == '기한 여유' and day_diff < 14:
                        filtered_list.append(result)

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
                "message" : "리스트 조회 성공",
                "data" : filtered_list
            }, 200
    
    
    def patch(self, purchase_id):
        data = request.get_json()
        # 소비기한 - 소비기한 보관 장소 수정 ✅
        if 'storage_location' in data:
            try :
                connection = get_connection()
                query = '''
                    UPDATE purchase
                    SET storage_location = %s
                    WHERE device_id = %s AND purchase_id = %s
                '''
                record = (data['storage_location'], data['device_id'], purchase_id)
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
                "message" : "보관 장소 수정 성공"
            }, 200
        
        # 소비기한 - 소비기한 즐겨찾기 업데이트 ✅
        if 'is_favorite' in data:
            try :
                connection = get_connection()
                query = '''
                    UPDATE purchase
                    SET is_favorite = %s
                    WHERE device_id = %s AND purchase_id = %s
                '''
                record = (data['is_favorite'], data['device_id'], purchase_id)
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
                "message" : "즐겨찾기 업데이트 성공"
            }, 200
    
    # 소비기한 - 소비기한 특정 제품 삭제 ✅
    def delete(self):
        data = request.get_json()
        device_id = data.get('device_id')
        purchase_ids = data.get('purchase_id')
        try :
            connection = get_connection()
            placeholders = ','.join(['%s'] * len(purchase_ids))
            query = f'''
                    delete from purchase
                    where device_id = %s AND purchase_id IN ({placeholders});
                    '''
            record = [device_id] + purchase_ids
            cursor = connection.cursor()
            cursor.execute(query, tuple(record))
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
            "message" : "제품 삭제 성공"
        }, 200
