import create
import learning
import working_mode
import numpy as np
from tensorflow.keras import utils
import save_open_neural as son

x_tr = []
y_tr = []
for i in range(1,50):
    x_tr.append(np.array([i]))
    y_tr.append(np.uint8(i//10))

# print(x_tr,y_tr)
x_tr = np.array(x_tr)
# тестовые данные
x_test = np.array([ np.array([i]) for i in range(0,50,2) ])
y_test = np.array([ np.uint8(i//10) for i in range(0,50,2) ])

# print(x_test,y_test)
y_tr = np.array(utils.to_categorical(y_tr,5))
y_test = np.array(utils.to_categorical(y_test,5))

#Данные хранятся:
#   набор данных - numpy.array, где каждый элемент это numpy.array из заданного количества входных параметров сети
#   проверочные данные - numpy.array, где каждый из numpy.array состощий из нулей и единицы

#создание нейронной сети
model = create.create_model(['num'])
#обучение сети
model = learning.learning(model,x_tr,y_tr)
#рабочее состояние
#получение ответа на 1 набор данных
decision = working_mode.make_decision(model,x_test[0])
#сохранение нейронки
#son.save_NN(model)
#Загрузка модели из памяти
model = son.open_NN()
