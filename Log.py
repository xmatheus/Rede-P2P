from datetime import datetime


def getFormatedTime():
    now = datetime.now()
    return ('%02d:%02d.%d' %
            (now.minute, now.second, now.microsecond))[:-4]


class Log:
    def __init__(self, fileName):
        self.fileName = fileName

    def save(self, title, msg):
        log_file = open(self.fileName, 'a')
        log_file.write("["+title+"]["+getFormatedTime()+"] "+str(msg)+"\n")
