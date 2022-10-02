from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense,Dropout

def create_model(listParam,layers):
    model = None
    vhod = len(listParam)
    # layers = []
    # with open("netw_param.txt") as pp:
    #     layers = pp.read().splitlines()
    if len(layers) != 0:
        model = Sequential()
        model.add(Dense(layers[0], input_dim=vhod, activation="relu"))
        for i in range(1, len(layers) - 1):
            model.add(Dense(layers[i], activation="relu"))
            # if float(layers[i]) < 1 :
            #     model.add(Dropout(layers[i]))
            # else:
            #     model.add(Dense(layers[i], activation="relu"))
        model.add(Dense(layers[len(layers)-1], activation="softmax"))
    else:
        return None
    model.compile(loss="categorical_crossentropy", optimizer="SGD", metrics=["accuracy"])
    return model



