import numpy as np

def make_decision(model,x_mas):
    try:
        prediction = model.predict(np.array([x_mas]))
        return np.argmax(prediction[0])
    except ValueError:
        print("Мало параметров - {}".format(len(x_mas)))
    return None

