import Pyro5.api
import uuid
import time
import threading
import os

from colors import bcolors

id = uuid.uuid4()
banner = ("""\
██████╗ ██████╗ ██████╗     ████████╗██████╗  █████╗ ██████╗  █████╗ ██╗     ██╗  ██╗ ██████╗
██╔══██╗╚════██╗██╔══██╗    ╚══██╔══╝██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║     ██║  ██║██╔═══██╗
██████╔╝ █████╔╝██████╔╝       ██║   ██████╔╝███████║██████╔╝███████║██║     ███████║██║   ██║
██╔═══╝ ██╔═══╝ ██╔═══╝        ██║   ██╔══██╗██╔══██║██╔══██╗██╔══██║██║     ██╔══██║██║   ██║
██║     ███████╗██║            ██║   ██║  ██║██║  ██║██████╔╝██║  ██║███████╗██║  ██║╚██████╔╝
╚═╝     ╚══════╝╚═╝            ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝""")


@ Pyro5.api.expose
class GlobalFunctions(object):
    def saveFile(self, name, content):
        try:
            with open('./user-files/'+name, 'a') as output:
                output.write(content)
            return True
        except:
            return False


class myThread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        # print("Thread start")
        self.servidorStart()

    def servidorStart(self):
        daemon = Pyro5.server.Daemon()           # cria um daemon
        ns = Pyro5.api.locate_ns()               # encontra o servidor de nomes
        uri = daemon.register(GlobalFunctions)   # Registra como um objeto Pyro
        # Registra um objeto com um nome no servidor de nomes
        ns.register(str(id), uri)
        daemon.requestLoop()                     # Começa o loop para esperar chamadas


def loadFiles():
    if not os.path.exists('user-files'):
        os.makedirs('user-files')

    arr = os.listdir('./user-files/')
    return arr


localFiles = loadFiles()

adder = Pyro5.api.Proxy("PYRONAME:Main")
adder.connect(id, localFiles)


try:
    thread1 = myThread()
    thread1.start()
except:
    print(bcolors.FAIL+"[Error] não deu para iniciar uma thread"+bcolors.ENDC)

try:
    option = -1
    print("\n"+banner)
    while(option != 0):
        option = int(input(
            "\n"+bcolors.OKCYAN+"1 - listar todos os arquivos\n2 - Enviar arquivo\n3 - Teste\n"+bcolors.WARNING+"0 - Sair\n\n"+bcolors.ENDC+"Opção: "))
        if(option == 1):
            files = adder.listFiles(id)
            print(bcolors.OKGREEN +
                  "\n[Arquivos disponíveis] => "+bcolors.ENDC+str(len(files)))
            print(files)

        elif(option == 2):
            fileName = input("Nome do arquivo: ")
            content = input("Conteúdo: ")
            adder.sendFile(fileName, content)

        elif(option == 3):
            print(option)

        elif(option == 0):
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

adder.closeConnection(id)
exit(0)
