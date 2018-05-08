# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

from flask import Blueprint

test=Blueprint('test',
        __name__,
        #template_folder='/opt/auras/templates/',   #指定模板路径
         #static_folder='/opt/auras/flask_bootstrap/static/',#指定静态文件路径
      )
  
#import views
from app.test import views
