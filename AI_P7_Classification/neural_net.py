"""
neural_net.py
-------------
Licensing Information:  You are free to use or extend these projects for
educational purposes provided that (1) you do not distribute or publish
solutions, (2) you retain this notice, and (3) you provide clear
attribution to UC Berkeley, including a link to http://ai.berkeley.edu.

Attribution Information: The Pacman AI projects were developed at UC Berkeley.
The core projects and autograders were primarily created by John DeNero
(denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
Student side autograding was added by Brad Miller, Nick Hay, and
Pieter Abbeel (pabbeel@cs.berkeley.edu).
"""

# Neural implementation
import numpy as np
import pandas as pd
from keras import Sequential
from keras.layers import Dense
from sklearn.preprocessing import OneHotEncoder

PRINT = False


class NeuralNetClassifier:
    """
    Neural Net classifier.
    """

    def __init__(self, legal_labels, _):
        self.model = self.make_model(len(legal_labels))
        self.legal_labels = legal_labels
        self.encoder = OneHotEncoder()

        # Your code here
        self.max_iterations = 50

    @staticmethod
    def make_model(outputs):
        """
        Creates a keras Neural Network
        :param outputs: number of outputs for the model
        :return: a keras model
        """

        model = Sequential()

        '''
        List of activation functions: https://keras.io/api/layers/activations/#available-activations
        '''

        # Add hidden layers here
        model.add(Dense(
            units= 256,
            activation='relu'
        ))

        model.add(Dense(
            units= 128,
            activation='relu'
        ))
        model.add(Dense(
            units= 64,
            activation='relu'
        ))


        # Output
        model.add(Dense(
            units= outputs,
            activation='softmax'
        ))


        '''
        List of optimizers:     https://keras.io/api/optimizers/#available-optimizers
        List of loss functions: https://keras.io/api/losses/#available-losses
        '''
        model.compile(
            optimizer='adam',   #'sgd',
            loss= 'categorical_crossentropy',    #'mse',
            metrics=['Accuracy']
        )

        return model

    # Do NOT edit code below this point. You will mess up the autograder.

    def train(self, training_data, training_labels, validation_data, validation_labels):
        x_train = np.array(pd.DataFrame.from_dict(training_data))

        y_train = np.array(training_labels).reshape(-1, 1)
        y_train = self.encoder.fit_transform(y_train).toarray()

        x_validate = np.array(pd.DataFrame.from_dict(validation_data))

        y_validate = np.array(validation_labels).reshape(-1, 1)
        y_validate = self.encoder.transform(y_validate).toarray()

        self.model.fit(
            x_train,
            y_train,
            epochs=self.max_iterations,
            validation_data=(x_validate, y_validate),
            verbose=PRINT
        )

    def classify(self, data):
        x_test = pd.DataFrame.from_dict(data)
        predict_x = self.model.predict(x_test)
        predictions=np.argmax(predict_x,axis=1)
        return predictions
