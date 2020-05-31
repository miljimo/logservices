import io;
import os;
from logmessage import LogMessage, LogMessageType;

class FileMessageLogger(object):
    

    def __init__(self, filename:str = 'log.txt'):
        if(type(filename) != str):
            raise TypeError("@FileMessageLogger : expecting a filename to be string");
        self.__Stream   =  None;
        self.__IsOpened  = False;
        if os.path.exists(filename) is not True:
           self.__Stream =  open(filename, mode='w+')
           self.__IsOpened = True;
        else:        
            self.__Stream  =  open(filename, mode='a');
            self.__IsOpened = True;
        self.__Filename    =  filename;
       
        
    @property
    def Filename(self):
        return self.__Filename;

    @property
    def IsOpened(self):
        return self.__IsOpened;
    

    def Write(self, message: LogMessage) -> bool:
        status  = False;
        if(isinstance(message, LogMessage) is not True):
            raise TypeError("@FileLogger: expecting a LogMessage structure object");
        message: LogMessage
        self.__Stream : io.TextIOWrapper
            
        if(self.__Stream != None):
            if(self.IsOpened):
                message_str  = '{0}\n'.format(message) ;
                self.__Stream.write(message_str);
                self.__Stream.flush();
                status  = True;

        return status ;


    def Close(self):
       
        if(self.__Stream  != None):
            self.__Stream : io.TextIOWrapper;
            self.__Stream.close();
            self.__IsOpened = False;
            


if __name__ =="__main__":
    logger   = FileMessageLogger('test_log.txt');
    for index in range(0,4):
        message  =  LogMessage("192.168.0.12", "Pulsar Service", index);
        message.Message =  "I do not understand why software is good";
        status   = logger.Write(message);
        if(status):
            print("Success");

    logger.Close();
    
        
    
            
            
        
        
   
        
