import json
from functools import wraps
from flask import Blueprint, render_template, session, request, redirect
from lib.common import _getRequestParams, _getDatetimeStr, _getDateInt,   getTodayStamp
from lib.mysqldb import MysqlDB
from conf.config import Config

cloud = Blueprint('cloud', __name__)


# 验证是否登陆
def isLogin(func):
    @wraps(func)
    def inner(*args, **kwargs):
        print(session.get('auth'))
        if session.get('auth'):
            ret = func(*args, **kwargs)
            return ret
        else:
            return redirect('/login')

    return inner


@cloud.route('/logout', methods=['GET', 'POST'])
@isLogin
def logout():
    session['auth'] = ''
    return redirect('/login')


@cloud.route('/', methods=['GET', 'POST'])
def main():
    return redirect('/login')


@cloud.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if session.get('auth'):
            return redirect('/account_list')

        if request.method == 'POST':
            param = ['username', 'password']
            req_param = _getRequestParams(param, 'json', True, ['password'])
            print(req_param)
            if 'username' in req_param and 'password' in req_param:

                if req_param['username'] == Config.user and req_param['password'] == Config.passwd:
                    session['auth'] = "hello"
                    # redirect('/index')
                    return json.dumps({"status": 0, 'msg': '登录成功', "data": ""})
                else:
                    # return return_error_msg('账户密码错误')
                    return json.dumps({'message': '账户或者密码错误', 'status': 100})

            else:
                # return return_error_msg('请将数据填写完整')
                return json.dumps({'message': '请将数据填写完整', 'status': 100})

        if request.method == 'GET':
            return render_template('cloud/user_login.html')

    except Exception as e:
        print(str(e))
        # print('login_user is error :%s' % (traceback.print_exc()))
        return json.dumps({'message': '请联系管理员', 'status': 100})


@cloud.route('/ip_list', methods=['GET'])
@isLogin
def account_list():
    return render_template('cloud/ip_list.json')


@cloud.route('/ip_list_api', methods=['GET'])
@isLogin
def ip_list_api():
    param = ['ip']
    req_param = _getRequestParams(param)
    page = req_param['page']
    pagenum = req_param['pagenum']

    where = []
    if req_param['ip']:
        where.append("ip like '%" + req_param['accountName'] + "%'")
    
    if where:
        where = 'where ' + ' and '.join(where)
    else:
        where = ''

    sql = "select ip,status,create_time,id from asset_ip  %s  limit %s,%s" % (
        where, str((int(page) - 1) * pagenum), str(pagenum))
    print(sql)
    res = MysqlDB().query(sql)
    

    sql = "select count(*) as num from asset_ip  %s  " % (where)
    rows = MysqlDB().query(sql)
    data = {
        'status': 0,
        "data": {
            "rows": res,
            "count": rows[0]['num']
        },
    }
    return json.dumps(data)



@cloud.route('/index', methods=['GET'])
@isLogin
def index():
    return render_template('index/index.html')

