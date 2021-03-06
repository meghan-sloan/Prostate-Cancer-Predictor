'''
Code implements multi-perceptron neural network to classify aggressive and
non-aggressive prostate cancer using a binary Gleason score as the label load_and_condition_MNIST_data
genomic data as features
'''

# from __future__ import division
import pandas as pd
import numpy as np
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers.core import Dense
from keras.layers import Dropout, Activation
from keras.optimizers import SGD
from keras.optimizers import Adam
from keras.initializers import RandomNormal
import theano
from sklearn.model_selection import train_test_split
from sklearn.metrics import recall_score
from keras.utils.training_utils import multi_gpu_model
from keras.callbacks import EarlyStopping
from sklearn.preprocessing import StandardScaler

def define_nn_mlp_model(X_train, y_train_ohe):
    ''' defines multi-layer-perceptron neural network '''
    # available activation functions at:
    # https://keras.io/activations/
    # https://en.wikipedia.org/wiki/Activation_function
    # options: 'linear', 'sigmoid', 'tanh', 'relu', 'softplus', 'softsign'
    # there are other ways to initialize the weights besides 'uniform', too

    model = Sequential() # sequence of layers
    num_neurons_in_layer = 100 # number of neurons in a layer
    num_inputs = X_train.shape[1] # number of features (784)
    num_classes = 1  # number of classes 0 or 1
    model.add(Dense(units=1000,
                    input_dim=num_inputs,
                    kernel_initializer='RandomNormal',
                    activation='relu'))
    model.add(Dense(units=500,
                    kernel_initializer='RandomNormal',
                    activation='relu'))
    model.add(Dropout(0.3))
    model.add(Dense(units=100,
                    kernel_initializer='RandomNormal',
                    activation='relu'))
    model.add(Dense(units=num_classes,
                    kernel_initializer='RandomNormal',
                    activation='sigmoid', name='end'))
    sgd = SGD(lr=0.0001, decay=1e-7, momentum=.9)
    adam = Adam(lr=0.001, decay=1e-7)
    model.compile(loss='binary_crossentropy', optimizer=adam, metrics=["accuracy"] ) # (keep)
    print (model.summary())
    return model

def specificity(y_test, y_pred):
    TN = np.sum([(y_pred==0) & (y_test==0)])
    FP = np.sum([(y_pred==1) & (y_test)==0])
    return TN/(TN+FP)

def print_output(model, y_train, y_test, rng_seed):
    '''prints model accuracy results'''
    y_train_pred = model.predict_classes(X_train, verbose=0)
    y_test_pred = model.predict_classes(X_test, verbose=0)
    print('\nRandom number generator seed: {}'.format(rng_seed))
    print('\nFirst 30 labels:      {}'.format(y_train[:30]))
    print('First 30 predictions: {}'.format(y_train_pred[:30]))
    train_acc = np.sum(y_train == y_train_pred, axis=0) / X_train.shape[0]
    print('\nTraining accuracy: %.2f%%' % (train_acc * 100))
    test_acc = np.sum(y_test == y_test_pred, axis=0) / X_test.shape[0]
    print('Test accuracy: %.2f%%' % (test_acc * 100))
    recall = recall_score(y_test, y_test_pred)
    print('Test recall: {}'.format(recall))
    specif = specificity(y_test_pred, y_test)
    print('Test specificity: {}'.format(specif))


if __name__ == '__main__':
    rng_seed = 2 # set random number generator seed
    np.random.seed(rng_seed)
    X = pd.read_csv('X_train_select.csv', index_col=0)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X.values)
    X_test = pd.read_csv('X_test_select.csv', index_col=0)
    X_test = scaler.transform(X_test.values)
    y = pd.read_csv('y_train.csv', index_col=0)
    y_train = y['Gleason_binary'].values.reshape(-1,1)
    yt = pd.read_csv('y_test.csv', index_col=0)
    y_test = yt['Gleason_binary'].values.reshape(-1,1)

    earlystopping = EarlyStopping(monitor='val_loss', patience=5)
    model = define_nn_mlp_model(X_train, y_train)
    model.fit(X_train, y_train, epochs=100, batch_size=50, verbose=1, callbacks=[earlystopping], validation_data=(X_test, y_test)) # cross val to estimate test error
    print_output(model, y_train, y_test, rng_seed)
