from flask import request, jsonify
from flask import json
from flask_restful import Resource
import mysql.connector
import os
import uuid
from mysql_connection import get_connection
from google.cloud import vision

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 개별 이미지 크롭 > 이미지 저장
def crop_and_save(image, bbox, img_path):
    cropped_img = image.crop(bbox)
    cropped_img.save(img_path)

# OCR 수행 함수
def detect_text(path):
    client = vision.ImageAnnotatorClient()
    with open(client, "rb") as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations


# 촬영하기 - 이미지 분석 진행 ✖️
class AnalyzeResource(Resource):
    def post(self):
        if 'image[]' not in request.files:
                return {
                    "error_code" : 400,
                    "description" : "Bad Request",
                    "message" : "잘못된 요청 (이미지 누락)"
                }, 400
        
        images = request.files.getlist("image[]")
        os.makedirs("./image/original", exist_ok=True)

        # YOLO 탐지 output dummy data
        dummy_yolo_output = [
            {
                "class": "name",
                "class_id": 0,
                "confidence": 0.92,
                "bbox": [50, 40, 400, 100]   # [x_min, y_min, x_max, y_max]
            },
            {
                "class": "ingredients",
                "class_id": 1,
                "confidence": 0.88,
                "bbox": [60, 150, 420, 350]
            },
            {
                "class": "date",
                "class_id": 2,
                "confidence": 0.95,
                "bbox": [70, 480, 250, 520]
            }
        ]
        name_bbox = dummy_yolo_output[0]['bbox'] # 제품명 좌표
        ingredients_bbox = dummy_yolo_output[1]['bbox'] # 원재료명 좌표
        date_bbox = dummy_yolo_output[2]['bbox'] # 소비기한 좌표


        for image in images:
            if image and allowed_file(image.filename):
                image_path = "./image/" + str(uuid.uuid1()) + ".jpg"
                image.save(image_path)
                detect_text(image_path) # OCR 수행
            else:
                return {
                    "error_code" : 415,
                    "description" : "Unsupported Media Type",
                    "message" : f"지원하지 않는 이미지 형식이 포함되어 있습니다."
                }, 400

        # YOLO 탐지 수행

        # 생성형 AI 실행

        # 응답 데이터 일부 ("YOLO 탐지 + OCR 수행 + 생성형 AI API 실행" 후 출력되는 값) 임의값 설정
        # OCR 수행 이후 출력값 더미 데이터
        product_name = "product_name_sample" # OCR 수행 이후 출력값 - 제품명
        expiration_date = "20200101" # OCR 수행 이후 출력값 - 소비기한
        ingredients = "ingredients_sample" # OCR 수행 이후 출력값 - 원재료명
        summary = "summary_sample" # 원재료명 값을 생성형 AI에 입력으로 넣어서 출력된 값 - 요약

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
            "message" : "요청이 성공적으로 처리되었습니다.",
            "data" : result_dict
        }, 200
