from flask import request
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection

# 촬영하기 - 제품 보관하기 ✅
class ProductsResource(Resource):
    def post(self, purchase_id):
        data = request.get_json()
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
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE
 
        return{
            "success" : True,
            "status" : 200,
            "message" : "보관 장소 등록 성공"
        }, 200
