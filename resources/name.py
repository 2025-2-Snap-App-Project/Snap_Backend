from flask import request
from flask_restful import Resource
import os
import uuid
from google.cloud import vision
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
    return texts[0].descriptions

# 촬영하기 - 제품명 안내
class ProductNameResource(Resource):
    def post(self):
        if 'image' not in request.files:
            handle_value_error("이미지 누락")
        image = request.files.get("image")
        os.makedirs("./name", exist_ok=True)

        if image and allowed_file(image.filename):
            img_filename = str(uuid.uuid1()) # 개별 이미지 파일명 설정
            img_path = "./name/" + img_filename + ".png" # 이미지 경로 설정
            image.save(img_path) # 이미지 저장

            # OCR 수행
            ocr_result = detect_text(img_path)
        else:
            handle_media_type_error("지원하지 않는 이미지 형식이 포함되어 있습니다.")

        print(ocr_result) # OCR 결과 출력

        return {
            "success" : True,
            "status" : 200,
            "message" : "요청이 성공적으로 처리되었습니다.",
            "product_name" : ocr_result
        }, 200

