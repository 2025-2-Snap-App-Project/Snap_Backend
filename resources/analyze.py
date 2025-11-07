from flask import request
from flask_restful import Resource
import os
import uuid
from google.cloud import vision
import google.generativeai as genai
from error_handler import *
from config import settings

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

# txt 파일 생성 함수
def create_txt_file(path, ocr_text):
    with open(path, "w") as f:
        f.write(ocr_text[0].description)

# Gemini 실행 함수
def gemini_summary(ingredients):
    genai.configure(api_key=settings.google_api_key)
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content(f"원재료명을 본 뒤에, 아래 내용을 요약 설명해줘.\n1.제품의 특징 및 주재료\n2.알레르기 유발 성분\n3.주의해야 할 첨가물을 설명해줘.\n\n원재료명 : {ingredients}", stream=True)
    return response

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

                # 텍스트 파일 생성
                os.makedirs("./text", exist_ok=True)
                txt_path = "./text/" + img_filename + ".txt" # 텍스트 파일 경로 설정
                create_txt_file(txt_path, ocr_text)

            else:
                handle_media_type_error("지원하지 않는 이미지 형식이 포함되어 있습니다.")

        """
        모델 추론 관련 코드 작성하기
        """

        # OCR 수행 & 모델 추론 이후 출력값 더미 데이터
        product_name = "초코파이" # 제품명
        expiration_date = "2020.01.01" # 소비기한
        ingredients = "밀가루(밀:미국산,호주산), 마시멜로(물엿, 설탕, 젤라틴), 식물성유지(팜유), 설탕, 전란액, 코코아분말, 정제소금, 합성착향료(바닐린), 탄산수소나트륨(팽창제), 밀가루(밀:미국산,호주산), 마시멜로(물엿, 설탕, 젤라틴), 식물성유지(팜유), 설탕, 전란액, 코코아분말, 정제소금, 합성착향료(바닐린), 탄산수소나트륨(팽창제),밀가루(밀:미국산,호주산), 마시멜로(물엿, 설탕, 젤라틴), 식물성유지(팜유), 설탕, 전란액, 코코아분말, 정제소금, 합성착향료(바닐린), 탄산수소나트륨(팽창제)" # 원재료명

        # 생성형 AI 실행
        summary = gemini_summary(ingredients)

       # 생성형 AI API 실행 이후 출력값 더미 데이터 
        summary = [
            "이 제품은 **닭가슴살**을 주재료로 한 가공식품입니다. 전반적으로 단백질이 풍부하지만, **몇 가지 주의할 점**이 있습니다.",
            "1. **대두(콩)**과 **밀**은 대표적인 알레르기 유발 성분입니다.",
            "2. **혼합제제(폴리인산나트륨, 피로인산나트륨)**는 가공식품에서 보존성과 조직감을 높이기 위한 첨가물로, 과도한 섭취 시 신장 건강에 영향을 줄 수 있습니다.",
            "3. **L-글루타민산나트륨(MSG)**는 감칠맛을 내는 조미료로, 일반적으로 안전하지만, 일부 민감한 사람에게는 두통 등을 유발할 수 있습니다.",
        ]

        result_dict = {"product_name" : product_name, "expiration_date" : expiration_date, "ingredients" : ingredients, "summary" : summary }

        return {
            "success" : True,
            "status" : 200,
            "message" : "요청이 성공적으로 처리되었습니다.",
            "data" : result_dict
        }, 200
