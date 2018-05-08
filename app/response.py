# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201708
#desc: 
#**********************************

from flask import make_response, jsonify

class Response:
    
    def __init__(self):
        pass
    
    @staticmethod
    def make_json_response(message, headers = None, status_code = 0, success=True, code=0):
        _res = 'success'
        if success!=True:
          _res = 'error' 
        data = {'res':_res,'code':code,'message':message}
        res = make_response(jsonify(data))
        res.mimetype = 'text/json'
        res.headers = headers
        res.status_code == status_code
        return res
        