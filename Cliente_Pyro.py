import Pyro5.api
import uuid
import time
import threading

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
    def test(self):
        print('Teste -> ' + id)


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
        ns.register(id, uri)
        daemon.requestLoop()                     # Começa o loop para esperar chamadas


adder = Pyro5.api.Proxy("PYRONAME:Main")
adder.connect(id, ['0.txt', '1.txt'])


try:
    thread1 = myThread()
    thread1.start()
except:
    print(bcolors.FAIL+"[Error] Unable to start thread"+bcolors.ENDC)

try:
    option = -1
    print("\n"+banner)
    while(option != 0):
        option = int(input(
            "\n"+bcolors.OKCYAN+"1 - listar todos os arquivos\n2 - Enviar arquivo\n3 - Teste\n"+bcolors.WARNING+"0 - Sair\n\n"+bcolors.ENDC+"Digite: "))
        if(option == 1):
            print(bcolors.OKGREEN+"\n[Arquivos disponíveis]"+bcolors.ENDC)
            print(adder.listFiles(id))
        elif(option == 2):
            print(option)
        elif(option == 3):
            print(option)
        elif(option == 0):
            print(bcolors.OKGREEN + "\n[!] Bye"+bcolors.ENDC)
        else:
            print(bcolors.FAIL +
                  "\n[!] Essa ai a gente não implementou :|"+bcolors.ENDC)
    print('\n'+bcolors.WARNING+'[INFO] '+bcolors.ENDC+'Press ctrl+c')
except:
    adder.closeConnection(id)

adder.closeConnection(id)
exit(0)
