
import os,pathlib,time,json,nmap,threadpool,sys
sys.path.append('../../')
from lib.common import _getTimeStr,_getDatetimeStr,_getDateInt
from lib.mysqldb import MysqlDB
from conf.config import Config
from lib.log import Log

class scanBase:
    name = 'scan'
    logger = ''

    def existFile(self,filename):
        if os.path.exists(filename):
            return True
        else:
            time.sleep(5)

    def __init__(self):
        self.logger = Log( self.name ,self.name)

        print('----'+_getDatetimeStr()+' Nmap/Masscan开始巡检----')
        self.logger.save('----'+_getDatetimeStr()+' Nmap/Masscan开始巡检----')

    def start(self):
        #从数据库里读取出来
        sql =  '''
        SELECT
            ip 
        FROM
            asset_ip ca
            
        WHERE
            ca.status = 1 
        '''
        res = MysqlDB().query(sql)

        if res:
            self.ip = []
            for i in res:
               self.ip.append( i['ip'] )
            #self.ip = res['public_ips'].split(',')

            mscanDir = Config.LOG_DIR + '/scan/masscan/' + _getTimeStr()
            nmapDir  = Config.LOG_DIR + '/scan/nmap/'    + _getTimeStr()
            
            if not os.path.exists(nmapDir):
                print('-目录不存在:'+ nmapDir)
                os.makedirs(nmapDir)

            if not os.path.exists(mscanDir):
                print('-目录不存在:'+ mscanDir)
                os.makedirs(mscanDir)

            param = []
            for i in self.ip:
                mscanFile = mscanDir+'/'+i.replace('.','_')+'.json'
                nscanFile = nmapDir+'/' +i.replace('.','_')+'.json'

                if not os.path.exists(mscanFile):
                    print('-文件不存在:'+mscanFile)
                    pathlib.Path(mscanFile).touch()

                param.append( [i,mscanFile,nscanFile] )

            try:
                pool = threadpool.ThreadPool(4)
                reqs = threadpool.makeRequests(self.executeStr,param )
                [pool.putRequest(req) for req  in reqs]
                pool.wait()
            except Exception as e:
                print(e)

        else:
            print('扫描目标不存在')

        self.expire()

    def executeStr(self,param):
        ip = param[0]
        mscanFile = param[1]
        nscanFile = param[2]
        cmd_str = '  '+Config.SCAN_DIR + "/tools/masscan %s -p1-65535 --rate=2000 --retries=1 --wait=20 -oJ %s"%(ip,mscanFile)
        print(cmd_str)
        os.system(cmd_str)
        print(ip)

        if self.existFile(mscanFile):
            if os.path.getsize(mscanFile) > 0:
                with open(mscanFile,'r') as f:
                    res = json.loads(f.read())

                postlist = ''
                for i in res:
                    port = str(i['ports'][0]['port'])
                    postlist += port+','
                print(postlist)

                print('开始Nmap扫描 ip:'+ip+',port:'+postlist)
                scanHandler = nmap.PortScanner()
                res = scanHandler.scan(hosts=ip,ports=str(postlist.strip(',')),arguments = '-sT -sV -Pn')
                print(res['scan'])
                insert_sql = "insert into ip_port(ip,port,service,product,version,create_time,create_date,status) values"
                if ip in res['scan'].keys():
                    if 'tcp' in res['scan'][ip].keys():
                        data = res['scan'][ip]['tcp']

                        with open(nscanFile, 'w') as f:
                            f.write(json.dumps(data))

                        insert = 0
                        for port,dt in data.items():
                            service = dt['name']
                            product = dt['product']
                            version = dt['version']
                            status  = dt['state']
                            #判断是否存在
                            sql = "select id from ip_port where ip='%s' and port='%s'"%(ip,port)
                            exists = MysqlDB().queryOne(sql)
                            if exists:
                                id = exists['id']
                                sql = "update ip_port set ip='%s',port=%s,service='%s',product='%s',version='%s',status='%s',update_time='%s',update_date='%s' where id=%s"%(ip,port,service,product,version,status,_getDateInt(),_getDatetimeStr(),id)
                                MysqlDB().execute(sql)
                            else:
                                insert  =1
                                insert_sql +="('%s','%s','%s','%s','%s','%s','%s','%s'),"%(ip,port,service,product,version,_getDateInt(),_getDatetimeStr(),status)


                        if insert :
                            print(insert_sql)
                            num = MysqlDB().execute(insert_sql.strip(','))
                            if num>0:
                                print('端口服务新增成功')
                            else:
                                print('端口服务新增失败')

    def expire(self):
        print('--------------------开始处理过期资源---------------------\r\n')
        today = _getTimeStr()
        sql = "select id  from ip_port where  (update_date<'%s' or (update_date is null and create_date <'%s') )" % (
             today + ' 00:00:00', today + ' 00:00:00')
        res = MysqlDB().query(sql)

        if res:
            ids = ''
            for i in res:
                ids += str(i['id']) + ','

            sql = "update ip_port set status='down' where id in (%s)" % (ids.strip(','))
            if MysqlDB().execute(sql) > 0:
                print('过期数据处理成功')
            else:
                print('过期数据处理失败')


if __name__ == "__main__":
    scanBase().start()
