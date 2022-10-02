from NN_create import create_model
from NN_learning import learning
from NN_working_mode import make_decision

from PyQt5.QtSql import QSqlQuery
from tensorflow.keras.models import model_from_json

class NN_model:

    def __init__(self, listPar, name, layers):
        self.model = None
        self.params = listPar
        self.id = None
        self.name = name
        self.layers = layers
        # with open('NN_decisions.txt') as d:
        #     self.decisons = d.read().splitlines()

    def create(self):
        self.model = create_model(self.params,self.layers)
        # self.report()
        self.model.compile(loss="categorical_crossentropy", optimizer="SGD", metrics=["accuracy"])
        return True

    def learning(self,x_train,y_train,params):
        if self.model == None:
            return False
        self.model = learning(self.model,x_train,y_train,params)
        return True

    def decision(self,mas_x):
        if self.model == None:
            return None
        return make_decision(self.model,mas_x)

    def save_model(self,db):
        NN_json = self.model.to_json()
        if db == None:
            return False
        #проверка на наличие
        if self.id != None:
            sql = QSqlQuery(db)
            print("update NN set data = '{0}' where id_n = {1}".format(NN_json,self.id))
            sql.exec("update NN set data = '{0}' where id_n = {1}".format(NN_json,self.id))
            if sql.lastError().text() != "":
                print(sql.lastError().text())
                return False
        else:
            #вставка новых данных
            sql = QSqlQuery(db)
            print("insert into NN (id_n,name_n,data) values (null,'{0}','{1}')".format(self.name,NN_json))
            sql.exec("insert into NN (id_n,name_n,data) values (null,'{0}','{1}')".format(self.name,NN_json))
            if sql.lastError().text() != "":
                print(sql.lastError().text())
                return False
            #получить id текущей НСети
            sql = QSqlQuery(db)
            print("select id_n from NN where date = (select max(date) from NN)")
            sql.exec("select id_n from NN where date = (select max(date) from NN)")
            if sql.next():
                self.id = sql.value(0)
            else:
                return False
            for i in self.params:
                sql = QSqlQuery(db)
                sql.exec("insert into params_nn values ({0},'{1}');".format(self.id, i))
                if sql.lastError().text() != "":
                    print(sql.lastError().text())
                    return False


        return True

    def load_model(self,name,date,db):
        sql = QSqlQuery(db)
        sql.exec("select id_n from NN where name_n = '{0}' and date = '{1}';".format(name,date))
        print(sql.lastError().text())
        if sql.next():
            self.id = sql.value(0)
        else:
            return False
        self.params = []
        sql = QSqlQuery(db)
        sql.exec("select name from params_nn where id_n = {0}".format(self.id))
        print(sql.lastError().text())
        while sql.next():
            self.params.append(sql.value(0))
        sql = QSqlQuery(db)
        sql.exec("select name_n,data from NN where id_n = {0}".format(self.id))
        print(sql.lastError().text())
        if sql.next():
            self.name = sql.value(0)
            NN_json = sql.value(1)
        else:
            return False
        self.model = model_from_json(NN_json)
        self.model.compile(loss="categorical_crossentropy", optimizer="SGD", metrics=["accuracy"])
        return True

    def report(self):
        import io
        stream = io.StringIO()
        self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
        summary_string = stream.getvalue()
        stream.close()
        return summary_string



    #Жалко удалять вариант с созданием папки кэширования
    # if isdir('cache') == False:
    #     mkdir('cache')
    # text_date = "cache/" + datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    # self.model.save(text_date + '.h5')
    # with open(text_date + ".h5", 'rb') as ff:
    #     file = ff.read()
    # ff = base64.b64encode(file)
    # NN_base = ff.decode('utf-8')


    # ff = base64.b64decode(NN_base64)
    # if isdir('cache') == False:
    #     mkdir('cache')
    #
    # text_date = "cache/" + datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    # with open(text_date + ".h5", 'wb') as netw:
    #     netw.write(ff)
