import sys
import ipaddress as ip
from time import sleep

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtGui import QRegExpValidator,QMovie
from PyQt5.QtCore import QRegExp,Qt,QDateTime

from thread_collector import Collector
from thread_worker import Worker
# from thread_waiter import Waiter

from DB import DataBase
from NN import NN_model
from UI_statBar import StatBar
from UI_mainform import Ui_MainWindow


class mywindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(mywindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.name = 'Анализатор сети'

        #инициализация новых ресурсов
        self.db = DataBase(self.ui)
        self.listNodes = []
        self.listParams = []
        self.listPeriods = []
        self.listActs = []
        self.listDecisions = []
        #threads
        self.collector = None
        self.worker = None
        self.waiter = None
        #self.thread.main = self
        #период сбора данных
        try:
            with open("config\config.txt") as f:
                import json
                self.config = json.load(f)
            self.PD = self.config['period']
        except json.JSONDecodeError:
            QMessageBox.about(self, self.name, "Неверный конфигурационный файл!")
            exit()
        self.NN = NN_model([], '', [])


        #Worker thread
        self.agentsAddress = []
        self.agentsNames = []

        #слоты сигналы
        self.ui.pushButton.clicked.connect(self.add_Node)
        self.ui.pushButton_2.clicked.connect(self.del_Node)
        self.ui.pushButton_3.clicked.connect(self.add_Param)
        self.ui.pushButton_4.clicked.connect(self.del_Param)
        self.ui.pushButton_5.clicked.connect(self.add_Period)
        self.ui.pushButton_6.clicked.connect(self.del_Period)
        self.ui.pushButton_8.clicked.connect(self.add_AgentWorker)
        self.ui.pushButton_9.clicked.connect(self.add_AgentsWorker)
        self.ui.pushButton_10.clicked.connect(self.add_ListParams)
        self.ui.pushButton_11.clicked.connect(self.del_AgentWorker)
        self.ui.pushButton_12.clicked.connect(self.add_Act)
        self.ui.pushButton_13.clicked.connect(self.del_Act)
        self.ui.pushButton_7.clicked.connect(self.del_NN)
        self.ui.pushButton_14.clicked.connect(self.load_NN)
        self.ui.pushButton_15.clicked.connect(self.create_NN)
        self.ui.pushButton_16.clicked.connect(self.save_NN)
        self.ui.pushButton_17.clicked.connect(self.learn_NN)
        self.ui.pushButton_18.clicked.connect(self.start_Collector)
        self.ui.pushButton_19.clicked.connect(self.stop_Collector)
        self.ui.pushButton_20.clicked.connect(self.add_Nodes)
        self.ui.pushButton_21.clicked.connect(self.filter_Data)
        self.ui.pushButton_22.clicked.connect(self.stop_Worker)
        self.ui.pushButton_23.clicked.connect(self.start_Worker)
        # self.ui.pushButton_24.clicked.connect(self.dialog_show)

        self.ui.menu.actions()[0].triggered.connect(self.open_DB)
        self.ui.menu.actions()[0].setShortcut("Ctrl+O")
        self.ui.menu.actions()[1].triggered.connect(self.create_DB)
        self.ui.menu.actions()[1].setShortcut("Ctrl+S")
        self.ui.menu.actions()[3].triggered.connect(self.exit_Prog)
        self.ui.menu.actions()[3].setShortcut("Ctrl+E")

        self.ui.menu_2.actions()[0].triggered.connect(self.turn_collect)
        self.ui.menu_2.actions()[0].setShortcut("Ctrl+C")
        self.ui.menu_2.actions()[2].triggered.connect(self.turn_manage)
        self.ui.menu_2.actions()[2].setShortcut("Ctrl+M")


        self.ui.lineEdit.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")))
        self.ui.lineEdit_5.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")))
        self.ui.lineEdit_9.setValidator(QRegExpValidator(QRegExp("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")))

        d = QDateTime.currentDateTime()
        self.ui.dateTimeEdit.setDateTime(d)
        self.ui.dateTimeEdit_2.setDateTime(d)
        self.ui.dateTimeEdit_3.setDateTime(d)
        self.ui.dateTimeEdit_4.setDateTime(d)
        self.ui.dateTimeEdit_5.setDateTime(d)
        self.ui.dateTimeEdit_6.setDateTime(d)
        # self.ui.dateTimeEdit_3.setDateTime(d)
        # self.ui.dateTimeEdit_4.setDateTime(d)

        self.statBar = StatBar(self.ui.label_16)
        self.statBar.append('DataBase', 'Не подключена')
        # self.load_dialog = dialog()
        # self.load_dialog
        from os import getcwd
        self.path = getcwd()
        self.ui.tabWidget.setCurrentIndex(0)


    def add_Nodes(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name,"База данных не подключена")
            return
        path = \
            QFileDialog.getOpenFileName(self, "Выберите файл c агентами мониторинга состояния", self.path, 'Text files (*.txt)')[0]
        if path == "":
            return
        with open(path, 'r') as ff:
            list = ff.read().splitlines()
        count = 0
        flagCon = 0
        for ag in list:
            try:
                if ag == '':
                    continue
                name, address = ag.split(":")
            except ValueError:
                flagCon = 1
                continue
            if self.db.insertNode(address, name) == True:
                self.listNodes.append(address)
                self.ui.lineEdit.setText("")
                self.ui.lineEdit_2.setText("")
                count += 1
        if flagCon == 1:
            QMessageBox.about(self, self.name, "Неверная структура данных агента.\nПопробуйте подключить вручную.")
        QMessageBox.about(self, "Добавление узлов", "Добавлено количество узлов: {}.".format(count))
        self.updNodes()



    def swap_images(self, r):
        if r == 0:
            self.ui.groupBox_25.show()
            self.ui.tabWidget_2.hide()
        else:
            self.ui.groupBox_25.hide()
            self.ui.tabWidget_2.show()


    def turn_collect(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name,"База данных не подключена")
            return
        self.db.createTableData(self.listParams)
        self.db.ins_locked()
        self.lock_man()


    def turn_manage(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        reply = QMessageBox.question(self, self.name, "Если вы включите управление, то собранные\n ранее данные будут удалены, включить?")
        if reply == QMessageBox.No:
            return
        self.stop_Collector()
        self.stop_Worker()
        self.waiter_1()

        # self.gif.start()
        # self.swap_images(0)
        # sleep(5)
        # wait = Waiter(self, 1)
        # wait.start()

    def lock_col(self):
        self.db.del_locked()
        self.ui.pushButton_18.setEnabled(False)
        self.ui.pushButton_19.setEnabled(False)
        self.ui.pushButton_3.setEnabled(True)
        self.ui.pushButton_4.setEnabled(True)
        self.ui.pushButton_10.setEnabled(True)

    def lock_man(self):
        self.ui.pushButton_3.setEnabled(False)
        self.ui.pushButton_4.setEnabled(False)
        self.ui.pushButton_10.setEnabled(False)
        self.ui.pushButton_18.setEnabled(True)
        self.ui.pushButton_19.setEnabled(True)


    def start_Collector(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.collector != None:
            return
        self.collector = Collector(self.db, self.listNodes,self.listParams,self.PD)
        self.collector.start()
        self.statBar.append('collector', 'on')


    def stop_Collector(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.collector != None:
            self.collector.running = False
        self.collector = None
        self.statBar.append('collector', 'off')

    def add_Act(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.ui.lineEdit_7.text() == "":
            QMessageBox.about(self, self.name, "Введите название типа инцидентов!")
            return
        self.db.insertAction(self.ui.lineEdit_7.text())
        self.ui.lineEdit_7.setText("")

    def waiter_0(self):
        self.close()

    def waiter_1(self):
        self.db.del_data()
        self.lock_col()

    def waiter_2(self):
        ...

    def add_ListParams(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        path = QFileDialog.getOpenFileName(self, "Выберите файл с параметрами", self.path, "Text file (*.txt)")[0]
        if path == "":
            return
        with open(path, 'r') as f:
            list = f.read().splitlines()
        for i in list:
            if i == "":
                continue
            self.db.insertParam(i)
        self.updParams()


    def change_PD(self):
        if len(self.ui.lineEdit_4.text()) != 0:
            self.PD = int(self.ui.lineEdit_4.text())

    def create_DB(self):
        if self.db.sdb != None:
            reply = QMessageBox.question(self, "Подтверждение","База данных уже подключена, переподключить?")
            if reply == QMessageBox.Yes:
                path = QFileDialog.getSaveFileName(self, "Выберите путь для сохранениния БД", self.path, "DataBase (*.db)")[0]
                if path == "":
                    return
                self.db.createDB(path)
                self.statBar.append('DataBase', path)
                self.updNodes()
                self.updParams()
                if self.db.checkLock() == True:
                    self.lock_man()
                else:
                    self.lock_col()
                return
        path = QFileDialog.getSaveFileName(self, "Выберите путь для сохранениния БД", self.path, "DataBase (*.db)")[0]
        if path == "":
            return
        self.db.createDB(path)
        self.statBar.append('DataBase',path)
        self.updNodes()
        self.updParams()
        if self.db.checkLock() == True:
            self.lock_man()
        else:
            self.lock_col()

    def open_DB(self):
        if self.db.sdb != None:
            reply = QMessageBox.question(self, "Подтверждение","База данных уже подключена, переподключить?")
            if reply == QMessageBox.Yes:
                path = QFileDialog.getOpenFileName(self,"Выберите файл базы данных",self.path ,'DataBase (*.db)')[0]
                if path == "":
                    return
                if self.db.connect(path) == False:
                    QMessageBox.about(self, self.name, "Не удалось подключить базу данных!")
                    return
                self.updNodes()
                self.updParams()
                self.statBar.append('DataBase', path)
                if self.db.checkLock() == True:
                    self.lock_man()
                else:
                    self.lock_col()
                return
        path = QFileDialog.getOpenFileName(self, "Выберите файл базы данных", self.path, 'DataBase (*.db)')[0]
        if path == "":
            return
        if self.db.connect(path) == False:
            QMessageBox.about(self, self.name, "Не удалось подключить базу данных!")
            return
        self.updNodes()
        self.updParams()
        self.statBar.append('DataBase',path)
        # self.listActs = self.db.getListActs()
        self.listActs = ["Обычное состояние", "Аномальное состояние"]
        if self.db.checkLock() == True:
            self.lock_man()
        else:
            self.lock_col()

    def updNodes(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        self.listNodes = sorted(self.db.getListNodes())
        self.ui.comboBox_2.clear()
        self.ui.comboBox_2.addItems(self.listNodes)
        self.ui.comboBox_3.clear()
        self.ui.comboBox_3.addItems(self.listNodes)

    def updParams(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        self.listParams = sorted(self.db.getListParams())
        self.ui.comboBox_4.clear()
        self.ui.comboBox_4.addItems(self.listParams)

    def updPeriods(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        self.listPeriods = self.db.getListPeriods()
        self.ui.comboBox_5.clear()
        self.ui.comboBox_5.addItems(self.listPeriods)

    def add_Node(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        try:
            ip.ip_address(self.ui.lineEdit.text())
        except ValueError:
            QMessageBox.about(self,"Неверные данные","Неверный Ip адрес")
            return
        node = None
        passw = 'public'
        if self.ui.lineEdit.text() not in self.listNodes:
            node = self.ui.lineEdit.text()
        if self.ui.lineEdit_2.text() == "":
            QMessageBox.about(self,"Неверные данные", "Пустое описание узла")
            return
        name = self.ui.lineEdit_2.text()
        if self.ui.lineEdit_12.text() != "":
            passw = self.ui.lineEdit_12.text()
        else:
            QMessageBox.about(self, "Добавление узла", "Использован пароль по умолчанию.")
        if self.db.insertNode(node + " " + passw, name) == True:
            self.listNodes.append(node + " " + passw)
            self.ui.lineEdit.setText("")
            self.ui.lineEdit_2.setText("")

            QMessageBox.about(self, "Обновление", "Узел добавлен")
        else:
            QMessageBox.about(self, "Неверные данные", "Узел не добавлен")
        self.updNodes()

    def del_Node(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.ui.comboBox_3.count() == 0:
            QMessageBox.about(self, self.name, "Список агентов пуст!")
            return
        reply = QMessageBox.question(self,"Подтверждение","Удалить узел {0}?".format(self.ui.comboBox_3.currentText()))
        if reply == QMessageBox.Yes:
            self.db.eraseNode(self.ui.comboBox_3.currentText())
            self.updNodes()

    def del_Act(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.ui.comboBox_4.count() == 0:
            QMessageBox.about(self, self.name, "Список инцидентов пуст!")
            return
        reply = QMessageBox.question(self, "Подтверждение",
                                     "Удалить тип инцидентов {0}?".format(self.ui.comboBox_6.currentText()))
        if reply == QMessageBox.Yes:
            self.db.eraseAct(self.ui.comboBox_6.currentText())
            self.db.updActions()

    def add_Param(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.ui.lineEdit_3.text() == "" or self.ui.lineEdit_8.text() == "":
            QMessageBox.about(self, self.name, "Заданы не все данные параметра!")
            return
        self.db.insertParam(self.ui.lineEdit_3.text() + " " + self.ui.lineEdit_8.text() + " " + self.ui.comboBox_9.currentText())
        self.updParams()
        self.ui.lineEdit_3.setText("")
        self.ui.lineEdit_8.setText("")


    def del_Param(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.ui.comboBox_4.count() == 0:
            QMessageBox.about(self, self.name, "Список параметров пуст!")
            return
        reply = QMessageBox.question(self, "Подтверждение","Удалить параметр {0}?".format(self.ui.comboBox_4.currentText()))
        if reply == QMessageBox.Yes:
            self.db.eraseParam(self.ui.comboBox_4.currentText())
            self.updParams()

    def add_Period(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.ui.comboBox_2.currentText() == "":
            QMessageBox.about(self, self.name, "Задайте тип события!")
            return
        self.db.insertPeriod(self.ui.dateTimeEdit.text(),self.ui.dateTimeEdit_2.text(),self.ui.comboBox_2.currentText())
        self.updPeriods()

    def del_Period(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.ui.comboBox_5.count() == 0:
            QMessageBox.about(self, self.name, "Список событий пуст!")
            return
        reply = QMessageBox.question(self, "Подтверждение","Удалить событие {0}?".format(self.ui.comboBox_5.currentText()))
        if reply == QMessageBox.Yes:
            self.db.erasePeriod(self.ui.comboBox_5.currentText())
            self.updPeriods()

    def learn_NN(self):
        if self.NN.model == None:
            QMessageBox.about(self, self.name, "Нейронная сеть не подключена!")
            return
        # self.load_dialog.show()
        # self.load_dialog.gif.start()
        time1 = self.ui.dateTimeEdit_3.text()
        time2 = self.ui.dateTimeEdit_4.text()
        train = self.db.learnTable(time1, time2)
        if len(train[0]) == 0:
            QMessageBox.about(self, self.name, "Набор данных пуст!\nОбучение невозможно.")
            return
        self.NN.learning(train[0], train[1],self.config["NN_learning_params"])
        # self.load_dialog.hide()

    def save_NN(self):
        if self.NN.model == None:
            QMessageBox.about(self, self.name, "Нейронная сеть не подключена!")
            return
        if self.NN.save_model(self.db.sdb) == True:
            QMessageBox.about(self, "Нейронная сеть", "'{0}' сохранена.".format(self.NN.name))
            self.db.updTableNN()
        else:
            QMessageBox.about(self, "Нейронная сеть", "'{0}' не сохранена.".format(self.NN.name))


    def create_NN(self):
        if self.db.sdb == None:
            QMessageBox.about(self, "База данных", "База данных не подключена.")
            return
        if self.ui.lineEdit_4.text() == "":
            QMessageBox.about(self, "База данных", "Задайте название нейронной сети.")
            return
        path = QFileDialog.getOpenFileName(self, "Выберите файл c размерами слоев нейронной сети", self.path, 'Text files (*.txt)')[0]
        if path == "":
            return
        with open(path,'r') as ff:
            layers = ff.read().splitlines()
        self.NN = NN_model(self.listParams,self.ui.lineEdit_4.text(),layers)
        if self.NN.create() == True:
            QMessageBox.about(self, "Нейронная сеть", "'{0}' создана".format(self.ui.lineEdit_4.text()))
            self.statBar.append('neural',self.ui.lineEdit_4.text())
        self.ui.textEdit.setText(self.NN.report())
        self.db.updParamsNN(self.NN.id)

    def load_NN(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        name,date = self.ui.comboBox.currentText().split(' - ')
        if self.NN.load_model(name,date,self.db.sdb) == False:
            QMessageBox.about(self, self.name, "Не удалось подключить нейронную сеть.")
            return
        QMessageBox.about(self, 'Нейронная сеть', "'{0}' загружена".format(name))
        self.statBar.append('neural',self.ui.comboBox.currentText())
        text = ''
        self.ui.textEdit.setText(self.NN.report())
        self.db.updParamsNN(self.NN.id)
        #import os
        #os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    def add_AgentsWorker(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        path = \
            QFileDialog.getOpenFileName(self, "Выберите файл c агентами мониторинга состояния", self.path, 'Text files (*.txt)')[0]
        if path == "":
            return
        with open(path, 'r') as ff:
            list = ff.read().splitlines()
        flagCon = 0
        for ag in list:
            try:
                if ag == '':
                    continue
                name, address = ag.split(":")
            except ValueError:
                continue
            self.agentsNames.append(name)
            self.agentsAddress.append(address)
        if flagCon == 1:
            QMessageBox.about(self, self.name, "Неверная структура данных агента.\nПопробуйте подключить вручную.")
        self.displayAgentsWorker()

    def add_AgentWorker(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        name = self.ui.lineEdit_6.text()
        address = self.ui.lineEdit_5.text()
        passw = self.ui.lineEdit_11.text()
        if name == '' or address == '':
            QMessageBox.about(self, self.name, "Введите адрес агента!")
            return
        if passw == "":
            passw = 'public'
        self.agentsNames.append(name)
        self.agentsAddress.append(address + " " + passw)
        self.displayAgentsWorker()
        self.ui.lineEdit_5.setText('')
        self.ui.lineEdit_6.setText('')
        self.ui.lineEdit_11.setText('')

    def del_AgentWorker(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        del self.agentsAddress[self.ui.comboBox_7.currentIndex()]
        del self.agentsNames[self.ui.comboBox_7.currentIndex()]
        self.displayAgentsWorker()

    def displayAgentsWorker(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        self.ui.textEdit_2.clear()
        self.ui.comboBox_7.clear()
        for i in range(len(self.agentsNames)):
            self.ui.textEdit_2.append("{0}: {1}".format(self.agentsNames[i],self.agentsAddress[i]))
        self.ui.comboBox_7.addItems(self.agentsNames)

    def start_Worker(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.worker != None:
            return
        if self.NN.model == None:
            QMessageBox.about(self, self.name, "Подключите нейронную сеть!")
            return
        if len(self.agentsAddress) == 0:
            QMessageBox.about(self, self.name, "Агенты не заданы!")
            return
        self.worker = Worker(self.NN, self.agentsAddress, self.listParams,
                             self.listActs, self.PD, self.ui.textEdit_3)
        self.worker.start()
        self.statBar.append('worker', 'on')

    def stop_Worker(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        if self.worker == None:
            return
        self.worker.running = False
        self.statBar.append('worker', 'off')
        self.worker = None

    def del_NN(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        reply = QMessageBox.question(self, "Подтверждение",
                                     "Удалить нейронную сеть '{0}'?".format(self.ui.comboBox_8.currentText()))
        if reply == QMessageBox.Yes:
            self.db.del_NN(self.ui.comboBox_8.currentText())
            self.db.updTableNN()

    def exit_Prog(self):
        if self.collector != None:
            self.collector.running = False
        if self.worker != None:
            self.worker.running = False
        sleep(5)
        exit()

    def filter_Data(self):
        if self.db.sdb == None:
            QMessageBox.about(self, self.name, "База данных не подключена")
            return
        params = ""
        zapr = ""
        if self.ui.checkBox_4.isChecked():
            zapr += " and ip = '{0}'".format(self.ui.lineEdit_9.text())
        if self.ui.checkBox_5.isChecked():
            for i in range(len(self.listParams)):
                if self.ui.lineEdit_10.text() == self.listParams[i]:
                    params = "param{0} as '{1}' ".format(i+1, self.listParams[i])
                    break
        if self.ui.checkBox_6.isChecked():
            zapr += " and time between '{0}' and '{1}' ".format(self.ui.dateTimeEdit_5.text(), self.ui.dateTimeEdit_6.text())
        if params == "":
            for i in range(len(self.listParams)):
                params += " param{0} as '{1}',".format(i+1, self.listParams[i])
            params = params[:len(params)-1]
        zapr = "select ip, time, {0} from data where 1=1 ".format(params) + zapr
        res = self.db.display_Data(zapr)
        if res!= "":
            QMessageBox.about(self, self.name, "Данные в таблице отстутствуют!")


app = QtWidgets.QApplication([])
application = mywindow()
application.show()
 
sys.exit(app.exec())
