# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

from flask import request, g, make_response, jsonify, redirect
from app.test import test
from authentication import session_require

tasks = [
    {
        'id': 1,
        'title': u'Buy groceries',
        'description': u'Milk, Cheese, Pizza, Fruit, Tylenol', 
        'done': False
    },
    {
        'id': 2,
        'title': u'Learn Python',
        'description': u'Need to find a good Python tutorial on the web', 
        'done': False
    }
]

@test.route('/')              #指定路由为/，因为run.py中指定了前缀，浏览器访问时，路径为http://IP/asset/
@test.route('')
@session_require
def index(): 
    print "dsadsadadsadsadsad, username: " + g.username
    #return jsonify({'tasks': tasks,'args':request.args,'data':request.data,'form':request.form})
    res = make_response(jsonify({'tasks': tasks,'args':request.args,'data':request.data,'form':request.form}))
    res.mimetype = 'text/plain'
    res.headers['x-tag'] = 'sth.magic'
    res.set_cookie('user','JJJJJohnny')
    res.status_code == 0
    return res