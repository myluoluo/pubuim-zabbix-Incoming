#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Powered by myluoluo
import os,sys,smtplib,requests,MySQLdb,codecs

to          =   sys.argv[1]
subject     =   sys.argv[2]
body        =   sys.argv[3]
servicesUrl =   'https://hooks.pubu.im/services/' + to

# Zabbix 数据库连接信息
mysql_server=   "127.0.0.1"
mysql_user  =   "zabbix"
mysql_pass  =   "xxxxx"
db_name     =   "zabbix"

# Zabbix 后台地址以及登录信息
zabbix_url  =   "http://zabbix.moe/"
zabbix_user =   "admin"
zabbix_pass =   "xxxxx"

# 放在 Web 目录，使其可被零信访问
#   若非 Root 运行，可能需要设定文件夹所属：
#       chown zabbix:zabbix /home/wwwroot/default/zabbix-graph/
image_path  =   "/home/wwwroot/default/zabbix-graph/" + os.popen('date +%Y%m').read().rstrip() + "/"
image_url   =   "http://zabbix.moe/zabbix-graph/" + os.popen('date +%Y%m').read().rstrip() + "/"
stime       =   os.popen('date +%Y%m%d%H%M%S').read().rstrip()
period      =   3600 # 秒
cookie      =   "/tmp/cookie"
width       =   1222

# 获取报警级别（相对于零信）
def getLevel(body):
    tmp = body.split('Trigger severity: ')
    if any(tmp) != True:
        return "info"

    level = tmp[1].split('\n')[0].strip()
    if level == 'Warning':
        return 'warning'

    if level == 'Information':
        return 'info'

    if level == 'Average':
        return 'error'

    return 'info';


# 事件详细信息地址
def getEvent(body):
    tmp = body.split('Original event ID: ')
    if any(tmp) != True:
        return ""
    eventId = tmp[1].split('\n')[0].strip()
    sql = "select objectid from events where eventid=%s" % (eventId)
    db = MySQLdb.connect(mysql_server, mysql_user, mysql_pass, db_name) 
    cursor = db.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    if any(results):
        db.close()
        return str(results[0][0]), str(eventId)

    return "", ""
    

# 通过ITEM ID查询图表
def getGraphId(body):
    # 获得ITEM ID
    itemId = body.split("ITEM ID: ")[1]
    db = MySQLdb.connect(mysql_server, mysql_user, mysql_pass, db_name) 
    cursor = db.cursor()
    sql = "select graphs_items.graphid, graphs.graphtype from graphs_items,graphs where graphs_items.itemid=%s and graphs_items.graphid = graphs.graphid limit 1;" % (itemId)
    cursor.execute(sql)
    results = cursor.fetchall()
    # 存在关联的图表
    if any(results):
        db.close()
        return int(results[0][0]), results[0][1], 1

    # 不存在关联图表
    return int(itemId), 0, 0

def main(to, subject, body):
    itemId = int(body.split("ITEM ID: ")[1])
    level = getLevel(body)
    print("level: " + level)
    triggerid, eventId = getEvent(body)
    
    if itemId > 0:
        graphid, type, flag = getGraphId(body)
        os.popen("""mkdir -p %s""" % (image_path))
        os.popen("""curl -c '%s' -b '%s' -d "request=&name=%s&password=%s&autologin=1&enter=Sign+in" %s/index.php""" % (cookie, cookie, zabbix_user, zabbix_pass, zabbix_url))
        # 存在关联的图表
        if flag > 0:
            print("存在关联的图表: " + str(graphid))
            zabbixUrl = zabbix_url + "/charts.php?graphid=" + str(graphid)
            os.popen("""curl -b '%s' -F "graphid=%d" -F "period=%d" -F "stime=%s" -F "width=%d" %s > %s%s.png""" % (cookie, graphid, period, stime, width, zabbix_url + "/chart2.php", image_path, stime))
        # 不存在关联图表，仅有独立item
        else:
            print("不存在关联图表")
            zabbixUrl = zabbix_url + "/history.php?action=showgraph&itemids[0]=" + body.split("ITEM ID: ")[1]
            os.popen("""curl -b '%s' -F "itemids[0]=%s" -F "period=%d" -F "stime=%s" -F "width=%d" %s > %s%s.png""" % (cookie, graphid, period, stime, width, zabbix_url + "/chart.php", image_path, stime))

        values = {
            "text": subject + "\r\n" + body, 
            "displayUser": {
                "name": "Zabbix", 
                "avatarUrl": "https://up.521.moe/zabbix-logo.png"
            }, 
            "attachments": [
                {
                    "title": subject, 
                    "url": zabbixUrl,
                    "color": level
                },
                {
                    "title": "查看事件详细信息", 
                    "url": zabbix_url + """/tr_events.php?triggerid=%s&eventid=%s""" % (triggerid, eventId) ,
                    "color": level
                },
                {
                    "photoUrl": image_url + str(stime) + ".png",
                    "color": level
                }
            ],
            "buttons": [
                {
                    "text": "滚去确认警报 _(:з」∠)_",
                    "url": zabbix_url + "/zabbix.php?action=acknowledge.edit&eventids[]=%s" % (eventId)
                }
            ]
        }
        # 发送到零信
        return requests.post(servicesUrl, json = values).text

    # 没有ITEM ID，仅发送信息
    values = {"text": subject + "\r\n" + body, "displayUser": {"name": "Zabbix", "avatarUrl": "https://up.521.moe/zabbix-logo.png"}}
    return requests.post(servicesUrl, json = values).text
 
if __name__ == "__main__":
    # xenbr0 等同于 eth0 避免重复 (XenServer)
    if "xenbr" in subject:
        exit
    res = main(to, subject, body)
