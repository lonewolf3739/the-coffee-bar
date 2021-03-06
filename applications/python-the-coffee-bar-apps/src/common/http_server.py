import json
from flask import Flask, Response, request
import requests

from src.utils.utils import to_json

from opentelemetry import trace
from opentelemetry.util import time_ns


class CustomResponse:
    def __init__(self, code: int = 200, msg: str = None, error: str = None):
        self.code = code
        self.msg = msg
        self.error = error


class EndpointAction:
    def __init__(self, action):
        self.action = action
        self.response = Response(mimetype='application/json')

    def __call__(self, *args, **kwargs):
        data = to_json(request.json)
        result = self.action(data)

        if isinstance(result, requests.models.Response):
            self.response.status_code = result.status_code
            self.response.set_data(result.content)
            try:
                res_json = json.loads(result.content)
                if result.status_code == 402:
                    trace.get_current_span().add_event("exception", {"exception.code": int(result.status_code),
                                                                     "exception.message": res_json['error']},
                                                       time_ns())
            except:
                pass
        else:
            self.response.status_code = result.code
            self.response.set_data(str({'msg': result.msg, 'error': result.error}))

            if result.code == 402:
                trace.get_current_span().add_event("exception", {"exception.code": int(result.code),
                                                                 "exception.message": str(result.error)}, time_ns())

        return self.response


class HttpServer:
    app = None

    def __init__(self, name: str, host: str, port: int):
        self.app = Flask(name)
        self.host = host
        self.port = port

    def run(self):
        self.app.run(host=self.host, port=self.port, debug=True)

    def add_endpoint(self, endpoint: str = None, endpoint_name: str = None, handler: staticmethod = None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=['POST', 'GET', 'HEAD'])
