import threading
import json
import os
from concurrent.futures import ThreadPoolExecutor
from events           import Event,EventHandler
from dispatchers      import DispatcherObject
from sservers import SocketServer,SocketStartEvent
from jimo_logservices import Client
from jimo_logservices import MessageParser
from jimo_logservices import MessageLoggerService


DELAY_TIME = 0.2


class LoggingServerApp(DispatcherObject):

    
    def __init__(self,AppName,  port:int = 4450):
        super().__init__();
        self.__Started         =  False;
        self.__Server          =  SocketServer(port=port);
        self.__Synchronised    =  threading.Lock()
        self.__Server.Started += self.__OnServerStarted
        self.__Server.Faulted += self.__OnServerFaulted
        self.__Server.Accepted+=self.__OnClientAccepted
        self._threadPool        = ThreadPoolExecutor(5)
        self.__Clients          =  list();
        self.__Parser           = MessageParser()
        self.__AppName          = os.path.basename(AppName)
        self.__Service          = MessageLoggerService("{0}.txt".format(AppName), AppName=self.__AppName)
        self.__IsOpened         = True
        

    @property
    def Service(self):
        return self.__Service
    
    @property
    def IsStarted(self):
        return self.__Server.IsRunning and self.__IsOpened

    def Start(self):
        try:
            self.__Synchronised.acquire()
            if(self.IsStarted is not True):
                self.__Server.Start()
        except Exception as err:
            self.__Synchronised.release()
            if(self.IsStarted is True):
                self.__Server.Stop()
            raise err
        self.__Synchronised.release()

    def Stop(self):
        try:
            self.__IsOpened = False
            self.__Synchronised.acquire()
            if(self.IsStarted):
                self.__Server.Stop()
            for c in self.__Clients:
                c.Close()
                self.__Clients.remove(c)
                
            self.__Synchronised.release()
        except:
            self.__Synchronised.release()
            
       
    def __HandleClientRequest(self, client):
        try:
            mistakeCount = 0;
            while(self.IsStarted):
                if(client is not None):
                    if(client.IsOpened):
                        request   = client.Read();
                        if request:
                            replyMessage  = None
                            try:
                                #parse the request data
                                message  = self.__Parser.Decode(request.decode("utf-8"));
                                if(message is not None):
                                    message.IpAddress           = "{0}:{1}".format(client.IpAddress,client.Port)
                                    message.ApplicationName     =  self.Service.AppName
                                    result = self.Service.LogMessage(message)
                                    
                                    if(result is not False):
                                        replyMessage  = '''{"success":true}'''                                        
                                    else:
                                        replyMessage  = '''{"success":false, "error":"unable to queue log, try again later"}'''
                                    client.Write(replyMessage.encode("utf-8"))
                                    
                            except Exception as err:
                                print(err)
                                replyMessage  = '''{"success":false, "error":{0}}'''.format(str(err))
                                client.Write(replyMessage.encode("utf-8'"))
                                raise err;
        except Exception as err:
            if(client.IsOpened):
                for c in self.__Clients:
                    if ( (c.Port == client.Port)  and
                         (c.IpAddress  ==  client.IpAddress)):
                        self.__Clients.remove(c)
                
                client.Close()
            self.__IsOpened = False
            print(err)
            
        

    def __OnClientAccepted(self,e):
        try:
            #Create a different thread to handle reading and parsing
            client  =  self.__CreateOrGetClient(e.Socket); 
            self._threadPool.submit(self.__HandleClientRequest,client)
            self.__Clients.append(client)
        except Exception as err:
            print(err)

    def __CreateOrGetClient(self, sock):
        client  = None
        addresses =  sock.getpeername()
        for c in self.__Clients:
            if ((c.IpAddress == addresses[0]) and
                 (c.Port == addresses[1])):
                  c.Close()
                  self.__Clients.remove(c)
                  break;  
        client  =  Client(socket = sock)
        return client

    def __OnServerFaulted(self, e):
        print("Fault detected")
        pass;

    def __OnServerStarted(self, e):
        try:
           print("Server started at {0}:{1}", self.__Server.HostAddress, self.__Server.Port)
        except:
            raise 
            


if __name__ =="__main__":
    import time
    try:
        app  = LoggingServerApp("../logs/SGStudentRegistration",8086);
        app.Start();
        total_logs  =  0;
        while(app.IsStarted):
            operation =  app.Service.Dispatcher.Run()
            if(not operation):
                time.sleep(1)
            total_logs +=1
                
    except KeyboardInterrupt as err:
        app.Stop()
        print(err);
        print("Stopped = {0}".format(total_logs))
    
    
