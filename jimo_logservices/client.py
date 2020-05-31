import socket;
import uuid;
from threading import Thread, Lock;
from events import BaseObject , Event, EventHandler;


DEFAULT_READ_BLOCK = 1024 *4;


class ClientFaultEvent(Event):

    def __init__(self, client, exception:Exception):
        super().__init__("client.fault.event");
        self.__Client    =  client;
        self.__Exception =  exception;

    @property
    def Client(self):
        return self.__Client;

    @property
    def Exception(self):
        return self.__Exception;
    

class Client(object):

    def __init__(self, **kwargs):
        soc = kwargs['socket'] if('socket' in kwargs) else None;
        self.__Socket        =  soc;
        self.__IsOpened      =  True if(isinstance(soc, socket.socket)) else False;
        self.__Closed        =  EventHandler();
        self.__Faulted       =  EventHandler();
        self.__ReadLock      =  Lock();
        self.__SessionUID    = uuid.uuid4();
        self.__Timeout       = kwargs['timeout'] if (('timeout' in kwargs) and ((type(kwargs['timeout'])== int) or (type(kwargs['timeout'])== float))) else 5;
        if(self.__IsOpened):
             self.__Socket.settimeout(self.__Timeout);

    @property
    def Socket(self):
        return self.__Socket;
   
    @property
    def Faulted(self):
        return self.__Faulted;

    @Faulted.setter
    def Faulted(self, handler)-> None:
        if(handler == self.__Faulted):
            self.__Faulted  =  self.__Faulted;

    @property
    def Port(self):
        return self.__Socket.getpeername()[1];
    
    @property
    def IpAddress(self):
        return self.__Socket.getpeername()[0];

    @property
    def Closed(self):
        return self.__Closed

    @Closed.setter
    def Closed(self, handler):
        if(isinstance(handler,EventHandler)):
           if(self.__Closed == handler):
               self.__Closed = handler;

    def Open(self, host, port):
        self.__ReadLock.acquire();
        if(self.IsOpened is not True):
            self.__Socket  =  socket.socket(socket.AF_INET, socket.SOCK_STREAM);
            self.Socket.settimeout(self.__Timeout);
            try:
                timeout  =  self.Socket.gettimeout();
                self.Socket.connect((host, port));
                self.__IsOpened = True; 
            except  Exception as err :
                self._RaiseFault(err);
            finally:
                self.__ReadLock.release();
        
        return self.IsOpened;
    

    def Write(self , data:bytearray):
        result =  0;
        try:
            self.__ReadLock.acquire();           
            if(self.IsOpened):
                result  = self.Socket.send(data);
        except Exception as err:
            self._RaiseFault(err);
        finally:
            self.__ReadLock.release();
        return result;

    def Read(self , nSize = DEFAULT_READ_BLOCK ):
        self.__ReadLock.acquire();
        try:
            result =  None;
            
            if(self.IsOpened)  and (type(nSize) is int):
                data_recieved =  self.Socket.recv(nSize);
                if(len(data_recieved) > 0):
                    result = data_recieved;
        except Exception as err:
            self._RaiseFault(err);
        finally:
            self.__ReadLock.release();
        return result;
        
    @property
    def IsOpened(self):
        return self.__IsOpened;

    def Close(self):
        try:
            self.__ReadLock.acquire();
            if(self.IsOpened is True):
                self.IsOpened  =  False;
                self.__Socket.close();
                if(self.Closed is not None):
                    self.Closed(Event("socket.event.close"));
        except Exception as err:
            self._RaiseFault(err);
        finally:
            self.__ReadLock.release();


    def _RaiseFault(self, exception:Exception):
        if(isinstance(exception , Exception)):
            if(self.Faulted is not None):
                self.Faulted(ClientFaultEvent(self, exception));


if(__name__ =="__main__"):

    def OnFaulted(err):
        print(err.Exception);
    try:
        print("Connecting ...\n");
        client  =  Client(timeout  = 5.90);
        client.Faulted+=OnFaulted;
        status  = False;
        attempted = 0;
        while(status != True):           
            status  = client.Open("10.10.0.45", 8081);
            attempted+=1;
            if(status):
                print("Connected: Reading...");
                data   = client.Read();
                print(data);
            else:
                if(attempted >= 2):
                    status = True;
                    break;
                print("Reconnecting: {0}".format(attempted));
                   
        print("Disconnected Status = {0}".format(status));
        
    except Exception as err:
        print(err);
    finally:
        client.Close();
    
    
