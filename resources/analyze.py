from flask import request, jsonify
from flask import json
from flask_restful import Resource
import os
import uuid
from google.cloud import vision
import pathlib
import textwrap

import google.generativeai as genai

from IPython.display import display
from IPython.display import Markdown
from error_handler import *

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "./파일명.json"

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
    return response.text_annotations

# Markdown 텍스트 표시 함수
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# 촬영하기 - 이미지 분석 진행 ✖️
class AnalyzeResource(Resource):
    def post(self):
        if 'image[]' not in request.files:
                handle_value_error("이미지 누락")
        
        images = request.files.getlist("image[]")
        os.makedirs("./image/original", exist_ok=True)
        os.makedirs("./image/name/", exist_ok=True)
        os.makedirs("./image/ingredients/", exist_ok=True)
        os.makedirs("./image/date/", exist_ok=True)

        # 이미지 크롭 > 이미지 저장 > OCR 수행
        for image in images:
            if image and allowed_file(image.filename):
                img_filename = str(uuid.uuid1()) # 개별 이미지 파일명 설정
                name_path = "./cropped/name/" + img_filename + ".jpg"
                ingredients_path = "./cropped/ingredients/" + img_filename + ".jpg"
                date_path = "./cropped/date/" + img_filename + ".jpg"

                # 개별 bbox 이미지 크롭 > 크롭된 이미지 저장
                crop_and_save(image, name_bbox, name_path) # 제품명
                crop_and_save(image, ingredients_bbox, ingredients_path) # 원재료명
                crop_and_save(image, date_bbox, img_filename) # 소비기한

                # OCR 수행 > 출력값을 개별 변수에 저장
                product_name = detect_text(name_path) # 제품명
                ingredients = detect_text(ingredients_path) # 원재료명
                expiration_date = detect_text(date_path) # 소비기한

            else:
                handle_media_type_error("지원하지 않는 이미지 형식이 포함되어 있습니다.")

        # 생성형 AI 실행
        genai.configure(api_key="YOUR_API_KEY")
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(f"원재료명을 본 뒤에, 아래 내용을 요약 설명해줘.\n1.제품의 특징 및 주재료\n2.알레르기 유발 성분\n3.주의해야 할 첨가물을 설명해줘.\n\n원재료명 : {ingredients}", stream=True)
        summary = to_markdown(response.text)

        # 응답 데이터 일부 ("YOLO 탐지 + OCR 수행 + 생성형 AI API 실행" 후 출력되는 값) 임의값 설정
        # OCR 수행 & 생성형 AI API 실행 이후 출력값 더미 데이터
        product_name = "product_name_sample" # OCR 수행 이후 출력값 - 제품명
        expiration_date = "20200101" # OCR 수행 이후 출력값 - 소비기한
        ingredients = "ingredients_sample" # OCR 수행 이후 출력값 - 원재료명
        summary = "summary_sample" # 원재료명 값을 생성형 AI에 입력으로 넣어서 출력된 값 - 요약

        result_dict = {"product_name" : product_name, "expiration_date" : expiration_date, "ingredients" : ingredients, "summary" : summary }
        return {
            "success" : True,
            "status" : 200,
            "message" : "요청이 성공적으로 처리되었습니다.",
            "data" : result_dict
        }, 200
