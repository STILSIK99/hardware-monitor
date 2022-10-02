

def learning(model,x_train,y_train,params):
    history = model.fit(x_train, y_train,
                        batch_size=min(params['batch_size'],len(x_train)//5),
                        epochs=params['epochs'],
                        verbose=params['verbose'])
    return model