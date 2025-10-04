# 400 Bad Request - 필수 파라미터 누락
def handle_value_error(msg):
    return {
        "error_code" : 400,
        "description" : "Bad Request",
        "message" : msg
    }, 400

# 415 Unsupported Media Type
def handle_media_type_error(msg):
    return {
        "error_code" : 415,
        "description" : "Unsupported Media Type",
        "message" : msg        
    }, 415

# 500 서버 내부 오류
def server_error(e):
    print(e)
    return {
        "error_code" : 500,
        "description" : e.description,
        "message" : f"서버 내부 오류 : {str(e)}"
    }, 500

