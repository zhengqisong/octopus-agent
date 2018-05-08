# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201707
#desc: 
#**********************************

import re

str22 = 'aaa2/2{ { id }}/{{name}}/bbb/{{ id }}'
print str22
print re.findall(r'\{\s*\{\s*(?P<name>.*?)\s*\}\s*\}', str22)

id = "id_value"
print re.sub(r'\{\s*\{\s*id\s*\}\s*\}', id, str22)

name = 'name_value'
print re.sub(r'\{\s*\{\s*name\s*\}\s*\}', name, str22)
#while sz:
#    entity=sz.group()#entityÈ«³Æ£¬Èç>
#    key=sz.group('name')
#    print key
