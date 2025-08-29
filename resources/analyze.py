from flask import request
from flask_restful import Resource
import mysql.connector
import os
from mysql_connection import get_connection

# 촬영하기 - 이미지 분석 진행 ✖️
class AnalyzeResource(Resource):
    def post(self):
        if 'image[]' not in request.files:
            return 'Image is missing', 404
        device_id = request.form['device_id']
        images = request.files.getlist("image[]")
        os.makedirs("./image/", exist_ok=True)

        for image in images:
            image_path = "./image/" + image.filename
            image.save(image_path)

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
            "message" : "이미지 업로드 성공",
            "data" : ""
        }, 200
