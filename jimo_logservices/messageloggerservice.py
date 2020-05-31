import time
import threading
import json
from events           import Event,EventHandler
from dispatchers      import DispatcherObject
from jimo_logservices import MessageParser
from jimo_logservices import MessageLogger
from jimo_logservices import LogMessage , LogMessageType

DEFAULT_APP_NAME  ='Unknown App'
DEFAULT_IPADDRESS = '192.168.0.1'
DEFAULT_CHUNK_LOG_SIZE = 1024 * 100
LOG_DIRECTION   = "app"


class MessageLoggerService(DispatcherObject):

    def __init__(self, filename: str, **kwargs):
        super().__init__()
        self.__AppName       = kwargs['AppName'] if('AppName' in kwargs) else DEFAULT_APP_NAME
        self.__SizePerFile   = kwargs['SizePerFile'] if('SizePerFile' in kwargs) else DEFAULT_CHUNK_LOG_SIZE
        self.__Logger        = MessageLogger(filename, SizePerFile = self.__SizePerFile)
        self.__Synchronised  = threading.Lock()
        self.__DebugMode     = kwargs['debug'] if('debug' in kwargs) else True


    @property
    def DebugMode(self):
        return self.__DebugMode
    
    @property
    def SizePerFile(self):
        return self.__SizePerFile;
    @property
    def AppName(self):
        return self.__AppName
    
    @property
    def Count(self):
        return self.__Logger.Count
 
    def Log(self ,logType : LogMessageType, ipAddress:str, message:str)->None:
        try:
            self.__Synchronised.acquire()
            
            if (type(logType) != int):
                if(isinstance(logType, LogMessageType) is not True):
                    raise TypeError("@Expecting a log type message")
            logMessage  =  LogMessage(ipAddress, self.AppName, logType)
            logMessage.Message  =  message
            self.Dispatcher.Invoke(self.__WriteLogToFile , logMessage)
            self.__Synchronised.release()
        except Exception as err:
            self.__Synchronised.release()
            raise err

    def LogMessage(self, message:LogMessage)->bool:
        status  = False
        try:
            if(isinstance(message, LogMessage)):
                #determined which type of log it belongs to
                messageType  =  message.MessageType
                
                if(type(messageType) == LogMessageType):
                    
                    if(messageType.Value ==  LogMessageType.DEBUG):
                        self.Debug(message.IpAddress, message.Message)
                    elif(messageType.Value == LogMessageType.INFO):
                        self.Info(message.IpAddress, message.Message)
                    elif(messageType.Value == LogMessageType.WARNING):
                        self.Warning(message.IpAddress, message.Message)
                    elif(messageType.Value  == LogMessageType.EXCEPTION):
                        self.Error(message.IpAddress, message.Message)
                    else:
                         self.Log(LogMessageType.UNKNOWN,message.IpAddress, message.Message)
                status = True
        except Exception as err:
            print(err)
            raise
        return status
         

    def Debug(self, ipAddress :str , message:str):
        self.Log(LogMessageType.DEBUG,ipAddress, message)

    def Info(self, ipAddress :str , message:str):
        self.Log(LogMessageType.INFO,ipAddress, message)

    def Warning(self, ipAddress :str ,message:str):
        self.Log(LogMessageType.WARNING, ipAddress, message)

    def Error(self,  ipAddress :str ,message:str):
        self.Log(LogMessageType.EXCEPTION,ipAddress, message);
        
    def __WriteLogToFile(self, message : LogMessage):
        result  =  None
        try:
            if(isinstance(message, LogMessage)):
                if(self.__Logger != None):                  
                    if(self.__Logger.IsOpened is True):
                        self.__Logger.Write(message)
                        if(self.DebugMode):
                            print(str(message))
                        result  = message;
        except Exception as err:
            raise err
        return result;


if __name__ == "__main__":
    LOG_FILE_PATH ="../logs/service_logger.txt"
    def AutoLogger(service):
        while(True):
            service.Debug("localhost","Auto debugging logging");
            service.Info("localhost","Auto info logging");
            service.Warning("localhost","Auto warning logging");
            service.Error("localhost","Auto exception logging");

            result  = service.LogMessage(LogMessage("192.167.1.20", service.AppName, LogMessageType.DEBUG))
           
        
    service = MessageLoggerService(LOG_FILE_PATH)
    t = threading.Thread(target=AutoLogger, args=(service,))
    t.daemon= True
    t.start()

    while(True):
        op = service.Dispatcher.Run();
        if not op:
            time.sleep(1)
        else:
            print(op.Result)
           
   
