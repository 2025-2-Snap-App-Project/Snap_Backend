# 400 Bad Request - 필수 파라미터 누락
def handle_value_error(msg):
    return {
        "error_code" : 400,
        "description" : "Bad Request",
        "message" : msg
    }, 400

# 400 Bad Request - mysql 무결성 제약조건 위반
def handle_mysql_integrity_error(e, msg):
    print(e)
    return {
        "error_code" : 400,
        "description" : "Bad Request",
        "message" : f"{msg} : {str(e)}"
    }, 400

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

