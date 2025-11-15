# 가상환경 활성화 방법
# 1. cd venv
# 2. cd scripts
# 3. activate.bat

from flask import Flask, request, jsonify
from flask_restful import Api
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
api.add_resource(AnalyzeResource, "/analyze") # 촬영하기 - 이미지 분석 진행

# ----------------------------
# 서버 실행
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
