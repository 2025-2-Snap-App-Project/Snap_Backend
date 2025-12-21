from flask import request
from flask_restful import Resource
import os
import uuid
import json
import re
import tempfile
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
      "ingredients": "원재료명 전체 문자열",
      "summary": [
        "1. 요약 설명",
        "2. 요약 설명",
        "3. 요약 설명",
        "4. 요약 설명",
        "5. 요약 설명",
        "..."
      ]
    }}

    **가장 중요한 규칙 (반드시 지켜야 함):**

    1. 반드시 JSON 형식만 반환하세요. JSON 외 텍스트 금지.
    2. OCR 결과에서 **원재료명(ingredients)을 명확히 식별할 수 있는 경우**
    - summary는 **반드시 원재료명 정보만을 기반으로 작성하세요**
    - 이 경우 **영양정보(열량, 나트륨, 당류 등)는 summary에 절대 포함하지 마세요**
    3. OCR 결과에서 **원재료명 정보를 식별할 수 없는 경우에만**
    - 영양정보를 차선책으로 사용하여 summary를 작성하세요
    4. 원재료명과 영양정보 모두 불분명한 경우
    - summary의 각 항목을 "알 수 없음"으로 작성하세요

    
    **summary 작성 규칙:**

    1. 불필요한 문장은 제거하세요.
    2. 문장 길이가 너무 짧거나 단순 요약이 되지 않도록 하세요.
    4. summary는 리스트 형태여야 합니다.
    5. 각 summary 항목은 반드시 번호로 시작해야 합니다: "1.", "2.", "3." 형태
    6. 각 항목에는 반드시 다음 두 가지를 모두 포함해야 합니다:
    - 해당 **원재료명 또는 영양성분**이 무엇인지에 대한 설명
    - 섭취 시 주의해야 할 점 또는 알레르기·건강상 유의사항
    7. summary 문장은 다음 구조를 따르세요:
    "{'번호'}. {'원재료명 또는 영양성분명'}은(는) {'기능·역할 설명'}에 해당하며, {'섭취 시 주의사항 또는 건강상 유의점'}."
    8. 각 summary 문장은 공백 포함 100~125 byte 길이로 작성하세요.
    9. summary 문장에는 마크다운 강조(**, __ 등)를 사용하지 말고 일반 텍스트만 사용하세요.
    10. 값이 불확실한 경우 "알 수 없음"으로 채우세요.


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
            "ingredients": None,
            "summary": []
        }

# 촬영하기 - 이미지 분석 진행
class AnalyzeResource(Resource):
    def post(self):
        if 'images[]' not in request.files:
                handle_value_error("이미지 누락")
        
        images = request.files.getlist("images[]")
        ocr_texts = [] # OCR 결과 리스트

        with tempfile.TemporaryDirectory() as temp_dir:
            for image in images: # 전송된 모든 이미지에 대해 OCR 수행
                if image and allowed_file(image.filename):
                    img_filename = str(uuid.uuid1()) # 개별 이미지 파일명 설정
                    img_path = temp_dir + "/" + img_filename + ".png" # 이미지 경로 설정
                    image.save(img_path) # 이미지 저장
                    print(img_path) # 이미지 경로 확인

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
