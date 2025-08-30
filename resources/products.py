from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection

class ProductsResource(Resource):
    # 촬영하기 - 제품 보관하기 ✅
    def post(self, purchase_id):
        data = request.get_json()
        if 'device_id' not in data or 'storage_location' not in data or purchase_id == None :
            return {
                "error_code" : 400,
                "description" : "Bad Request",
                "message" : "필수 파라미터 누락"
            }, 400
        

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
            cursor.close()
            connection.close()

        except mysql.connector.errors.IntegrityError as e:
            print(e)
            cursor.close()
            connection.close()
            return {
                "error_code" : 400,
                "description" : "Bad Request",
                "message" : f"제품 정보를 저장할 수 없습니다! : {str(e)}"
            }, 400
        
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {
                "error_code" : 503,
                "description" : e.description,
                "message" : f"MySQL connector 에러 : {str(e)}"
            }, 503 # HTTPStatus.SERVICE_UNAVAILABLE

        except Exception as e :
            print(e)
            cursor.close()
            connection.close()
            return {
                "error_code" : 500,
                "description" : e.description,
                "message" : f"서버 내부 오류 : {str(e)}"
            }, 500
         
        return{
            "success" : True,
            "status" : 200,
            "message" : "보관 장소 등록 성공"
        }, 200
    
    # 소비기한 - 소비기한 보관 장소 수정 ✅
    def patch(self, purchase_id):
        data = request.get_json()
        if purchase_id == None or 'device_id' not in data or 'storage_location' not in data:
            return {
                "error_code" : 400,
                "description" : "Bad Request",
                "message" : "필수 파라미터 누락"
            }, 400

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

            if cursor.rowcount == 0:
                return {
                    "error_code": 404,
                    "description": "Not Found",
                    "message": "수정할 제품을 찾을 수 없음"
                }, 404
            
            connection.commit()
            cursor.close()
            connection.close()
        
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {
                "error_code" : 503,
                "description" : e.description,
                "message" : f"MySQL connector 에러 : {str(e)}"
            }, 503 # HTTPStatus.SERVICE_UNAVAILABLE
        
        except Exception as e :
            print(e)
            cursor.close()
            connection.close()
            return {
                "error_code" : 500,
                "description" : e.description,
                "message" : f"서버 내부 오류 : {str(e)}"
            }, 500


        return{
            "success" : True,
            "status" : 200,
            "message" : "보관 장소 수정 성공"
        }, 200
