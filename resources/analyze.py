from flask import request
from flask_restful import Resource
import os
import uuid
import json
import re
from google.cloud import vision
import google.generativeai as genai
from error_handler import *
from config import settings

# Google Cloud Vision API 서비스키 연결
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.google_application_credentials

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
def gemini_summary(ocr_text: str):
    genai.configure(api_key=settings.google_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    아래는 식품 라벨 OCR 결과입니다. 불필요한 텍스트가 포함되어 있을 수 있습니다.
    이 텍스트를 분석하여 다음 형식의 JSON만 반환하세요.

    {{
      "product_name": "제품명 (string)",
      "expiration_date": "유통기한 (YYYY.MM.DD 형식)",
      "ingredients": "원재료명 전체 문자열",
      "summary": [
        "1. 원재료명에 대한 요약 설명",
        "2. 원재료명에 대한 요약 설명",
        "3. 원재료명에 대한 요약 설명",
        "4. 원재료명에 대한 요약 설명",
        "5. 원재료명에 대한 요약 설명",
        "..."
      ]
    }}

    **주의사항(모두 필수로 지켜야 함):**

    1. 반드시 JSON 형식만 반환하세요. JSON 외 텍스트 금지.
    2. summary는 리스트 형태여야 합니다.
    3. 요약 설명은 단순한 재료 나열이 아니라, 
    - 알레르기 유발 가능성
    - 첨가물의 기능적 역할
    - 과다 섭취 시 주의점
    - 일반 소비자가 알아두면 좋은 정보
    등의 **해설형 설명**을 포함해야 합니다.
    4. summary의 각 항목은 원재료 하나 또는 한 그룹을 기준으로 작성하고,
    - 공백 포함 **100~125 byte 길이**로 작성하세요.
    - 문장 길이가 너무 짧거나 단순 요약이 되지 않도록 하세요.
    5. summary 각 문단에서 **Markdown 강조는 1~2개 키워드에만 적용**하세요.
    - 강조는 **주요 알레르기 유발 성분**, **식품첨가물**, **원산지**, **특징적인 재료** 등에만 적용합니다.
    - 과도한 강조 금지.
    6. 불필요한 문장은 제거하세요.
    7. 값이 불확실하면 "알 수 없음"으로 채우세요.

    OCR 결과:
    {ocr_text}
    """
    try: # Gemini 응답 생성
        response = model.generate_content(prompt)
        cleaned_txt = re.sub(r"```json|```", "", response.text).strip()
        return json.loads(cleaned_txt)
    except Exception as e: # Gemini 응답 에러 처리
        print("다른 에러:", e)
        return {
            "product_name": None,
            "expiration_date": None,
            "ingredients": None,
            "summary": []
        }

# 촬영하기 - 이미지 분석 진행
class AnalyzeResource(Resource):
    def post(self):
        if 'images[]' not in request.files:
                handle_value_error("이미지 누락")
        
        images = request.files.getlist("images[]")
        os.makedirs("./images", exist_ok=True)

        ocr_texts = [] # OCR 결과 리스트

        for image in images: # 전송된 모든 이미지에 대해 OCR 수행
            if image and allowed_file(image.filename):
                img_filename = str(uuid.uuid1()) # 개별 이미지 파일명 설정
                img_path = "./images/" + img_filename + ".png" # 이미지 경로 설정
                image.save(img_path) # 이미지 저장

                # OCR 수행
                raw_txt = detect_text(img_path)
                ocr_texts.append(raw_txt[0].description) # OCR 결과를 list에 추가

            else:
                handle_media_type_error("지원하지 않는 이미지 형식이 포함되어 있습니다.")

        combined_ocr = "\n".join(ocr_texts) # OCR 결과를 하나로 통합
        print(combined_ocr) # 하나로 통합된 OCR 결과를 로그 출력

        result_dict = gemini_summary(combined_ocr) # Gemini 실행 (하나로 통합된 OCR 결과를 프롬프트로 입력)
        print(result_dict) # Gemini 답변 생성 결과를 로그 출력

        return {
            "success" : True,
            "status" : 200,
            "message" : "요청이 성공적으로 처리되었습니다.",
            "data" : result_dict
        }, 200
