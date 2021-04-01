import Pyro5.api
from colors import bcolors
# servidor de nomes
# '~/.local/bin/pyro5-ns'

clients = []


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


@Pyro5.api.expose
class GlobalFunctions(object):

    def connect(self, id, files):
        clients.append(Client(id, files))

        print(bcolors.OKGREEN+"[  CONNECT ]\t"+bcolors.ENDC+id)

    def closeConnection(self, id):
        deleteClient(id)
        print(bcolors.WARNING+"[DISCONNECT]\t"+bcolors.ENDC+id)

    def listFiles(self, id):
        files = []
        for client in clients:
            files.append(client.getFiles())
        return [item for sublist in files for item in sublist]
        # proxyClient = Pyro5.api.Proxy("PYRONAME:"+id)
        # proxyClient.test(files)


daemon = Pyro5.server.Daemon()           # cria um daemon
ns = Pyro5.api.locate_ns()               # encontra o servidor de nomes

uri = daemon.register(GlobalFunctions)   # Registra como um objeto Pyro


# Registra um objeto com um nome no servidor de nomes
ns.register("Main", uri)


print("Server ready")
daemon.requestLoop()                     # Começa o loop para esperar chamadas
