from werkzeug.exceptions import HTTPException
from flask import make_response , jsonify

class NotFoundError(HTTPException):
    def __init__(self, description=None):
        self.description = description
        self.code = 404
        super().__init__()

    def get_response(self, environ=None):
        response = make_response(jsonify(error=self.description), self.code)
        response.content_type = 'application/json'
        return response
