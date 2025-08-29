from flask import request
from flask import json
from flask_restful import Resource
import mysql.connector
import os
from mysql_connection import get_connection

# 촬영하기 - 이미지 분석 진행 ✖️
class AnalyzeResource(Resource):
    def post(self):
        if 'image[]' not in request.files:
            return 'Image is missing', 404
        images = request.files.getlist("image[]")
        os.makedirs("./image/", exist_ok=True)

        for image in images:
            image_path = "./image/" + image.filename
            image.save(image_path)

        # YOLO 탐지 수행

        # OCR 수행

        # 생성형 AI 실행

        # 응답 데이터 일부 ("YOLO 탐지 + OCR 수행 + 생성형 AI API 실행" 후 출력되는 값) 임의값 설정
        product_name = "product_name_sample"
        expiration_date = "20200101"
        summary = "summary_sample"
        ingredients = "ingredients_sample"

        try :
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            query1 = '''
                        select *
                        from Product
                        where product_name = %s;
                    '''
            record1 = (product_name, )
            cursor.execute(query1, record1)
            result_list = cursor.fetchall()

            if len(result_list) == 0:
                query2 = '''
                        insert into Product (product_name)
                        values (%s);
                        '''
                record2 = (product_name,)
                cursor.execute(query2, record2)
                product_id = cursor.lastrowid
            else:
                result = result_list[0]
                product_id = result['product_id']

            query3 = '''
                    insert into ProductItem (product_id, expiration_date, summary, ingredients)
                    values (%s, %s, %s, %s);
                    '''
            record3 = (product_id, expiration_date, summary, ingredients)
            cursor.execute(query3, record3)
            item_id = cursor.lastrowid
            result_dict = {"item_id" : item_id, "product_name" : product_name, "expiration_date" : expiration_date, "ingredients" : ingredients, "summary" : summary }

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
            "message" : "요청이 성공적으로 처리되었습니다.",
            "data" : result_dict
        }, 200
