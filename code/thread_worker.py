
from PyQt5.QtCore import QThread
from PyQt5.QtSql import QSqlQuery
from datetime import datetime
from time import sleep
from pysnmp.entity.rfc3413.oneliner import cmdgen
import numpy as np
from thread_waiter import Waiter

def get_param(agent, oid_mib, password='public'):
    oid, mib = oid_mib.split(" ")
    # print(oid,mib,sep=' - ')
    errorIndication, errorStatus, errorIndex, \
    BindTable = cmdgen.CommandGenerator().nextCmd(
        cmdgen.CommunityData(password),
        cmdgen.UdpTransportTarget((agent, 161)),
        (oid))
    # print(errorIndication, errorStatus,errorIndex,sep=", ")
    if errorIndication != None:
        return None
    for BindRow in BindTable:
        for name, val in BindRow:
            if mib != name.prettyPrint():
                continue
            return val.prettyPrint()
    return None


class Worker(QThread):
    #parent - class window
    def __init__(self,NN,listNodes,listParams,acts,period,textEdit,parent=None):
        QThread.__init__(self, parent)
        self.running = True
        self.period = period
        self.NN = NN
        self.agents = listNodes
        self.params = listParams
        self.textEdit = textEdit
        self.listActs = ["Обычное состояние"] + acts
        self.waiter = Waiter(self,period,textEdit)
        self.prev_vals = {}

    def run(self) :
        print("Start worker")
        #Сбор данных
        all_full = 0
        self.waiter.start()
        while self.running:
            for i in range(len(self.agents)):
                values = []
                indikator = []
                agent_ip, agent_pass = self.agents[i].split()
                if self.waiter.answer.get(agent_ip) == None:
                    self.waiter.answer[agent_ip] = 0
                for id_param in range(len(self.params)):
                    check = 0
                    oid, mib, type = self.params[id_param].split(" ")
                    if type == "delta":
                        check = 1
                        all_full += 1
                        indikator.append(1)
                    else:
                        indikator.append(0)
                    val = get_param(agent_ip, oid + " " + mib,agent_pass)
                    if val != None:
                        self.waiter.answer[agent_ip] += 1
                        values.append(int(val))
                    else:
                        print('Не удалось получить значение параметра "{0}" у агента "{1}"'.format(mib, agent_ip))
                # Проверка результата через нейронную сеть
                # agent , values
                if values == []:
                    result = 'Не удается собрать параметры'
                    self.prev_vals[agent_ip] = None
                else:
                    self.waiter.answer[agent_ip] += 1
                    if check == 1:
                        if self.prev_vals.get(agent_ip) == None:
                            self.prev_vals[agent_ip] = values
                            continue
                        else:
                            prev = self.prev_vals.get(agent_ip)
                            ins_data = []
                            for j in range(len(prev)):
                                if indikator[j] == 0:
                                    ins_data.append(values[j])
                                else:
                                    ins_data.append(abs(prev[j] - values[j]))
                            self.prev_vals[agent_ip] = values
                            result = self.NN.decision(np.array(ins_data))
                            if result != None:
                                result = self.listActs[result]
                    elif check == 0:
                        result = self.NN.decision(np.array(values))
                        if result != None:
                            result = self.listActs[result]
                        else:
                            result = self.listActs[1]

                if result!= None:
                    self.textEdit.append(datetime.now().strftime("%H:%M:%S ") + "{0}:  состояние - {1}".format(agent_ip,result))
                    # self.db.insertData(agent,values)
            sleep(self.period)
        self.waiter.running = False
        print("Worker finish the work!")


# print(get_params('192.168.110.141',['SNMPv2-SMI::mib-2.2.2.1.10.1','SNMPv2-SMI::mib-2.2.2.1.17.1']))