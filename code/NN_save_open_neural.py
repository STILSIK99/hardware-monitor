from PyQt5.QtSql import QSqlDatabase,QSqlTableModel,QSqlQuery,QSqlQueryModel
from tensorflow.keras.models import load_model
# from tensorflow.keras.models import Sequential
import base64

def save_NN(model):
    model.save_model('neural.h5')
    with open("neural.h5",'rb') as netw:
        file = netw.read()
    ff = base64.b64encode(file)
    ff = ff.decode('utf-8')
    return ff
    # with open("base.txt",'w') as bb:
    #     bb.write(ff)

def open_NN(NN_base64):
    # with open("base.txt",'r') as bb:
    #     file = bb.read()
    ff = base64.b64decode(NN_base64)
    with open("neural.h5",'wb') as netw:
        netw.write(ff)
    return load_model("neural.h5")

