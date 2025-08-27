# run.py
from flask import Flask, request, jsonify
from ultralytics import YOLO
from PIL import Image
import io
import os
from google.cloud import vision
import uuid

# ----------------------------
# Google Cloud Vision API 클라이언트 설정
client = vision.ImageAnnotatorClient()

# ----------------------------
# Flask 앱 생성
app = Flask(__name__)

# ----------------------------
# YOLO 모델 로드
model_path = './yolov8_model/best.pt'  # 로컬 경로
model = YOLO(model_path)

# ----------------------------
# OCR 수행 함수
def ocr_image(image_bytes):
    image = vision.Image(content=image_bytes)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    return ""

# ----------------------------
# 홈 라우트
@app.route('/')
def home():
    return 'YOLO + OCR 서버 실행 중!'

# ----------------------------
# 이미지 분석 API
@app.route('/analyze', methods=['POST'])
def analyze():
    # 요청 검증
    if 'device_id' not in request.form:
        return jsonify({'success': False, 'status': 400, 'message': 'device_id 누락'}), 400
    if 'images' not in request.files:
        return jsonify({'success': False, 'status': 400, 'message': '이미지 파일 누락'}), 400

    device_id = request.form['device_id']
    files = request.files.getlist('images')

    response_data = []

    try:
        for file in files:
            img_bytes = file.read()
            img = Image.open(io.BytesIO(img_bytes))

            # ----------------------------
            # YOLO 추론
            preds = model(img)
            pred_boxes = preds[0].boxes  # Ultralytics YOLOv8 결과 객체

            # 클래스별 bbox 찾기
            roi_dict = {'name': None, 'date': None, 'ingredients': None}
            for box, cls in zip(pred_boxes.xyxy, pred_boxes.cls):
                cls_name = model.names[int(cls)]
                if cls_name in roi_dict:
                    roi_dict[cls_name] = box  # bbox 좌표 저장

            # ----------------------------
            # OCR 수행
            ocr_results = {}
            any_detected = any(roi_dict.values())  # 하나라도 감지되었는지 확인

            if any_detected:
                # 각 클래스 bbox별로 OCR 수행
                for key in ['name', 'date', 'ingredients']:
                    if roi_dict[key] is not None:
                        x1, y1, x2, y2 = map(int, roi_dict[key])
                        cropped_img = img.crop((x1, y1, x2, y2))
                        buffer = io.BytesIO()
                        cropped_img.save(buffer, format='PNG')
                        ocr_results[key] = ocr_image(buffer.getvalue())
                    else:
                        ocr_results[key] = ''
            else:
                # 어떤 클래스도 감지 못했으면 전체 이미지 OCR
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                text = ocr_image(buffer.getvalue())
                ocr_results = {'name': text, 'date': text, 'ingredients': text}

            # ----------------------------
            # 결과 정리
            item_id = str(uuid.uuid4())  # 랜덤 고유 ID
            response_data.append({
                'item_id': item_id,
                'product_name': ocr_results['name'],
                'expiration_date': ocr_results['date'],
                'ingredients': ocr_results['ingredients'],
                'summary': []  # 추후 요약 추가 가능
            })

        return jsonify({
            'success': True,
            'status': 200,
            'message': '요청이 성공적으로 처리되었습니다.',
            'data': response_data
        })

    except Exception as e:
        print(f"Error during prediction/OCR: {str(e)}")
        return jsonify({'success': False, 'status': 500, 'message': str(e)}), 500

# ----------------------------
# 서버 실행
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
