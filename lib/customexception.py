#!/usr/bin/python
# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201508
#desc: 
#*************************************


class CustomIOException(Exception):
    pass

class CustomNotFoundException(Exception):
    pass
    
class CustomLoadException(Exception):
    pass
    
class CustomParseException(Exception):
    pass

class CustomReqTimeoutException(Exception):
    pass

class CustomAuthException(Exception):
    pass

class CustomExecException(Exception):
    pass