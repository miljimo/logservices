import threading;
from dispatchers      import DispatcherObject;
from events           import EventHandler, Event;
from jimo_logservices import Client, ClientFaultEvent

class DataRecievedEvent(Event):

    def __init__(self, source, data):
        super().__init__("channel.data.recieved.event");
        self.__Channel = source;
        self.__Data    = data;

    @property
    def Channel(self):
        return self.__Channel;

    @property
    def Data(self):
        return self.__Data;

        
class Channel(DispatcherObject):

    def __init__(self, client: Client = None):
        super().__init__();        
        self.__DataRecieved =  EventHandler();
        self.__Client       =  client if(isinstance(client , Client)) else Client();
        self.__ReadThread   =  self.__CreateThread();
        self.__IsRunning  = False;
        self.__Synchronised = threading.Lock();
        
    @property
    def IsRunning(self):
        return self.__IsRunning;

    @property
    def DataRecieved(self):
        return self.__DataRecieved;

    @DataRecieved.setter
    def DataRecieved(self, handler:EventHandler)->None:
        if handler == self.__DataRecieved:
            self.__DataRecieved  =  self.__handler

    @property
    def Client(self):
        return self.__Client;
    

    def Connect(self, ipAddress:str , port:int)->bool:
        status  = False;
        try:
            self.__Synchronised.acquire();
            if(self.IsRunning):
                return ;
            if(self.__ReadThread == None):
                self.__ReadThread        = self.__CreateThread();
            self.__ReadThread.daemon = True;
            if(self.Client != None):
                status  =  self.Client.Open(ipAddress,port);
                if(status):
                    self.__ReadThread.start();
        except Exception as err:
            self._RaiseFault(err);
        finally:
            if(status is not True):
                self.__Synchronised.release();
            return status;

    def Stop(self):
        try:
            self.__Synchronised.acquire();
            if(self.IsRunning):
                #Stop the reading of the client data in a normal way.
                self.__IsRunning = False;
                if(self.__ReadThread != None):
                    if(self.__ReadThread.is_alive()):
                        self.__ReadThread.join(1);
            if(self.Client != None):
                 self.Client.Close();
        finally:
            self.__ReadThread = None;
            self.__Client     = None;
            self.__Synchronised.release();
        

    def __ReadInBackground(self):
        self.__IsRunning  = True
        self.__Synchronised.release()
       
        try:
            while(self.IsRunning):                
                if((self.Client != None) and
                   (self.Client.IsOpened)):
                    print("Reading...");
                    # Read the data and block until there is something to read.
                    data  =  self.Client.Read();
                    if(data != None):
                        if(self.DataRecieved != None):
                            self.DataRecieved(DataRecievedEvent(self, data));
                        pass;
                    pass;
        except Exception as err:
            self._RaiseFault(err);
        finally:
            self.Client.Close();
            self.__ReadThread  = None;
            self.__IsListening = False;

    def __CreateThread(self):
        return threading.Thread(target= self.__ReadInBackground)


    def _RaiseFault(self, exception:Exception):
        if(isinstance(exception , Exception)):
            if(self.Client.Faulted != None):
                self.Client.Faulted(ClientFaultEvent(self,exception));
        



if(__name__ =="__main__"):
    def OnFaulted(evt):
        print(evt.Exception);
        
    channel  =  Channel();
    channel.Client.Faulted+= OnFaulted;
    channel.Connect("localhost",8084);
    pass;

    
