from flask import request
from flask_restful import Resource
import mysql.connector
import os
from mysql_connection import get_connection

# 촬영하기 - 이미지 분석 진행 ✖️
class AnalyzeResource(Resource):
    def post(self):
        if 'image' not in request.files:
            return 'Image is missing', 404
        device_id = request.form['device_id']
        image = request.files['image']
        image_path = "./image/" + image.filename
        image.save(image_path)

        product_id = "product_id_sample"
        product_name = "product_name_sample"
        item_id = "item_id_sample"
        expiration_date = "expiration_date_sample"
        summary = "summary_sample"
        ingredients = "ingredients_sample"

        # try :
        #     connection = get_connection()
        #     query = '''
        #             '''
        #     record = (product_id, product_name)
        #     cursor = connection.cursor()
        #     cursor.execute(query, record)
        #     connection.commit()
        #     cursor.close()
        #     connection.close()

        # except mysql.connector.Error as e :
        #     print(e)
        #     cursor.close()
        #     connection.close()
        #     return {"error" : str(e)}, 503 #HTTPStatus.SERVICE_UNAVAILABLE
 
        return{
            "success" : True,
            "status" : 200,
            "message" : "이미지 업로드 성공",
            "data" : ""
        }, 200
