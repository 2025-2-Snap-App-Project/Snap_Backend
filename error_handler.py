from werkzeug.exceptions import HTTPException, _aborter, default_exceptions
from flask import jsonify

def error_app(app):
    def error_handling(error):
        if isinstance(error, HTTPException):
            result = {
                "error_code" : error.code,
                "description" : error.description,
                "message" : str(error)
            }

        else:
            description_500 = _aborter.mapping[500].description
            result = {
                "error_code" : 500,
                "description" : description_500,
                "message" : str(error)
            }

        res = jsonify(result)
        res.status_code = result['error_code']
        return res
    
    for code in default_exceptions.keys():
        app.register_error_handler(code, error_handling)

    return app
