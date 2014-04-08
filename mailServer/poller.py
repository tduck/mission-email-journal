import select
import socket
import sys
import time
import os
import errno
import traceback
from printer import Printer

class Poller:
    """ Polling server """
    def __init__(self,port):
        self.host = "localhost"
        self.port = port
        self.open_socket()
        self.clients = {}
        self.size = 1024
        self.caches = dict()
        self.lastIOs = dict()
        self.hosts = dict()
        self.timout = 1
        self.media = dict()
        self.parseConfig()
        self.serverHeader = "Server: SuperServer\r\n"
        self.version = "HTTP/1.1"

        Printer.debugPrint(Printer, "server initialized. serving on port " + str(self.port))

    def parseConfig(self):
        with open("web.conf") as configFile:
            for line in configFile:
                values = line.split()
                if(len(values) == 3):
                    if(values[0] == "host"):
                        self.hosts[values[1]] = values[2]
                    elif (values[0] == "media"):
                        self.media[values[1]] = values[2]
                    elif(values[0] == "parameter"):
                        if(values[1] == "timeout"):
                            self.timeout = int(values[2])
                    else:
                        Printer.debugPrint(Printer,message="this line of the config file was not recognized :\n..." +line)





    def open_socket(self):
        """ Setup the socket for incoming clients """
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
            self.server.bind((self.host,self.port))
            self.server.listen(5)
            self.server.setblocking(0)
        except socket.error, (value,message):
            if self.server:
                self.server.close()
            print "Could not open socket: " + message
            sys.exit(1)

    def run(self):
        """ Use poll() to handle each incoming client."""
        self.poller = select.epoll()
        self.pollmask = select.EPOLLIN | select.EPOLLHUP | select.EPOLLERR
        self.poller.register(self.server,self.pollmask)
        lastCheck = time.time()
        while True:
            # poll sockets
            try:
                fds = self.poller.poll(timeout=.75)
                Printer.debugPrint(Printer, "poll called")
                Printer.debugPrint(Printer, fds)
            except:
                return
            for (fd,event) in fds:
                Printer.debugPrint(Printer, message="handling event")
                # handle errors
                if event & (select.POLLHUP | select.POLLERR):
                    self.handleError(fd)
                    continue
                # handle the server socket
                if fd == self.server.fileno():
                    self.handleServer()
                    continue
                # handle client socket
                result = self.handleClient(fd)

            #check for garbage collection
            if(time.time() - lastCheck > .75):
                #do gargabe check
                self.cleanUpSockets()
                lastCheck = time.time()
                    

    def handleError(self,fd):
        Printer.debugPrint(Printer, "handling Error for client " + str(fd))
        if fd == self.server.fileno():
            # recreate server socketl
            self.poller.unregister(fd)
            self.server.close()
            self.open_socket()
            self.poller.register(self.server,self.pollmask)
        else:
            # close the socket
            self.removeSocket(fd)

    def handleServer(self):
        # accept as many clients are possible
        while True:
            try:
                (client,address) = self.server.accept()
            except socket.error, (value,message):
                # if socket blocks because no clients are available,
                # then return
                if value == errno.EAGAIN or errno.EWOULDBLOCK:
                    return
                print traceback.format_exc()
                sys.exit()
            # set client socket to be non blocking
            client.setblocking(0)
            self.clients[client.fileno()] = client
            self.poller.register(client.fileno(),self.pollmask)
            self.lastIOs[client.fileno()] = time.time()
            self.caches[client.fileno()]=""
            Printer.debugPrint(Printer, message="client " + str(client.fileno()) + " was added")

    def handleClient(self,fd):
        while(True):
            try:
                data = self.clients[fd].recv(self.size)
                if(data == ""):
                    self.removeSocket(fd)
                    return
            except socket.error, e:
                error = e.args[0]
                if (error == errno.EAGAIN or error == errno.EWOULDBLOCK):
                    return
                else:
                    Printer.debugPrint(Printer, "an error (" + error + ") occured and the client was removed")
                    removeSocket(fs)
            else:
                #got a message so do something with it
                #append the message to the cache for that client
                for i in range(len(data)):
                    self.caches[fd] += data[i]
                Printer.debugPrint(Printer, message= "cache for " + str(fd) + ":  " + self.caches[fd])
                messageProcessed = False
                endIndex = self.caches[fd].find("\r\n\r\n")
                while(endIndex != -1):#this handles a client with multiple valied requests
                    message = self.caches[fd][0:endIndex]
                    leftovers = self.caches[fd][endIndex + 4:len(self.caches[fd])]
                    self.caches[fd] = leftovers
                    if(self.processMessage(message=message, fd=fd)):
                        messageProcessed = True
                    else:
                        Printer.debugPrint("a received message was unable to process: " + message)
                        messageProcessed = True
                    endIndex = self.caches[fd].find("\r\n\r\n")

                if(messageProcessed):
                    return


    def processMessage(self, message, fd):
        #1-read and parse the HTTP request Message
        Printer.debugPrint(Printer, message="the requeset: " + message)
        lines = message.split("\r\n")
        response = ""
        body = None
        openFile = None
        size = None

        request = lines[0].split()
        headers = {}
        path = ""
        domain = self.hosts["default"]
        fileName = "index.html"
        contType = self.media["html"] 
        sendFile = False
        start = 0 
        end = -1
        if(len(request) != 3):
            #return a bad request error
            request = self.getBadRequestError()
            return True
        else:
            url = request[1]
            

            #read in the headers
            for i in range(1, len(lines)):
                nxtHeader = lines[i].split(": ",1)
                if(len(nxtHeader) == 2):
                    headers[nxtHeader[0]] = nxtHeader[1]

            Printer.debugPrint(Printer, headers)

            if(request[0].lower() == "get" or request[0].lower() == "head"):
                #2-translate the URI to a file name
                try:
                    if(url != "/"):
                        splitPath = url.split("/")
                        Printer.debugPrint(Printer, splitPath)
                        fileName = splitPath[len(splitPath) - 1]
                        contType = self.media[fileName.split(".")[1]]
                        Printer.debugPrint(Printer, message="filename: " + fileName+ "  content type: " + contType)
                    else:
                        url = "/" + fileName
                    if "Host" in headers.keys():
                        splitHost = headers['Host'].split(":")[0]
                        Printer.debugPrint(Printer, "looking for host " + splitHost+ " in...")
                        Printer.debugPrint(Printer, self.hosts)
                        if splitHost in self.hosts.keys():
                            domain = self.hosts[splitHost]

                    path = domain+url
                    Printer.debugPrint(Printer, "filePath: " + path)

                    if("Range" in headers.keys()):
                        try:
                            rangeVals = headers["Range"].split("=")[1].split("-")
                            start = int(rangeVals[0])
                            end = int(rangeVals[1])
                        except:
                            body = "the range header was invalid"
                            response = self.version +" 416 Requested range not satisfiable\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: "+str(len(body)) + "\r\nContent-Type: " + contType + "\r\n\r\n" 
                            self.sendToClient(fd, response)
                            return True
                except:
                    response = self.getBadRequestError()


                #3-determine wheter the request is authorized
                    #check file permissions or other authorization procedure
                try :
                    with open(path) as openFile:
                        size = os.stat(path).st_size
                        modified = os.stat(path).st_mtime
                        Printer.debugPrint(Printer, "request:")
                        Printer.debugPrint(Printer, request)
                        if(request[0].lower() == "get"):
                            #if it's a head request we just need to make sure we can open the file                           else:
                            #check for a range header
                            if("Range" in headers.keys()):
                                try:
                                    rangeVals = headers["Range"].split("=")[1].split("-")
                                    start = int(rangeVals[0])
                                    end = int(rangeVals[1])
                                    #get to the right starting point
                                    openFile.seek(start)
                                    body = openFile.read(end+1 - start)
                                    size = end+1 - start
                                    response = self.version +" 206 Partial Content\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: " + str(size) + "\r\nLast-Modified: "+ self.getGMT(modified) + "\r\nContent-Type: " + contType + "\r\n\r\n"
                                except:
                                    Printer.debugPrint(Printer, "error parsing the range header")
                                    Printer.debugPrint(Printer, headers["Range"])
                                    body = "the range header was invalid"
                                    response = self.version +" 416 Requested range not satisfiable\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: "+str(len(body)) + "\r\nContent-Type: " + contType + "\r\n\r\n" 
                            
                            else:
                                Printer.debugPrint(Printer, "reading entire body")
                                body = openFile.read()
                                response = self.version +" 200 OK\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: " + str(size) + "\r\nLast-Modified: "+ self.getGMT(modified) + "\r\nContent-Type: " + contType + "\r\n\r\n"
                        else:
                            response = self.version +" 200 OK\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: " + str(size) + "\r\nLast-Modified: "+ self.getGMT(modified) + "\r\nContent-Type: " + contType + "\r\n\r\n"
                            
                except IOError as ( number , strerror ):
                    if number == 13:
                        # respnose = self.version +" 403 Forbidden\r\n" +self.serverHeader+ self.getDateHeader() +"Content-Length: 0\r\n\r\n" 
                        body = "You do not have access to this file"
                        response = self.version +" 403 Forbidden\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: "+str(len(body)) + "\r\nContent-Type: " + contType + "\r\n\r\n"

                    elif number == 2:
                        #response = self.version +" 404 File Not Found\r\n" +self.serverHeader+ self.getDateHeader() +"Content-Length: 0\r\n\r\n" 
                        body = "The file you requested could not be found"
                        response = self.version +" 404 File Not Found\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: "+str(len(body)) + "\r\nContent-Type: " + contType + "\r\n\r\n"

                    else :
                        #respnose = self.version + " 500 Internal Server Error\r\n" +self.serverHeader + self.getDateHeader() +"Content-Length: 0\r\n\r\n" 
                        body="the server encountered an internal error... oops"
                        response = self.version +" 500 Internal Server Error\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: "+str(len(body)) + "\r\nContent-Type: " + contType + "\r\n\r\n"


                
            else:
                #return a not implemented error 
                #response = self.version + " 501 Not Implemented\r\n"+self.serverHeader + self.getDateHeader() +"Content-Length: 0\r\n\r\n" 
                body="I don't know how to do that"
                response = self.version +" 501 Not Implemented\r\n"+self.serverHeader + self.getDateHeader() + "Content-Length: "+str(len(body)) + "\r\nContent-Type: " + contType + "\r\n\r\n"



        #4-Generate and transmit the response
            #error code or file or results of script
            #must be a valid HTTP message with appropriate headers
        Printer.debugPrint(Printer, "Headers: \n"+response)
        
        #if this function returnns false then an error occured sending the message
        Printer.debugPrint(Printer, "sending headers")
        if not self.sendToClient(fd, response):
            return True
        
        if(body):
            #if this function returnns false then an error occured sending the message
            Printer.debugPrint(Printer, "sending body")
            if not self.sendToClient(fd, body):
                return True


        self.lastIOs[fd] = time.time()
        return True

    def sendToClient(self, fd, message):
        Printer.debugPrint(Printer, "sending: " + message)
        sent = 0;
        while(sent < len(message)):
            try:
                Printer.debugPrint(Printer, "sending...")
                sent += self.clients[fd].send(message[sent:])
            except socket.error, e:
                error = e.args[0]
                if (error == errno.EAGAIN or error == errno.EWOULDBLOCK):
                    continue
                else:
                    Printer.debugPrint(Printer, "an error occured while sending the response body")
                    Printer.debugPrint(Printer, e)
                    return False

        Printer.debugPrint(Printer, "size sent = " + str(sent))
        return True


    def cleanUpSockets(self):
        """this method checks the last I/O event of each socket and closes those that have been idle too long"""
        Printer.debugPrint(Printer, "cleaning sockets")
        Printer.debugPrint(Printer, self.clients)
        Printer.debugPrint(Printer, self.lastIOs)
        for fd in self.lastIOs.keys():
            if(time.time() - self.lastIOs[fd] > self.timeout):
                self.removeSocket(fd)



    def removeSocket(self, fd):
        """this method unregisters a client and removes all associated information"""
        Printer.debugPrint(Printer, "removing client " + str(fd))
        #remove the cache
        del self.caches[fd]
        #remove the timer
        del self.lastIOs[fd]
        #unregister the client
        self.poller.unregister(fd)
        #close the socket
        self.clients[fd].close()
        #remove the client
        del self.clients[fd]

    def getBadRequestError(self):
        return self.version +" 400 Bad-Request\r\nContent-Length: 0\r\n" +self.getDateHeader()+ self.serverHeader+ "\r\n"
        
    def getDateHeader(self):
        return "Date: "+ self.getGMT(time.time()) + "\r\n"

    def getGMT(self, t):
        gmt = time.gmtime(t)
        dateFormat = '%a %d %b %Y %H:%M:%S GMT'
        time_string = time.strftime ( dateFormat , gmt )
        return time_string
