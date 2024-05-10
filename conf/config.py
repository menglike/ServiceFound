import os

class Config():
    SCAN_DIR   = os.path.dirname ( os.path.dirname( os.path.abspath(__file__) ) ) +'/crontab/scan'
    LOG_DIR    = os.path.dirname ( os.path.dirname( os.path.abspath(__file__) ) ) +'/logs'

    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASS = 'root'
    MYSQL_DB   = 'hawkeye2'

    user       = 'secw'
    passwd     = '123'

