import time
import threading
import json
from dispatchers import DispatcherObject
from events import EventHandler, Event
from jimo_logservices import Client, ClientFaultEvent
from jimo_logservices import MessageParser
from jimo_logservices import LogMessage, LogMessageType


class ReplyMessage(object):

    def __init__(self, jsonstr:str):
        json_object  =  json.loads(jsonstr);
        if(json_object is not None):
            self.__Success  =  json_object['success']
            self.__Error    =  json_object['error'] if ('error' in json_object) else None
    @property
    def Success(self):
        return self.__Success
    @property
    def Error(self):
        return self.__Error


    def __str__(self):
        return "ReplyMessage[success = {0},error = {1}]".format(self.Success, self.Error)
       
class ServiceLogger(DispatcherObject):

    def __init__(self, ipAddress :str, port:int):
        super().__init__()
        self.__Client  = Client()
        self.__IpAddress  = ipAddress
        self.__Port       = port
        self.__Client.Open(self.__IpAddress, self.__Port)
        self.__Parser   =  MessageParser()
        self.__logLocker =  threading.Lock()

    @property
    def Available(self):
        return self.__Client.IsOpened

    def __Log(self, message: LogMessage):
        reply = None
        try:
            self.__logLocker.acquire()
            if(isinstance(message, LogMessage)):
                if(self.__Client.IsOpened):
                    data  =  self.__Parser.Encode(message)
                    if(data):
                        data_str  =  json.dumps(data)
                        self.__Client.Write(data_str.encode("utf-8'"))
                        replyStr  = self.__Client.Read();
                        if(replyStr):
                            reply = ReplyMessage(replyStr.decode('utf-8'))
                            
            self.__logLocker.release()
        except Exception as err:
            self.__logLocker.release()
            self.__Client.Close()
            print(err)
        return reply

    def Debug(self, message):
         return self.__WriteLog(message, LogMessageType.DEBUG)
        
    def Info(self, message):
        return self.__WriteLog(message, LogMessageType.INFO)
    
    def Warning(self, message):
        return self.__WriteLog(message, LogMessageType.WARNING)
    
    def Error(self,excep: Exception):
        return self.__WriteLog(str(excep), LogMessageType.EXCEPTION)

    def __WriteLog(self, message:str , logType: LogMessageType.DEBUG):
         messageLog  = LogMessage("localhost","FakeMessageAppName", logType)
         messageLog.Message  = message
         return self.__Log(messageLog)
        
    def __del__(self):
        if(self.__Client.IsOpened):
            self.__Client.Close()

        
        

    
        

if __name__ == "__main__":
    import json
   
    def OnFaulted(evt):
        print(evt.Exception)
    try:
        channel  =  ServiceLogger("192.168.0.4",8086)
        while(channel.Available):
            print(channel.Error("Something went wrong"))
            print(channel.Info("Some Information testing"))
            print(channel.Debug("Some Debug testing"))
            print(channel.Warning("Some Warning testing"))
          
    except Exception as err:
        print (err)
        
    
   
  
    
