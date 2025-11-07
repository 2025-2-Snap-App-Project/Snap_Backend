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
        "원재료명에 대한 요약 설명 1",
        "원재료명에 대한 요약 설명 2",
        "원재료명에 대한 요약 설명 3",
        "원재료명에 대한 요약 설명 4",
        "원재료명에 대한 요약 설명 5",
        "..."
      ]
    }}

    **주의사항:**
    - 반드시 JSON 형식만 반환하세요 (텍스트나 설명 절대 금지)
    - summary는 리스트 형태여야 합니다.
    - 불필요한 문장은 제거하세요.
    - 값이 불확실하면 "알 수 없음"으로 채우세요.
    - summary 문장을 작성할 때 **주요 원재료, 원산지, 첨가물 등 중요한 키워드에는 반드시 `**`를 붙여 강조**하세요. 예시: "주재료는 **미국산/호주산 밀**을 사용한 밀가루입니다."

    OCR 결과:
    {ocr_text}
    """
    try: # Gemini 응답 생성
        response = model.generate_content(prompt)
        cleaned_txt = re.sub(r"```json|```", "", response.text).strip()
        print(cleaned_txt)
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

        for image in images:
            if image and allowed_file(image.filename):
                img_filename = str(uuid.uuid1()) # 개별 이미지 파일명 설정
                img_path = "./images/" + img_filename + ".png" # 이미지 경로 설정
                image.save(img_path) # 이미지 저장
                ocr_text = detect_text(img_path) # 전체 이미지 OCR 수행
                print(ocr_text[0].description) # OCR 수행 결과 로그로 출력

            else:
                handle_media_type_error("지원하지 않는 이미지 형식이 포함되어 있습니다.")

        # OCR 수행 이후 출력값 더미 데이터
        dummy_txt = """
        초코파이, 2020.01.01, 밀가루(밀:미국산,호주산), 마시멜로(물엿, 설탕, 젤라틴), 식물성유지(팜유), 설탕, 전란액, 코코아분말,
        정제소금, 합성착향료(바닐린), 탄산수소나트륨(팽창제)
        """

        # 생성형 AI 실행
        result_dict = gemini_summary(dummy_txt)
        return {
            "success" : True,
            "status" : 200,
            "message" : "요청이 성공적으로 처리되었습니다.",
            "data" : result_dict
        }, 200
