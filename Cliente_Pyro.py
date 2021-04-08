import Pyro5.api
import uuid
import time
import threading
import os

from Colors import bcolors
from Log import Log

log = Log('client-log.txt')
banner = ("""\
██████╗ ██████╗ ██████╗     ████████╗██████╗  █████╗ ██████╗  █████╗ ██╗     ██╗  ██╗ ██████╗
██╔══██╗╚════██╗██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║     ██║  ██║██╔═══██╗
██████╔╝ █████╔╝██████╔╝       ██║   ██████╔╝███████║██████╔╝███████║██║     ███████║██║   ██║
██╔═══╝ ██╔═══╝ ██╔═══╝        ██║   ██╔══██╗██╔══██║██╔══██╗██╔══██║██║     ██╔══██║██║   ██║
██║     ███████╗██║            ██║   ██║  ██║██║  ██║██████╔╝██║  ██║███████╗██║  ██║╚██████╔╝
╚═╝     ╚══════╝╚═╝            ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝""")


@ Pyro5.api.expose
class GlobalFunctions(object):
    def saveFile(self, name, content, clientId):
        try:
            with open('./user-files/'+name, 'a') as output:
                output.write(content)
            # print("\n[ACESSO-EXTERNO] Recendo arquivo")
            log.save("LOCAL-FILE-SAVED", name + " from "+str(clientId))
            return True
        except:
            return False

    def getFile(self, fileName):
        file = open('./user-files/'+fileName, "r")
        return file.read()


class MyThread (threading.Thread):
    def __init__(self, id):
        self.clientId = id
        threading.Thread.__init__(self)

    def run(self):
        self.servidorStart()

    def servidorStart(self):
        daemon = Pyro5.server.Daemon()           # cria um daemon
        ns = Pyro5.api.locate_ns()               # encontra o servidor de nomes
        uri = daemon.register(GlobalFunctions)   # Registra como um objeto Pyro
        # Registra um objeto com um nome no servidor de nomes
        ns.register(str(self.clientId), uri)
        daemon.requestLoop()                     # Começa o loop para esperar chamadas


class Client():
    def __init__(self):
        self.localFiles = self.loadFiles()
        self.adder = Pyro5.api.Proxy("PYRONAME:Main")
        self.id = self.adder.connect(self.localFiles)

    def loadFiles(self):
        if not os.path.exists('user-files'):
            os.makedirs('user-files')

        arr = os.listdir('./user-files/')
        return arr

    def listFiles(self):
        self.localFiles = self.loadFiles()
        files = self.adder.listFiles(self.id)

        log.save('LIST-ALL-FILES', "LENGTH => "+str(len(files)))
        print(bcolors.OKGREEN +
              "\n[Arquivos disponíveis] => "+bcolors.ENDC+str(len(files))+"\n")

        for file in files:
            if(file in self.localFiles):
                print(bcolors.OKGREEN+"[ LOCAL ] "+bcolors.ENDC+file)
            else:
                print(bcolors.WARNING+"[EXTERNO] "+bcolors.ENDC+file)

    def readFile(self):
        fileName = input("Digite o nome do arquivo: ")

        if(fileName in self.localFiles):
            # nao precisa ir no ADMIN para achar o arquivo
            log.save('READ-LOCAL-FILE', fileName)

            print(bcolors.OKGREEN+"\n[CONTEÚDO]"+bcolors.ENDC)
            print(GlobalFunctions().getFile(fileName))
            return

        # arquivo ta fora da maquina
        try:
            otherClientId = self.adder.getFile(fileName)
            log.save('READ-EXTERNAL-FILE', fileName +
                     " from "+str(otherClientId))

            proxyClient = Pyro5.api.Proxy("PYRONAME:"+str(otherClientId))
            response = proxyClient.getFile(fileName)

            print(bcolors.OKGREEN+"\n[CONTEÚDO]"+bcolors.ENDC)
            print(response)
        except Exception as error:
            print(error)

    def connectToAnotherClient(self, anotherClientID, name, content):
        proxyClient = Pyro5.api.Proxy("PYRONAME:"+str(anotherClientID))
        fileId = uuid.uuid4()
        fileName = str(fileId)+"-"+name
        response = proxyClient.saveFile(fileName, content, self.id)

        if(response == True):
            log.save("SEND-FILE-SUCESS", "from " +
                     str(self.id)+" to "+str(anotherClientID))

            print(bcolors.OKBLUE+"[  SAVED-FILE  ]\t"+bcolors.ENDC +
                  name+" IN "+bcolors.WARNING+anotherClientID+bcolors.ENDC)

            self.adder.appendFile(fileName, anotherClientID)
        else:
            log.save("SEND-FILE-FAIL", "from " +
                     str(self.id)+" to "+str(anotherClientID))

            print(bcolors.FAIL+"[ UNSAVED-FILE ]\t"+bcolors.ENDC +
                  name+" IN "+bcolors.WARNING+anotherClientID+bcolors.ENDC)

    def sendFile(self):
        fileName = input("Nome do arquivo: ")
        content = input("Conteúdo: ")

        anotherClientID = self.adder.loadBalacing(self.id)
        self.connectToAnotherClient(anotherClientID, fileName, content)

    def disconnect(self):
        self.adder.closeConnection(self.id)
        exit(0)


client = Client()

try:
    thread1 = MyThread(client.id)
    thread1.start()
except:
    print(bcolors.FAIL+"[Error] não deu para iniciar uma thread"+bcolors.ENDC)

try:
    option = '-1'
    print("\n"+banner)
    while(option != '0'):
        option = input(
            "\n"+bcolors.OKCYAN+"1 - listar todos os arquivos\n2 - Enviar arquivo\n3 - Abrir arquivo\n"+bcolors.WARNING+"0 - Sair\n\n"+bcolors.ENDC+"Opção: ")
        if(option == '1'):
            client.listFiles()
        elif(option == '2'):
            client.sendFile()
        elif(option == '3'):
            client.readFile()

        elif(option == '0'):
            log.save("DISCONNECT", '')
            print(bcolors.OKGREEN + "\n[!] Bye"+bcolors.ENDC)

        else:
            print(bcolors.FAIL +
                  "\n[!] Essa ai a gente não implementou :|"+bcolors.ENDC)

    print('\n'+bcolors.WARNING+'[INFO] '+bcolors.ENDC+'Press ctrl+c')

except KeyboardInterrupt:
    print(bcolors.OKGREEN+"\n[!] Bye"+bcolors.ENDC)
    print('\n'+bcolors.WARNING+'[INFO] '+bcolors.ENDC+'Press ctrl+c')

except Exception as error:
    print(bcolors.FAIL+"[Error] falha no menu"+bcolors.ENDC)
    print(error)

client.disconnect()
