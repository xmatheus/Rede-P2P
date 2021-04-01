# servidor de nomes
# '~/.local/bin/pyro5-ns'
import Pyro5.api
from colors import bcolors
from datetime import datetime
import uuid

from Log import Log

clients = []
log = Log('servidor-log.txt')


class Client:
    def __init__(self, id, files):
        self.id = id
        self.files = files

    def getFiles(self):
        return self.files


def deleteClient(id):
    for client in clients:
        if(client.id == id):
            clients.remove(client)


def getFormatedTime():
    now = datetime.now()
    return ('%02d:%02d.%d' %
            (now.minute, now.second, now.microsecond))[:-4]


@Pyro5.api.expose
class GlobalFunctions(object):

    def connect(self, id, files):
        log.save("USER-CONNECT", id)
        clients.append(Client(id, files))

        print(bcolors.OKGREEN+"[  CONNECT ]" +
              bcolors.OKCYAN+"["+getFormatedTime()+"]\t"+bcolors.ENDC+id)

    def closeConnection(self, id):
        log.save("USER-DISCONNECT", id)
        deleteClient(id)

        print(bcolors.WARNING+"[DISCONNECT]" +
              bcolors.OKCYAN+"["+getFormatedTime()+"]"+"\t"+bcolors.ENDC+id)

    def listFiles(self, id):
        log.save("USER-REQUEST-LIST-FILES", id)
        files = []
        for client in clients:
            files.append(client.getFiles())
        return [item for sublist in files for item in sublist]

    def appendFile(self, fileName, clientId):
        for client in clients:
            if(clientId == client.id):
                client.files.append(fileName)

    def loadBalacing(self, clientId):
        print(bcolors.OKBLUE+"[SENDING-FILE]\t"+bcolors.ENDC)

        selected = clients[0]

        for client in clients:
            if(len(client.files) < len(selected.files)):
                selected = client

        log.save("USER-REQUEST-SEND-FILE", "from " +
                 str(clientId)+" to "+selected.id)
        return selected.id

    def getFile(self, fileName):
        log.save("USER-REQUEST-FILE", fileName)

        for client in clients:
            for file in client.files:
                if(file == fileName):
                    return client.id
        raise Exception("Arquivo não encontrado")


daemon = Pyro5.server.Daemon()           # cria um daemon
ns = Pyro5.api.locate_ns()               # encontra o servidor de nomes

uri = daemon.register(GlobalFunctions)   # Registra como um objeto Pyro


# Registra um objeto com um nome no servidor de nomes
ns.register("Main", uri)


print("Server ready")
daemon.requestLoop()                     # Começa o loop para esperar chamadas
