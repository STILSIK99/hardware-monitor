from PyQt5.QtCore import QThread
from time import sleep
from datetime import datetime

class Waiter(QThread):
    #parent - class window
    def __init__(self, parent, period, textEdit):
        QThread.__init__(self, parent)
        self.running = True
        self.parent = parent
        self.answer = {}
        self.period = 5 * period
        self.textEdit = textEdit
        self.running = True


    def run(self) :
        sleep(self.period)
        while self.running:
            print(self.answer)
            # print("Waiter check - {}".format(datetime.now().strftime("%H:%M:%S ")))
            for key in self.answer:
                if self.answer.get(key) == 0:
                    self.textEdit.append(datetime.now().strftime("%H:%M:%S ") + "{0}:  состояние - {1}".format(key,"Агент не отвечает"))
                else:
                    self.answer[key] = 0
            sleep(self.period)







