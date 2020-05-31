import json;
from jimo_logservices import LogMessage
from jimo_logservices import LogMessageType


class MessageParserException(Exception):

    def __init__(self, err:Exception):
        super().__init__(str(err))        
        self.__Exception  = err if(isinstance(err, Exception)) else None

    def Exception(self):
        return self.__Exception
    

class MessageParser(object):

    
    def Decode(self, data:str)-> LogMessage:
        logMessage  =  None
        if(type(data) != str):
            raise TypeError(data)
        try:
            jsonObj  =  json.loads(data);
            if(jsonObj is not None):
                if('LogType' in  jsonObj):
                    logType   =  int(jsonObj['LogType'])                   
                    ipAddress =  jsonObj['IpAddress'] if ('IpAddress' in jsonObj) else 'Unknown'
                    appName   =  jsonObj['AppName'] if ('AppName' in jsonObj) else "Unknown App"
                    message   =  jsonObj['Message'] if('Message' in jsonObj) else None
                    if(message == None):
                        raise Exception("@Parser: expecting a valid log Message")
                    
                    logMessage  =  LogMessage(ipAddress, appName, logType)
                    logMessage.Message  =  message
        except Exception as err:
            raise MessageParserException(err)
        return logMessage

    def Encode(self, message: LogMessage)->str:
        log  =  dict()
        
        try:
            if(isinstance(message, LogMessage) is not True):
                raise TypeError(str(message))
            
            log['LogType']   = message.MessageType
            log['IpAddress'] = message.IpAddress
            log['AppName']   = message.ApplicationName
            log['Message']   = message.Message
            log['DateTime']  = str(message.DateTime)
            
        except Exception as err:
            raise MessageParserException(err)
        
        return log


if __name__ =="__main__":
    try:
        json_str  =  '''{"LogType":"0", "IpAddress":"localhost", "AppName":"Pulsar Service", "Message":" Initialisation of resources..."}'''
        parser    =  MessageParser()
        message   =  parser.Decode(json_str)
        val  = parser.Encode(message)
        print(message)
        print("\n")
        print(val)
    except MessageParserException as err:
        print(err);
            
