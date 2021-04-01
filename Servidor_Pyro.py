import Pyro5.api
from colors import bcolors
from datetime import datetime
import uuid
# servidor de nomes
# '~/.local/bin/pyro5-ns'

clients = []


class Client:
    def __init__(self, id, files):
        self.id = id
        self.files = files

    def getFiles(self):
        return self.files

    def saveFile(self):
        pass


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
        clients.append(Client(id, files))

        print(bcolors.OKGREEN+"[  CONNECT ]" +
              bcolors.OKCYAN+"["+getFormatedTime()+"]\t"+bcolors.ENDC+id)

    def closeConnection(self, id):
        deleteClient(id)

        print(bcolors.WARNING+"[DISCONNECT]" +
              bcolors.OKCYAN+"["+getFormatedTime()+"]"+"\t"+bcolors.ENDC+id)

    def listFiles(self, id):
        files = []
        for client in clients:
            files.append(client.getFiles())
        return [item for sublist in files for item in sublist]

    def sendFile(self, name, content):
        print(bcolors.OKBLUE+"[RECEIVING-FILE]\t"+bcolors.ENDC+name)

        fileId = uuid.uuid4()
        client = self.loadBalacing()

        proxyClient = Pyro5.api.Proxy("PYRONAME:"+str(client.id))
        fileName = str(fileId)+"-"+name
        response = proxyClient.saveFile(fileName, content)

        if(response == True):
            client.files.append(fileName)
            print(bcolors.OKBLUE+"[  SAVED-FILE  ]\t"+bcolors.ENDC +
                  name+" IN "+bcolors.WARNING+client.id+bcolors.ENDC)
        else:
            print(bcolors.FAIL+"[ UNSAVED-FILE ]\t"+bcolors.ENDC +
                  name+" IN "+bcolors.WARNING+client.id+bcolors.ENDC)

    def loadBalacing(self):
        selected = clients[0]

        for client in clients:
            if(len(client.files) < len(selected.files)):
                selected = client

        return selected


daemon = Pyro5.server.Daemon()           # cria um daemon
ns = Pyro5.api.locate_ns()               # encontra o servidor de nomes

uri = daemon.register(GlobalFunctions)   # Registra como um objeto Pyro


# Registra um objeto com um nome no servidor de nomes
ns.register("Main", uri)


print("Server ready")
daemon.requestLoop()                     # Começa o loop para esperar chamadas