#添加新ip
@cloud.route('/ip_add', methods=['POST'])
@isLogin
def ip_add():
    param = ['ip']
    req_param = _getRequestParams(param)

    sql = """
    insert into asset_ip(ip,create_time,create_date)
    values('%s','%s','%s')
    """ % (req_param['ip'], _getDateInt(), _getDatetimeStr())
    # print(sql)

    try:
        num = MysqlDB().execute(sql)
        if num > 0:
            data = {"status": 0, "msg": "添加成功"}
        else:
            data = {"status": 100, "msg": "添加失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)})


@cloud.route('/ip_edit', methods=['POST'])
@isLogin
def account_edit():
    param = ['ip',  'id']
    req_param = _getRequestParams(param)

    sql = """
    update asset_ip set ip='%s',update_time='%s',update_date='%s' where id=%s
    """ % (req_param['ip'],  _getDateInt(), _getDatetimeStr(), req_param['id'])

    try:
        num = MysqlDB().execute(sql)
        if num > 0:
            data = {"status": 0, "msg": "更新成功"}
        else:
            data = {"status": 100, "msg": "更新失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)})


@cloud.route('/stopall', methods=['POST'])
@isLogin
def stopall():
    param = ['ids']
    req_param = _getRequestParams(param,'json')

    sql = "update asset_ip set status=-1 where id in (%s)" % (req_param['ids'])
    num = MysqlDB().execute(sql)
    try:
        if num > 0:
            data = {"status": 0, "msg": "批量停用成功"}
        else:
            data = {"status": 100, "msg": "批量停用失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)}) 

@cloud.route('/startall', methods=['POST'])
@isLogin
def startall():
    param = ['ids']
    req_param = _getRequestParams(param,'json')

    sql = "update asset_ip set status=1 where id in (%s)" % (req_param['ids'])
    num = MysqlDB().execute(sql)
    try:
        if num > 0:
            data = {"status": 0, "msg": "批量启用成功"}
        else:
            data = {"status": 100, "msg": "批量启用失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)}) 

@cloud.route('/delall', methods=['POST'])
@isLogin
def delall():
    param = ['ids']
    req_param = _getRequestParams(param,'json')
    sql = "delete from asset_ip where id in (%s)" % (req_param['ids'])
    num = MysqlDB().execute(sql)
    try:
        if num > 0:
            data = {"status": 0, "msg": "批量移除成功"}
        else:
            data = {"status": 100, "msg": "批量移除失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)}) 

@cloud.route('/ip_stop', methods=['GET'])
@isLogin
def ip_stop():
    param = ['id']
    req_param = _getRequestParams(param)

    sql = "update asset_ip set status=-1 where id=%s" % (req_param['id'])
    num = MysqlDB().execute(sql)
    try:
        if num > 0:
            data = {"status": 0, "msg": "停用成功"}
        else:
            data = {"status": 100, "msg": "停用失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)})

@cloud.route('/ip_del', methods=['GET'])
@isLogin
def ip_del():
    param = ['id']
    req_param = _getRequestParams(param)
    try:
        sql = "delete  from asset_ip where id=%s" % (req_param['id'])
        num = MysqlDB().execute(sql)
        if num > 0:
            data = {"status": 0, "msg": "移除成功"}
        else:
            data = {"status": 100, "msg": "停用失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)})


@cloud.route('/ip_start', methods=['GET'])
@isLogin
def ip_start():
    param = ['id']
    req_param = _getRequestParams(param)
    try:
        sql = "update asset_ip set status=1 where id=%s" % (req_param['id'])
        num = MysqlDB().execute(sql)
        if num > 0:
            data = {"status": 0, "msg": "启用成功"}
        else:
            data = {"status": 100, "msg": "启用失败"}
        return json.dumps(data)
    except Exception as e:
        return json.dumps({"status":100,'msg':str(e)})




@cloud.route('/port_options', methods=['GET'])
@isLogin
def port_options():
    param = ['type']
    req_param = _getRequestParams(param)
    sql = "select  distinct %s from ip_port " % (req_param['type'])
    res = MysqlDB().query(sql)
    app = []
    for i in res:
        app.append({"label": i[req_param['type']], "value": i[req_param['type']]})
    return json.dumps(app)





@cloud.route('/port', methods=['GET'])
@isLogin
def port():
    return render_template('cloud/port.json')


@cloud.route('/port_list', methods=['GET'])
@isLogin
def port_list():
    param = ['ip', 'port', 'service', 'product', 'version','status']
    req_param = _getRequestParams(param)
    page = req_param['page']
    pagenum = req_param['pagenum']

    where = []
    if req_param['ip']:
        where.append("ip like '%" + req_param['ip'] + "%'")
    if req_param['port']:
        where.append("port like '%" + req_param['port'] + "%'")
    if req_param['service']:
        where.append("service ='" + req_param['service'] + "'")
    if req_param['status']:
        where.append("status ='" + req_param['status'] + "'")
    if req_param['product']:
        where.append("product like '%" + req_param['product'] + "%'")
    if req_param['version']:
        where.append("version like '%" + req_param['version'] + "%'")
    if where:
        where = 'where ' + ' and '.join(where)
    else:
        where = ''

    sql = "  select ip,port,service,port,version,status,create_time,update_time,product from ip_port   %s  limit %s,%s" % (
    where, str((int(page) - 1) * pagenum), str(pagenum))
    print(sql)
    res = MysqlDB().query(sql)

    for i in res:
        idx = res.index(i)
        res[idx]['remark'] = '-'
        if i['update_time'] and i['update_time'] < getTodayStamp():
            res[idx]['remark'] = '未巡检出'

    sql = "select count(*) as num from ip_port  %s  " % (where)
    rows = MysqlDB().query(sql)
    data = {
        'status': 0,
        "data": {
            "rows": res,
            "count": rows[0]['num']
        },
    }
    return json.dumps(data)



@cloud.route('/menu', methods=['GET'])
@isLogin
def menu():
    return {
        "status": 0,
        "msg": "",
        "data": {
            "pages": [
                {"label": "", "icon": 'fa fa-cube', "children": [
                    {
                        "label": "IP管理",
                        "icon": "fa fa-address-book",
                        "children": [
                            {
                                "label": "IP列表",
                                "url": "/ip_list",
                                "schemaApi": "get:/ip_list"
                            }
                        ]
                    },
                    {
                        "label": "端口管理",
                        "icon": "fa fa-address-book",
                        "children": [
                            {
                                "label": "端口列表",
                                "url": "/port",
                                "icon": "",
                                "schemaApi": "get:/port"

                            },

                        ]
                    }
                ]},
                {"url": "/", "redirect": "/ip_list"}
            ]
        }
    }
