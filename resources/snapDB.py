from flask import request
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection

class UserResource(Resource) :
    # 로그인 ✅
    def post(self) :
        data = request.get_json()
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
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE
 
        return {"result" : "success"}, 200
    
    # 회원 탈퇴 ✅
    def delete(self) :
        data = request.get_json()
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
            cursor.close()
            connection.close()
 
        except mysql.connector.Error as e :
            print(e)
            cursor.close()
            connection.close()
            return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE
 
        return {"result" : "success"}, 200

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
            record = (data['purchase_id'], data['device_id'], data['storage_location'], False)
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
 
        return {"result" : "success"}, 200
    
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

                expirateion_date = result.get('expiration_date')
                if expirateion_date:
                    result['expiration_date'] = expirateion_date.strftime("%Y.%m.%d")

                summary_str = result.get('summary')
                if summary_str:
                    summary_list = []
                    for s in summary_str.split('.'):
                        s = s.strip()
                        if s != '':
                            summary_list.append(s)
                    result['summary'] = summary_list
                
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
                "date" : result
            }, 200

        # 소비기한 - 소비기한 리스트 조회 ✖️
        else:
            return
    
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
    
            return {"result" : "success"}, 200
        
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
    
            return {"result" : "success"}, 200
    
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
 
        return {"result" : "success"}, 200

# 촬영하기 - 이미지 분석 진행 ✖️
class AnalyzeResource(Resource):
    def post(self, purchase_id=None):
        data = request.get_json()
