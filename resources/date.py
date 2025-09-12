from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection
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

        except mysql.connector.Error as e :
            handle_mysql_integrity_error(e)
        
        except Exception as e :
            server_error(e)

        finally:
            cursor.close()
            connection.close()
    
    # 소비기한 - 소비기한 특정 제품 삭제 ✅
    def delete(self):
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        if 'purchase_ids' not in data:
            handle_value_error("구매 ID 누락")

        device_id = data.get('device_id')
        purchase_ids = data.get('purchase_ids')

        for purchase_id in purchase_ids:
            try :
                connection = get_connection()
                query = f'''
                        delete from purchase
                        where device_id = %s AND purchase_id = %s;
                        '''
                record = (device_id, purchase_id)
                cursor = connection.cursor(dictionary=True)
                cursor.execute(query, record)
                connection.commit()

                if cursor.rowcount == 0:
                    handle_not_found_error("삭제할 제품을 찾을 수 없음")

                return {
                    "success" : True,
                    "status" : 200,
                    "message" : "제품 삭제 성공"
                }, 200

            except mysql.connector.errors.IntegrityError as e:
                handle_mysql_integrity_error(e, "제품을 삭제할 수 없습니다!")
 
            except mysql.connector.Error as e :
                handle_mysql_connect_error(e)
        
            except Exception as e :
                server_error(e)

            finally:
                cursor.close()
                connection.close()
    
class DateItemResource(Resource):
    # 소비기한 - 소비기한 상세 정보 조회 ✅
    def get(self, purchase_id):
        device_id = request.args.get('device_id')
        if device_id == None :
            handle_value_error("디바이스 ID 누락")
        if purchase_id == None :
            handle_value_error("구매 ID 누락") 

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

            if result is None:
                handle_not_found_error("해당하는 제품을 찾을 수 없습니다.")

            return {
                "success" : True,
                "status" : 200,
                "message" : "상세 조회 성공",
                "data" : result
            }, 200

        except mysql.connector.Error as e :
            handle_mysql_connect_error(e)
        
        except Exception as e :
            server_error(e)

        finally:
            cursor.close()
            connection.close()
    
    # 소비기한 - 소비기한 즐겨찾기 업데이트 ✅
    def patch(self, purchase_id):
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        if 'is_favorite' not in data:
            handle_value_error("즐겨찾기 여부 누락")
        if purchase_id == None :
            handle_value_error("구매 ID 누락")

        try :
            connection = get_connection()

            query = '''
                select * from purchase
                WHERE device_id = %s AND purchase_id = %s
            '''
            record = (data['device_id'], purchase_id)
            cursor = connection.cursor()
            cursor.execute(query, record)

            if cursor.fetchone() is None:
                handle_not_found_error("해당하는 제품 또는 디바이스 ID를 찾을 수 없습니다.")
            
            query = '''
                UPDATE purchase
                SET is_favorite = %s
                WHERE device_id = %s AND purchase_id = %s
            '''
            record = (data['is_favorite'], data['device_id'], purchase_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            return {
                "success" : True,
                "status" : 200,
                "message" : "즐겨찾기 업데이트 성공"
            }, 200

        except mysql.connector.errors.IntegrityError as e:
            handle_mysql_integrity_error(e, "제품 정보를 업데이트할 수 없습니다!")
        
        except mysql.connector.Error as e :
            handle_mysql_connect_error(e)
        
        except Exception as e :
            server_error(e)

        finally:
            cursor.close()
            connection.close()
