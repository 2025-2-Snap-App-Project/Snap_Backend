from flask import request
from flask_restful import Resource
import mysql.connector
from mysql_connection import get_connection

# 촬영하기 - 이미지 분석 진행 ✖️
class AnalyzeResource(Resource):
    def post(self, purchase_id=None):
        data = request.get_json()
