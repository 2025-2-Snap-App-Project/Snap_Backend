from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection
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

        try :
            connection = get_connection()
            query = '''
                    insert into purchase
                        (purchase_id, device_id, storage_location, is_favorite)
                    values
                        (%s,%s,%s,%s);
                    '''
            record = (purchase_id, data['device_id'], data['storage_location'], False)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            return {
                "success" : True,
                "status" : 200,
                "message" : "보관 장소 등록 성공"
            }, 200

        except mysql.connector.errors.IntegrityError as e:
            handle_mysql_integrity_error(e, "제품 정보를 저장할 수 없습니다!")
        
        except mysql.connector.Error as e :
            handle_mysql_integrity_error(e)

        except Exception as e :
            server_error(e)

        finally:
            cursor.close()
            connection.close()
    
    # 소비기한 - 소비기한 보관 장소 수정 ✅
    def patch(self, purchase_id):
        data = request.get_json()
        if 'device_id' not in data:
            handle_value_error("디바이스 ID 누락")
        if 'storage_location' not in data:
            handle_value_error("보관 장소 누락")
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
                SET storage_location = %s
                WHERE device_id = %s AND purchase_id = %s
            '''
            record = (data['storage_location'], data['device_id'], purchase_id)
            cursor = connection.cursor()
            cursor.execute(query, record)
            connection.commit()

            return{
                "success" : True,
                "status" : 200,
                "message" : "보관 장소 수정 성공"
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
