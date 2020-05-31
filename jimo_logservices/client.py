import socket
import time
import errno
import select
import uuid
from threading import Thread, Lock
from events import Event, EventHandler

DEFAULT_READ_BLOCK = 1024
DEFAULT_TIMEOUT = 5


class ClientFaultEvent(Event):

    def __init__(self, client, exception: Exception):
        super().__init__("client.fault.event")
        self.__Client = client
        self.__Exception = exception

    @property
    def Client(self):
        return self.__Client

    @property
    def Exception(self):
        return self.__Exception


class ClientCloseEvent(Event):
    def __init__(self, client):
        super().__init__("SocketCloseEvent")
        self.__Client = client

    @property
    def Client(self):
        return self.__Client


class Client(object):

    def __init__(self, **kwargs):
        soc = kwargs['socket'] if ('socket' in kwargs) else None
        self.__Socket = soc
        self.__IsOpened = True if (isinstance(soc, socket.socket)) else False
        self.__Closed = EventHandler()
        self.__Faulted = EventHandler()
        self.__ReadLock = Lock()
        self.__SessionUID = uuid.uuid4()
        self.__NonBlocking = False
        self.__Timeout = kwargs['timeout'] if (('timeout' in kwargs) and
                                               ((type(kwargs['timeout']) == int) or
                                                (type(kwargs['timeout']) == float))) else DEFAULT_TIMEOUT
        if self.__IsOpened:
            self.__Socket.settimeout(self.__Timeout)

    @property
    def IsBlocking(self):
        return self.__NonBlocking

    @IsBlocking.setter
    def IsBlocking(self, value: bool):
        if type(value) == bool:
            self.__Socket: socket.socket
            self.__NonBlocking = value
            self.__Socket.setblocking(self.__NonBlocking)

    @property
    def Socket(self):
        return self.__Socket

    @property
    def Faulted(self):
        return self.__Faulted

    @Faulted.setter
    def Faulted(self, handler) -> None:
        if handler == self.__Faulted:
            self.__Faulted = self.__Faulted

    @property
    def Port(self):
        return self.__Socket.getpeername()[1]

    @property
    def IpAddress(self):
        return self.__Socket.getpeername()[0]

    @property
    def Timeout(self):
        return self.__Timeout

    @Timeout.setter
    def Timeout(self, value: float):
        if (type(value) == float) or (type(value) == int):
            self.__Timeout = value

    @property
    def Closed(self):
        return self.__Closed

    @Closed.setter
    def Closed(self, handler):
        if isinstance(handler, EventHandler):
            if self.__Closed == handler:
                self.__Closed = handler

    def Open(self, host, port):
        self.__ReadLock.acquire()
        if self.IsOpened is not True:
            self.__Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.__Socket.settimeout(self.__Timeout)
                self.__Socket.connect((host, port))
                if self.IsBlocking is not True:
                    self.__IsOpened = True
            except socket.error as e:
                if (e.errno == errno.EWOULDBLOCK) or (e.errno == errno.EINPROGRESS):
                    ready_sockets = select.select([], [self.__Socket], [])[1]
                    if len(ready_sockets) > 0:
                        socket_ready = ready_sockets[0]
                        self.__IsOpened = True
                else:
                    self.__IsOpened = False
                    self._RaiseFault(e)
                    raise e
            finally:
                self.__ReadLock.release()
        return self.IsOpened

    def Write(self, data: bytearray):
        self.__ReadLock.acquire()
        total_length = 0
        try:
            if self.IsOpened:
                total_length = self.Socket.send(data)
        except Exception as e:
            self.__IsOpened = False
            self._RaiseFault(e)
            self.__ReadLock.release()
        self.__ReadLock.release()
        return total_length

    def Read(self, nSize=DEFAULT_READ_BLOCK):
        self.__ReadLock.acquire()
        buffer = bytearray()
        try:
            try:
                if self.IsOpened and (type(nSize) is int):
                    buffer = self.Socket.recv(nSize)
            except socket.error as e:
                if ((e.errno != errno.EWOULDBLOCK) and
                        (e.errno != errno.EAGAIN)):
                    select.select([self.Socket], [], [])
                else:
                    raise e
        except Exception as e:
            self.__IsOpened = False
            self.__ReadLock.release()
            self._RaiseFault(e)
            raise e 
        self.__ReadLock.release()
        return buffer

    @property
    def IsOpened(self):
        return self.__IsOpened

    def Close(self):
        try:
            self.__ReadLock.acquire()
            if self.IsOpened is True:
                self.IsOpened = False
                self.__Socket.shutdown()
                self.__Socket.close()
                self.__ReadLock.release()
                if self.Closed is not None:
                    self.Closed(ClientCloseEvent(self))
        except Exception as err:
            self._RaiseFault(err)      
            self.__ReadLock.release()
            raise err
       

    def _RaiseFault(self, exception: Exception):
        if isinstance(exception, Exception):
            if self.Faulted is not None:
                self.Faulted(ClientFaultEvent(self, exception))


if __name__ == "__main__":

    def OnFaulted(err):
        print("@FaultError: {0}".format(err.Exception))


    try:
        print("Connecting ...\n")
        client = Client(timeout=5.90)
        client.Faulted += OnFaulted
        status = False
        attempted = 0
        if not status:
            status = client.Open("10.10.0.45", 8081)
            attempted += 1
            if status:
                print("Connected: Reading...")
                data = client.Read()
                if data:
                    print(data)
            else:
                if attempted >= 2:
                    status = True
                print("Reconnecting: {0}".format(attempted))

        print("Disconnected Status = {0}".format(status))

    except Exception as err:
        print(err)
    finally:
        client.Close()
