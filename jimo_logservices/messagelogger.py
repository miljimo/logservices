import io;
import os;
import threading;
from jimo_logservices  import LogMessage, LogMessageType;
import uuid

class MessageLogger(object):
    

    def __init__(self, filename:str, **kwargs):
        if(type(filename) != str):
            raise TypeError("@FileMessageLogger : expecting a filename to be string");
        self.__SizePerFile  =  kwargs['SizePerFile'] if ('SizePerFile' in kwargs) else (1024*100)        
        self.__Filename      = filename;
        self.__Synchronised  = threading.Lock()
        self.__Stream        =  None
        self.__OpenFile(filename);
        
    @property
    def __Size(self):
        size  =  0;
        if(self.__Stream != None):
            if(self.IsOpened):
                cur_pos  =  self.__Stream.tell()
                size  = self.__Stream.seek(0,io.SEEK_END);
                self.__Stream.seek(cur_pos, io.SEEK_SET)
        return size

    def __OpenFile(self, filename:str):
        try:
            self.__Synchronised.acquire()          
            
            if(self.__Stream is not None):
                if(self.__Stream.IsOpened is True):
                    self.__Stream.close();
                    self.__Stream    = None
            self.__IsOpened  = False
            
            if os.path.exists(filename) is not True:              
               self.__Stream =  open(filename, mode='w+')
               self.__IsOpened = True;
            else:               
                self.__Stream  =  open(filename, mode='a');
                self.__IsOpened = True;
            
        except Exception as err:
            self.__Synchronised.release()
            raise err
        self.__Synchronised.release()
       
        
    @property
    def Filename(self):
        return self.__Filename;

    @property
    def IsOpened(self):
        return self.__IsOpened;

    def Write(self, message: LogMessage):
        try:
            if(self.__Stream is not None):
                if(self.__Size >= self.__SizePerFile):
                    self.__Stream.close();
                    self.__Stream = None;
                    #Rename file name to a random file
                    baseFileName  = os.path.basename(self.Filename);
                    folder        = os.path.dirname(self.Filename)
                    newfilename  = os.path.join(folder, "{0}_{1}".format(uuid.uuid4(), baseFileName))
                    os.rename(self.Filename,newfilename)
                    with open(self.Filename, mode='w') as file:
                        #Clear the code
                        file.close()
                        pass
                    self.__OpenFile(self.Filename);
                self.__WriteLog(message);
        except Exception as err:
            print(err);
            raise err;
            
                

    def __WriteLog(self, message: LogMessage) -> bool:
        status  = False;
        try:
            self.__Synchronised.acquire()
       
            if(isinstance(message, LogMessage) is not True):
                raise TypeError("@FileLogger: expecting a LogMessage structure object");
            message: LogMessage
            self.__Stream : io.TextIOWrapper
                
            if(self.__Stream != None):
                if(self.IsOpened):
                    message_str  = '{0}\n'.format(message) ;
                    self.__Stream.write(message_str);
                    self.__Stream.flush();
                    status  = True
                    
        except Exception as err:
            self.__Synchronised.release()
            raise err
        self.__Synchronised.release()
        return status


    def Close(self):
       
        if(self.__Stream  != None):
            self.__Stream : io.TextIOWrapper;
            self.__Stream.close();
            self.__IsOpened = False;
            


if __name__ =="__main__":
    logger   = MessageLogger('test_log.txt');
    for index in range(0,4):
        message  =  LogMessage("192.168.0.12", "Pulsar Service", index);
        message.Message =  "I do not understand why software is good";
        status   = logger.Write(message);
        if(status):
            print("Success");

    logger.Close();
    
        
    
            
            
        
        
   
        
