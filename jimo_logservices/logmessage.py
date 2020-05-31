
from datetime import datetime;


class LogMessageType(int):
    UNKNOWN   = 0xFF; #Unknown log should
    DEBUG     = 0x00;
    INFO      = 0x01;
    WARNING   = 0x02;
    EXCEPTION = 0x03;

    def __init__(self, logValue: int):
        if type(logValue) != int:
            raise TypeError("@Expecting an int value for log object");
        if ((logValue  != self.UNKNOWN) and
            (logValue  != self.DEBUG) and
            (logValue  != self.INFO) and
            (logValue  != self.WARNING) and
            (logValue  != self.EXCEPTION)):
             raise ValueError("@LogMessageType: {0} is invalid".format(logValue));

        self.__LogValue  =  logValue;

    @property
    def Value(self):
        return self.__LogValue

    def __str__(self):
        strvalue  = "UNKNOWN"
        if(self.Value == self.DEBUG):
            strvalue ="DEBUG"
        elif(self.Value == self.INFO):
            strvalue  =  "INFO"
        elif(self.Value == self.WARNING):
            strvalue  =  "WARNING"
        elif(self.Value == self.EXCEPTION):
            strvalue ="EXCEPTION"
        else:
            pass;        
        return "[{0}]".format(strvalue)
          
         

class LogMessage(object):

    def __init__(self, ipAddress:str, applicationName:str ,logType:LogMessageType =
                 LogMessageType.UNKNOWN):
        self.__MessageType = None;
        if self.__ValidIpAddressID(ipAddress) is not True:
            raise TypeError("@IpAddress: {0} is invalid".format(ipAddress));
        if(self.__ValidApplicationName(applicationName) is not True):
            raise TypeError("@applicationName : is not valid");
            
        self.__DateTime : datetime         =  datetime.now();
        self.__Message  : str              =  '';
        self.__ApplicationName : str       =  applicationName;
        self.__IpAddress       : str       =  ipAddress;
        self.MessageType  : LogMessageType = logType;

    @property
    def MessageType(self)-> LogMessageType: 
        return self.__MessageType;

    @MessageType.setter
    def MessageType(self, logtype: LogMessageType)->None:
        if((type(logtype) != int) and (type(logtype) != LogMessageType)):
            raise TypeError("@Expecting a log type of object LogMessageType");
        
        if(type(logtype) == int):            
            self.__MessageType   =  LogMessageType(logtype);
        else:
            self.__MessageType   =  logtype;

    @property
    def IpAddress(self):
        return self.__IpAddress;
            
    @property
    def ApplicationName(self):
        return self.__ApplicationName;


    @property
    def DateTime(self):
        return self.__DateTime;
    
    @DateTime.setter
    def DateTime(self, dtime: datetime):
        dtime : datetime;
        if(isinstance(dtime, datetime) is not True):
            raise TypeError("@Datetime: property expected to be a datetime object");
        self.__DateTime  =  dtime;

    @property
    def Message(self):
        return self.__Message;

    @Message.setter
    def Message(self, message:str):
        if(type(message) != str):
            raise TypeError("@Message: expecting a string value");
        self.__Message  =  message;

    def __ValidIpAddressID(self, ipAddress:str)->bool:
        status  = False;
        if type(ipAddress) == str:
            if ipAddress.strip() != '':
               status  = True;
        return status

    def __ValidApplicationName(self, applicationName:str)->bool:
        status  = False;
        if type(applicationName) == str:
            if applicationName.strip() != '':
                status  = True;
        return status;

    def __PaddingText(self, text:str , size:str):
        value  =  str(text);
        length  = len(value);
        paddinglength = size  - length;
        if(paddinglength > 0):
            for i in range(paddinglength):
                value +=" ";
        return value;
        
        

    def __str__(self)->str:

        messageType  =  self.__PaddingText(self.MessageType,12);
        result : str  =  "{0} - {1}- {2}; {3}:{4} ".format(self.DateTime,
                                                  messageType,
                                                  self.IpAddress,
                                                  self.ApplicationName,
                                                  self.Message );

        return result;


if __name__ =="__main__":
    logMessageType  =  LogMessageType(LogMessageType.EXCEPTION);
    logMessage  = LogMessage("192.168.1.12", "Pulsar", logMessageType);
    logMessage.Message="Zero division error founded"
    print(logMessage);

    
        
