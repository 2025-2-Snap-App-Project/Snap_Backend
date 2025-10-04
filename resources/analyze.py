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

# 이미지 파일 형식 체크 함수
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# OCR 수행 함수
def detect_text(path):
    client = vision.ImageAnnotatorClient()
    with open(path, "rb") as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    return texts

# Gemini 실행 함수
def gemini_summary(ingredients):
    genai.configure(api_key="YOUR_API_KEY")
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(f"원재료명을 본 뒤에, 아래 내용을 요약 설명해줘.\n1.제품의 특징 및 주재료\n2.알레르기 유발 성분\n3.주의해야 할 첨가물을 설명해줘.\n\n원재료명 : {ingredients}", stream=True)
    return to_markdown(response.text)

# Markdown 텍스트 표시 함수
def to_markdown(text):
  text = text.replace('•', '  *')
  return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))


# 촬영하기 - 이미지 분석 진행
class AnalyzeResource(Resource):
    def post(self):
        if 'image[]' not in request.files:
                handle_value_error("이미지 누락")
        
        images = request.files.getlist("image[]")
        os.makedirs("./image", exist_ok=True)

        for image in images:
            if image and allowed_file(image.filename):
                img_filename = str(uuid.uuid1()) # 개별 이미지 파일명 설정
                img_path = "./image/" + img_filename + ".png" # 이미지 경로 설정
                image.save(img_path) # 이미지 저장
                ocr_text = detect_text(img_path) # 전체 이미지 OCR 수행

            else:
                handle_media_type_error("지원하지 않는 이미지 형식이 포함되어 있습니다.")

        """
        모델 추론 관련 코드 작성하기
        """

        # OCR 수행 & 모델 추론 이후 출력값 더미 데이터
        product_name = "초코파이" # 제품명
        expiration_date = "20200101" # 소비기한
        ingredients = "밀가루(밀:미국산,호주산), 마시멜로(물엿, 설탕, 젤라틴), 식물성유지(팜유), 설탕, 전란액, 코코아분말, 정제소금, 합성착향료(바닐린), 탄산수소나트륨(팽창제), 밀가루(밀:미국산,호주산), 마시멜로(물엿, 설탕, 젤라틴), 식물성유지(팜유), 설탕, 전란액, 코코아분말, 정제소금, 합성착향료(바닐린), 탄산수소나트륨(팽창제),밀가루(밀:미국산,호주산), 마시멜로(물엿, 설탕, 젤라틴), 식물성유지(팜유), 설탕, 전란액, 코코아분말, 정제소금, 합성착향료(바닐린), 탄산수소나트륨(팽창제)" # 원재료명

        # 생성형 AI 실행
        summary = gemini_summary(ingredients)

       # 생성형 AI API 실행 이후 출력값 더미 데이터 
        summary = "이 제품은 밀가루, 마시멜로, 식물성 유지(팜유), 설탕을 주재료로 사용한 과자류로 보입니다. 특히, 밀가루와 설탕이 가장 많이 함유되어 있으며, 전란액과 코코아분말이 들어 있어 부드러운 식감에 초코 맛이 더해진 형태일 가능성이 높습니다." # 요약 및 정리

        result_dict = {"product_name" : product_name, "expiration_date" : expiration_date, "ingredients" : ingredients, "summary" : summary }

        return {
            "success" : True,
            "status" : 200,
            "message" : "요청이 성공적으로 처리되었습니다.",
            "data" : result_dict
        }, 200
