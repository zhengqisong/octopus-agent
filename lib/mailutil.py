# -*- coding: UTF-8 -*-
#*************************************
#author:zhengqs
#create:201710
#desc:
#**********************************

import smtplib
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.header import Header

sender = 'zhengqisong@sohu.com'
receivers = ['501917150@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

sender = 'zhengqsa@digitalchina.com'
receivers = ['zhengqisong@sohu.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱

# 三个参数：第一个为文本内容，第二个 plain 设置文本格式，第三个 utf-8 设置编码
message = MIMEText('Python 邮件发送测试...', 'plain', 'utf-8')
#message['From'] = Header("菜鸟教程", 'utf-8')
#message['From'] = Header("zhengqisong@digitalchina.com", 'utf-8')
message['From'] = "郑启松<zhengqisong@digitalchina.com>"
message['To'] = "zhengqisong@sohu.com"

subject = '我来测试邮件'
message['Subject'] = Header(subject, 'utf-8')

try:
    smtpObj = smtplib.SMTP('172.16.1.127',25)
    #smtpObj = SMTP_SSL('smtp.qq.com')
    smtpObj.set_debuglevel(1)

    #smtpObj.ehlo('smtp.qq.com')
    #smtpObj.connect('smtp.qq.com')
    #smtpObj.starttls()
    #smtpObj.login("501917150@qq.com", "dsads")
    smtpObj.sendmail(sender, receivers, message.as_string())
    print "邮件发送成功"
except smtplib.SMTPException, ex:
    print "Error: 无法发送邮件", ex
