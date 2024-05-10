from flask import request
import time,requests,json
from lib.mysqldb import MysqlDB
# from  importlib import import_module


def _getDatetimeStr():
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())

def _getDateInt():
    return int(time.time())

def _getTimeStr():
    return time.strftime('%Y-%m-%d', time.localtime())


def _getRequestParams(param_list, type='form', filter=True, exclude=[]):
    page = request.args.get('page', 1)
    pagenum = request.args.get('perPage', 10)

    request_param = {}
    request_param['page'] = int(page)
    request_param['pagenum'] = int(pagenum)

    # .-@:
    bad_word = ["\"", "\\", "'", "=", "#", ";", "<", ">", "%", "$", "(", ")", "&", "!", "~", '^', '*', '/', '+']

    if type == 'form':
        if param_list:
            for i in param_list:
                if request.method == 'POST':
                    tmp = request.form.get(i, '').strip()

                    if tmp == '':
                        tmp = request.args.get(i, '').strip()

                if request.method == 'GET':
                    tmp = request.args.get(i, '').strip()

                for j in bad_word:

                    if exclude and i in exclude:
                        continue

                    tmp = tmp.replace(j, '')

                request_param[i] = tmp

    if type == 'json' and filter == True:
        tmp = json.loads(request.get_data(as_text=True))
        print(tmp)
        for k, v in tmp.items():
            if isinstance(v, dict):
                request_param[k] = v
            else:
                v = str(v).strip()

                if k not in exclude:
                    for j in bad_word:
                        v = v.replace(j, '')

                request_param[k] = v
    if type == 'json' and filter == False:
        tmp = json.loads(request.get_data(as_text=True))

        for k, v in tmp.items():
            if isinstance(v, str):
                request_param[k] = v.replace("'", '"')
            else:
                request_param[k] = v

    return request_param






def getTodayStamp():
    timestr = time.strftime('%Y-%m-%d', time.localtime())+' 00:00:00'
    timeArray = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # 转换为时间戳
    timeStamp = int(time.mktime(timeArray))
    return timeStamp

def _dateStrToInt(timestr):
    timeArray = time.strptime(timestr, "%Y-%m-%d %H:%M:%S")
    # 转换为时间戳
    timeStamp = int(time.mktime(timeArray))
    return timeStamp


