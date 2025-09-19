# 400 Bad Request - 필수 파라미터 누락
def handle_value_error(data, required_fields):
    for field in required_fields:
        if field not in data:
            return {
                "error_code" : 400,
                "description" : "Bad Request",
                "message" : f"{field} 누락"
            }, 400

# 400 Bad Request - mysql 무결성 제약조건 위반
def handle_mysql_integrity_error(e):
    print(e)
    return {
        "error_code" : 400,
        "description" : "Bad Request",
        "message" : f"데이터 무결성 제약조건 위반 : {str(e)}"
    }, 400

# 415 Unsupported Media Type
def handle_media_type_error(msg):
    return {
        "error_code" : 415,
        "description" : "Unsupported Media Type",
        "message" : msg        
    }, 415

# 404 Not Found
def handle_not_found_error(msg):
    return {
    "error_code": 404,
    "description": "Not Found",
    "message": msg
}, 404

# 503 MySQL connector 에러
def handle_mysql_connect_error(e):
    print(e)
    return {
    "error_code" : 503,
    "description" : e.description,
    "message" : f"MySQL connector 에러 : {str(e)}"
}, 503 # HTTPStatus.SERVICE_UNAVAILABLE

# 500 서버 내부 오류
def server_error(e):
    print(e)
    return {
        "error_code" : 500,
        "description" : e.description,
        "message" : f"서버 내부 오류 : {str(e)}"
    }, 500

