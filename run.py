# .\venv\Scripts\activate 로 venv 활성화
from flask import Flask, request, jsonify
from flask_restful import Api
from resources.user import UserResource
from resources.product import ProductsResource
from resources.date import DateResource
from resources.analyze import AnalyzeResource

from ultralytics import YOLO
from PIL import Image
import io
import os
from google.cloud import vision
import uuid

# ----------------------------
# Flask 앱 생성
app = Flask(__name__)

# restfulAPI 생성
api = Api(app)
api.add_resource(UserResource, '/user') # 로그인, 회원 탈퇴
api.add_resource(AnalyzeResource, "/analyze", "/analyze/<string:purchase_id>") # 촬영하기 - 이미지 분석 진행
api.add_resource(ProductsResource, '/products/<string:purchase_id>') # 촬영하기 - 제품 보관하기
api.add_resource(DateResource, "/date", "/date/<string:purchase_id>") # 소비기한 메뉴

# ----------------------------
# 서버 실행
if __name__ == '__main__':
    app.run()
