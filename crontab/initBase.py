from lib.log import  Log

class initBase:
    account = {}
    logger  = ''

    def __init__(self,cloud_type,cloud):
        self.logger = Log(cloud_type.lower(), cloud)
        

