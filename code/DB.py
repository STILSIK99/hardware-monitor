from PyQt5.QtSql import QSqlDatabase,QSqlQuery,QSqlQueryModel
from PyQt5.QtWidgets import QMessageBox,QWidget
from PyQt5.QtWidgets import QHeaderView

from tensorflow.keras import utils

from datetime import datetime

import numpy as np

def convert(num,step):
    mas = []
    i = 1
    for n in range(step):
        if num & i != 0:
            mas.append(1)
        else:
            mas.append(0)
    return np.array(mas)

class DataBase():
    def __init__(self,parent=None):
        self.sdb = None
        self.modelNodes = None
        self.modelParams = None
        self.ui = parent
        self.modelNData = None
        self.modelPeriods = None
        self.modelActions = None
        self.modelNN = None
        self.rows = None
        self.modelParamsNN = None

    def createDB(self,path):
        self.sdb = QSqlDatabase.addDatabase("QSQLITE")
        self.sdb.setDatabaseName(path)

        if self.sdb.open() != False:
            self.initTables()
            self.updTableNodes()
            self.updTableParams()
            self.updPeriods()
            self.updActions()

    def initTables(self):
        sql = QSqlQuery(self.sdb)
        sql.exec("create table params(id integer primary key autoincrement,name text UNIQUE);")
        print(sql.lastError().text())
        sql.exec("CREATE TABLE nodes (id INTEGER PRIMARY KEY AUTOINCREMENT,address TEXT UNIQUE,name TEXT);")
        print(sql.lastError().text())
        # sql.exec("create table data (address text,paramName text,value text,time TIMESTAMP default CURRENT_TIMESTAMP);")
        # print(sql.lastError().text())
        sql.exec("create table periods(id integer primary key autoincrement,start TIMESTAMP default CURRENT_TIMESTAMP,finish TIMESTAMP default CURRENT_TIMESTAMP,action TEXT);")
        print(sql.lastError().text())
        sql.exec("create table actions (id integer primary key autoincrement,name Text);")
        print(sql.lastError().text())
        sql.exec("create table locked (mean integer)")
        # sql.exec("insert into locked values (1)")
        print(sql.lastError().text())
        sql.exec("CREATE TABLE NN (id_n INTEGER PRIMARY KEY AUTOINCREMENT,name_n VARCHAR (100),    date   TIME_STAMP    DEFAULT CURRENT_TIMESTAMP,data   TEXT);")
        print(sql.lastError().text())
        sql.exec("CREATE TABLE params_nn (id_n  REFERENCES NN (id_n) ON DELETE CASCADE,name TEXT);")
        print(sql.lastError().text())

    def connect(self,path):
        if path == '':
            return False
        self.sdb = QSqlDatabase.addDatabase("QSQLITE")
        self.sdb.setDatabaseName(path)

        if self.sdb.open() != False:
            if self.check() == False:
                QMessageBox.about(QWidget(), 'База данных','Структура базы данных неверна!')
                return False
            self.updTableNodes()
            self.updTableParams()
            self.updPeriods()
            self.updActions()
            self.updTableNN()
            QMessageBox.about(QWidget(), 'База данных', 'База данных подключена!')
            return True

    def del_locked(self):
        sql = QSqlQuery(self.sdb)
        sql.exec("delete locked")

    def del_data(self):
        sql = QSqlQuery(self.sdb)
        sql.exec("drop table data")

    def check(self):
        result = ''
        tables = {}
        tables['actions'] = ['id','name']
        tables['locked'] = ['mean']
        tables['NN'] = ['id_n','name_n','date','data']
        tables['nodes'] = ['id','address','name']
        tables['params'] = ['id','name']
        tables['params_nn'] = ['id_n','name']
        tables['periods'] = ['id','start','finish','action']
        # tables[''] = ['','']
        for key in tables:
            # print(key,tables[key])
            zapr = ''
            for column in tables[key]:
                zapr += column + " ,"
            zapr = zapr[:len(zapr) - 1]
            sql = QSqlQuery()
            sql.exec('select ' + zapr + 'from ' + key + " where 0 = 1")
            result += sql.lastError().text()
        if result != '':
            return False
        return True



    def updActions(self):
        self.modelActions = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select name as 'Состояния сети' from actions")
        self.modelActions.setQuery(sql)
        self.ui.comboBox_2.clear()
        self.ui.comboBox_6.clear()
        self.ui.comboBox_2.setModel(self.modelActions)
        self.ui.comboBox_6.setModel(self.modelActions)
        self.ui.tableView_7.setModel(self.modelActions)
        self.ui.tableView_7.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    def updPeriods(self):
        self.modelPeriods = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select start as 'Начало атаки', finish as 'Конец атаки', action as 'Тип инцидента' from periods")
        self.modelPeriods.setQuery(sql)
        self.ui.tableView_4.setModel(self.modelPeriods)
        self.ui.tableView_4.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.modelPeriods = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select start || ' - ' || finish  || ' - ' || action from periods")

        self.modelPeriods.setQuery(sql)
        self.ui.comboBox_5.setModel(self.modelPeriods)


    def updTableParams(self):
        self.modelParams = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select name as 'Название параметра' from params order by name")
        self.modelParams.setQuery(sql)
        self.ui.tableView_3.setModel(self.modelParams)
        self.ui.tableView_3.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def updTableNodes(self):
        self.modelNodes = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select address as 'Ip адрес',name as 'Описание' from nodes order by address")
        self.modelNodes.setQuery(sql)
        self.ui.tableView.setModel(self.modelNodes)
        self.ui.tableView.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def updTableNN(self):
        self.modelNN = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select name_n || ' - ' || date as 'Нейронная сеть' from NN order by date")
        self.modelNN.setQuery(sql)
        self.ui.tableView_2.setModel(self.modelNN)
        self.ui.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.ui.comboBox.setModel(self.modelNN)
        self.ui.comboBox_8.setModel(self.modelNN)

    def getListNodes(self):
        listNode = []
        sql = QSqlQuery(self.sdb)
        sql.exec("select address from nodes")
        while sql.next():
            listNode.append(sql.value(0))
        return listNode

    def getListParams(self):
        listParams = []
        sql = QSqlQuery(self.sdb)
        sql.exec("select name from params")
        while sql.next():
            listParams.append(sql.value(0))
        return listParams

    def getListPeriods(self):
        listPeriods = []
        sql = QSqlQuery(self.sdb)
        sql.exec("select start,finish from periods order by start")
        while sql.next():
            listPeriods.append(sql.value(0) + " - " + sql.value(1))
        return listPeriods

    def getListActs(self):
        list = []
        sql = QSqlQuery(self.sdb)
        sql.exec("select name from actions")
        while sql.next():
            list.append(sql.value(0))
        return list

    def insertNode(self,ipaddr,descr):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        sql = QSqlQuery(self.sdb)
        sql.exec("insert into nodes values(null,'{0}','{1}') ".format(ipaddr,descr))
        self.updTableNodes()
        if sql.lastError().text() == "":
            print(sql.lastError().text())
            return True
        self.updTableNodes()
        return False

    def insertParam(self,name):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        sql = QSqlQuery(self.sdb)
        sql.exec("insert into params values(null,'{0}') ".format(name))
        self.updTableParams()
        if sql.lastError().text() == "":
            return True
        self.modelParams.select()
        return False

    def insertAction(self,name):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        sql = QSqlQuery(self.sdb)
        sql.exec("insert into actions values(null,'{0}') ".format(name))
        self.updActions()
        if sql.lastError().text() == "":
            return True
        self.modelParams.select()
        print(sql.lastError().text())
        return False

    def insertPeriod(self,start,finish,name):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        sql = QSqlQuery(self.sdb)
        sql.exec("insert into periods values(null,'{0}','{1}','{2}') ".format(start,finish,name))
        self.updPeriods()
        if sql.lastError().text() == "":
            return True
        self.modelPeriods.select()
        return False

    def eraseAct(self,name):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        sql = QSqlQuery(self.sdb)
        sql.exec("delete from actions where name='{0}'".format(name))
        if sql.lastError().text() == "":
            return True
        self.updActions()
        return False

    def eraseParam(self,name):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        sql = QSqlQuery(self.sdb)
        sql.exec("delete from params where name='{0}'".format(name))
        self.updTableParams()
        if sql.lastError().text() == "":
            return True
        self.modelParams.select()
        return False

    def erasePeriod(self,period):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        start,finish,action = period.split(" - ")
        sql = QSqlQuery(self.sdb)
        sql.exec("delete from periods where start='{0}' and finish='{1}' and action = '{2}'".format(start,finish,action))
        self.updPeriods()
        if sql.lastError().text() == "":
            return True
        self.modelParams.select()
        return False

    def eraseNode(self,ipaddr):
        if self.sdb == None:
            QMessageBox.about(None, "Нет подключения", "Подключите базу данных")
            return False
        sql = QSqlQuery(self.sdb)
        sql.exec("delete from nodes where address='{0}'".format(ipaddr))
        self.updTableNodes()
        if sql.lastError().text() == "":
            return True
        self.modelNodes.select()
        return False

    def updNodes(self,ipaddr):
        self.modelNData = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select address as 'Ip адрес',type as 'Тип узла',name as 'Описание' from nodes order by address")
        self.modelNodes.setQuery(sql)
        self.ui.tableView_2.setModel(self.modelNData)
        self.ui.tableView_2.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

    def updParamsNN(self,id):
        self.modelParamsNN = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec("select name as 'Параметр протокола SNMP' from params_nn where id_n = {0} order by name".format(id))
        self.modelParamsNN.setQuery(sql)
        self.ui.tableView_5.setModel(self.modelParamsNN)
        self.ui.tableView_5.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)


    def insData(self,node ,param,value,ttime):
        sql = QSqlQuery(self.sdb)
        sql.exec("insert into data ('{0}','{1}','{2}','{3}')".format(node,param,value,ttime))
        if sql.lastError() != "":
            print(sql.lastError())

    def checkLock(self):
        sql = QSqlQuery(self.sdb)
        sql.exec("select count(*) from locked")
        if sql.next():
            if sql.value(0) > 0:
                return True
        print(sql.lastError().text())
        return False

    def ins_locked(self):
        sql = QSqlQuery(self.sdb)
        sql.exec("insert into locked values (1)")

    def createTableData(self, listParam):
        zapr = "create table data (ip text, time TIMESTAMP default current_timestamp,type integer default 0,"
        for i in range(len(listParam)):
            zapr += "param{0} integer, ".format(i+1)
        zapr = zapr[:len(zapr)-2]
        zapr += ")"
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr)
        print(sql.lastError().text())

    def insertData(self,ip,listValues):
        zapr = "insert into data values ('{0}','{1}',0".format(ip,datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
        for i in range(len(listValues)):
            zapr += "," + str(listValues[i])
        zapr += ')'
        # print(zapr)
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr)
        print(sql.lastError().text())

    def learnTable(self,time1,time2):
        sql = QSqlQuery(self.sdb)
        sql.exec("drop table learn")
        print(sql.lastError().text())
        sql.exec("select count(*) from actions")
        count = 0
        if sql.next():
            count = sql.value(0)
        # bit_action = 1
        # map_keys = {1:0}
        # for i in range(1, count + 1):
        #     bit_action *= 2
        #     map_keys[bit_action] = i
        # del bit_action
        #создали таблицу из выборки, по которой нам надо обучать сеть
        zapr = "CREATE TABLE learn AS SELECT * FROM data where time between '{0}' and '{1}'".format(time1,time2)
        print(zapr)
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr)
        print(sql.lastError().text())
        #выберем инциденты, которые были в этот момент
        zapr_1 = "select * from periods where start between '{0}' and '{1}' or finish between '{0}' and '{1}' or (start < '{0}' and finish > '{1}')"
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr_1.format(time1,time2))
        print(sql.lastError().text())
        while sql.next():
            mn = 2**sql.value(0) #добавляем типо бит
            zapr_2 = "update learn set type = type + {0} where time between '{1}' and '{2}'"
            sql_2 = QSqlQuery(self.sdb)
            sql_2.exec(zapr_2.format(mn,sql.value(1),sql.value(2)))
            print(zapr_2.format(mn,sql.value(1),sql.value(2)))
            print(sql_2.lastError().text())
        #узнать количество параметров в таблице learn
        zapr = "select count(*) from params"
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr)
        print(sql.lastError().text())
        rowCount = None
        if sql.next():
            rowCount = sql.value(0)
        else:
            return []
        #выборка обновленной таблицы
        zapr = "select * from learn"
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr)
        print(sql.lastError().text())
        x_tr = []
        y_tr = []
        while sql.next():
            x = []
            for i in range(rowCount):
                x.append(sql.value(i+3))
            x_tr.append(np.array(x))
            y = sql.value(2)
            # то что здесь + 1 + 1 - это вшито обычное состояние
            if y != 0:
                # state = map_keys[y] + 1
                state = 1
                size = count + 1
                y_tr.append(utils.to_categorical(1, 2))
                # y_tr.append(utils.to_categorical(state, size))
            else:
                y_tr.append(utils.to_categorical(0, 2))
                # y_tr.append(utils.to_categorical(0, count + 1))
        zapr = "drop table learn"
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr)
        print(sql.lastError().text())
        return [np.array(x_tr),np.array(y_tr)]

    def del_NN(self,name_date):
        name,date = name_date.split(' - ')
        sql = QSqlQuery(self.sdb)
        sql.exec("delete from NN where name_n = '{0}' and date = '{1}'".format(name,date))
        print(sql.lastError().text())

    def display_Data(self, zapr):
        model_Data = QSqlQueryModel()
        sql = QSqlQuery(self.sdb)
        sql.exec(zapr)
        print(zapr)
        model_Data.setQuery(sql)
        self.ui.tableView_6.setModel(model_Data)
        self.ui.tableView_6.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        return sql.lastError().text()




