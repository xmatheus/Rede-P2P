# servidor de nomes
# '~/.local/bin/pyro5-ns'

import Pyro5.api
from Colors import bcolors
from datetime import datetime
import uuid
import threading

from Log import Log


log = Log('servidor-log.txt')
clients = []


class Client:
    backup = False

    def __init__(self, id, files, admin, backup=False):
        self.id = id
        self.files = files
        self.admin = admin
        self.backup = backup

    def getFiles(self):
        return self.files


def getFormatedTime():
    now = datetime.now()
    return ('%02d:%02d.%d' %
            (now.minute, now.second, now.microsecond))[:-4]


class ServidorBackup(threading.Thread):

    def __init__(self, clientId, filename='', content='', otherClientId=''):
        threading.Thread.__init__(self)
        self.clientId = clientId
        self.filename = filename
        self.content = content
        self.otherClientId = otherClientId

    def run(self):

        proxyClient = Pyro5.api.Proxy("PYRONAME:"+str(self.clientId))

        if(self.clientId != self.otherClientId):
            proxyClient.saveFile('backup-'+self.filename,
                                 self.content, self.clientId)

        proxyClient.clearBackup()

        for cl in clients:
            proxyClient.backup(cl.id, cl.admin, cl.backup, cl.files)


@Pyro5.api.expose
class GlobalFunctions(object):

    def __init__(self, oldClients=[]):
        clients = oldClients

    def connect(self, files, admin):
        id = str(uuid.uuid4())
        log.save("USER-CONNECT", id)

        # limitacao de 50 clientes(definido no escopo do trabalho)
        if(len(clients) > 50):
            log.save("LIMIT-REACHED", '50')
            raise Exception("Máximo de clientes conectados")

        self.newClient(id, files, admin)

        print(bcolors.OKGREEN+"\n[  CONNECT ]" +
              bcolors.OKCYAN+"["+getFormatedTime()+"]\t"+bcolors.ENDC+id)
        return id

    def closeConnection(self, id):
        log.save("USER-DISCONNECT", id)

        print(bcolors.WARNING+"[DISCONNECT]" +
              bcolors.OKCYAN+"["+getFormatedTime()+"]"+"\t"+bcolors.ENDC+id)

        return self.__deleteClient(id)

    def listFiles(self, id):
        log.save("USER-REQUEST-LIST-FILES", id)
        files = []
        for client in clients:
            files.append(client.getFiles())
        return [item for sublist in files for item in sublist]

    def _selectClientBackup(self):
        for client in clients:
            if(client.backup and not client.admin):
                return client

        for client in clients:
            if(not client.admin):
                client.backup = True
                return client

        return False

    def _checkBackup(self, filename='', content='', clientId=''):
        # need broadcast

        client = self._selectClientBackup()
        if(client):
            try:
                thread1 = ServidorBackup(
                    client.id, filename, content, clientId)
                thread1.daemon = True
                thread1.start()
            except Exception as error:
                print(error)
                print("[ERROR] backup failed")

    def appendFile(self, filename, clientId, content):
        for client in clients:
            if(clientId == client.id):
                client.files.append(filename)

        # self._checkBackup(filename, content, clientId)

    def newClient(self, id, files, admin):
        clients.append(Client(id, files, admin))
        # self._checkBackup()

    def loadBalacing(self, clientId):
        print(bcolors.OKBLUE+"[RECEIVING-SEND-FILE-REQUEST]" +
              bcolors.OKCYAN+"["+getFormatedTime()+"]" +
              bcolors.ENDC+"\tfrom "+str(clientId))

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

    def __deleteClient(self, id):
        for client in clients:
            if(client.id == id):
                clients.remove(client)

                if(client.admin):
                    return clients[0].id
                return False

    def getClients(self):
        return clients


class Servidor:
    def __init__(self):
        daemon = Pyro5.server.Daemon()           # cria um daemon
        ns = Pyro5.api.locate_ns()               # encontra o servidor de nomes

        uri = daemon.register(GlobalFunctions)   # Registra como um objeto Pyro

        # Registra um objeto com um nome no servidor de nomes
        ns.register("Main", uri)

        daemon.requestLoop()
