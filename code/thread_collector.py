from PyQt5.QtCore import QThread
from PyQt5.QtSql import QSqlQuery
import datetime
from time import sleep
from pysnmp.entity.rfc3413.oneliner import cmdgen


def get_param(agent, oid_mib, password='public'):
    oid, mib = oid_mib.split(" ")
    # print(oid,mib,sep=' - ')
    errorIndication, errorStatus, errorIndex, \
    BindTable = cmdgen.CommandGenerator().nextCmd(
        cmdgen.CommunityData(password),
        cmdgen.UdpTransportTarget((agent, 161)),
        (oid))
    print(errorIndication, errorStatus,errorIndex,sep=", ")
    if errorIndication != None:
        return None
    for BindRow in BindTable:
        for name, val in BindRow:
            if mib != name.prettyPrint():
                continue
            return val.prettyPrint()
    return None

class Collector(QThread):
    #parent - class window
    def __init__(self,db,listNodes,listParams,period,parent=None):
        QThread.__init__(self, parent)
        self.running = True
        self.period = period
        self.db = db
        self.agents = listNodes
        self.params = listParams

        self.prev_vals = {}

    def run(self) :
        print("Start collector")
        all_full = 0
        while self.running:
            for i in range(len(self.agents)):
                values = []
                indikator = []
                agent_ip, agent_pass = self.agents[i].split()
                for id_param in range(len(self.params)):
                    check = 0
                    oid, mib, typ = self.params[id_param].split(" ")
                    if typ == "delta":
                        check = 1
                        all_full += 1
                        indikator.append(1)
                    else:
                        indikator.append(0)
                    val = get_param(agent_ip, oid + " " + mib,agent_pass)
                    if val != None:
                        values.append(int(val))
                    else:
                        print('Не удалось получить значение параметра "{0}" у агента "{1}"'.format(mib,agent_ip))
                # agent , values
                print(values)
                if values == []:
                    result = 'агент недоступен'
                    self.prev_vals[agent_ip] = None
                else:
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
                            values = ins_data
                            # result = self.listActs[self.NN.decision(np.array(ins_data))]
                    # elif check == 0:
                        # result = self.listActs[self.NN.decision(np.array(values))]
                    if len(values) != len(self.params):
                        continue
                    self.db.insertData(agent_ip, values)
                # self.db.insertData(agent,values)
            sleep(self.period)
        print("Collector finish the work!")


#print(get_param('10.33.102.97','1.3.6.1.2.1.5.1 SNMPv2-SMI::mib-2.5.1.0'))
