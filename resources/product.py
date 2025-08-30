from flask import request, jsonify
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection

# 촬영하기 - 제품 보관하기 ✅
class ProductsResource(Resource):
    def post(self, purchase_id):
        data = request.get_json()
        if 'device_id' not in data or 'storage_location' not in data or purchase_id == None :
            response = {
                "error_code" : 400,
                "description" : "Bad Request",
                "message" : "필수 파라미터 누락"
            }
            return jsonify(response), 400
        

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
            "message" : "보관 장소 등록 성공"
        }, 200
