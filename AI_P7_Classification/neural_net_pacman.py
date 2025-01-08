"""
neural_net_pacman.py
--------------------
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

import numpy as np
from keras import Sequential
from keras.layers import Dense
from sklearn.preprocessing import StandardScaler, OneHotEncoder

from neural_net import NeuralNetClassifier

PRINT = False


class NeuralNetClassifierPacman(NeuralNetClassifier):
    def __init__(self, legal_labels, max_iterations):
        NeuralNetClassifier.__init__(self, legal_labels, max_iterations)
        self.scaler = StandardScaler()

        # Your code here
        self.max_iterations = 100

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
            units=256,
            activation='relu'
        ))
        model.add(Dense(
            units=128,
            activation='relu'
        ))
        model.add(Dense(
            units=64,
            activation='relu'
        ))

        # Output
        model.add(Dense(
            units=outputs,
            activation='softmax'
        ))

        '''
        List of optimizers:     https://keras.io/api/optimizers/#available-optimizers
        List of loss functions: https://keras.io/api/losses/#available-losses
        '''
        model.compile(
            optimizer='adam',      #'sgd',
            loss='categorical_crossentropy',              #'mse',
            metrics=['Accuracy']
        )

        return model

    # Do NOT edit code below this point. You will mess up the autograder.

    def train(self, training_data, training_labels, validation_data, validation_labels):

        x_train = self._encode_data(training_data)
        x_train = self.scaler.fit_transform(x_train)

        y_train = np.array(training_labels).reshape(-1, 1)
        y_train = self.encoder.fit_transform(y_train).toarray()

        x_validate = self._encode_data(validation_data)
        x_validate = self.scaler.transform(x_validate)

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
        x_test = self._encode_data(data)
        x_test = self.scaler.transform(x_test)

        predictions = self.model.predict(x_test)
        predictions = self.encoder.inverse_transform(predictions)

        return predictions

    def _encode_data(self, data):
        encoded = []

        temp = list(data[0][0].keys())
        num_elements = len(data[0][0][temp[0]].values())

        for counter, valid in data:
            x = []

            keys = [key.upper() for key in list(counter.keys())]
            for label in self.legal_labels:
                if label in keys:
                    # add elements from counter
                    x.extend(list(counter[label.capitalize()].values()))
                else:
                    # add all zeros
                    x.extend(np.zeros(num_elements))

            valid = self._encode_moves(valid)

            x.extend(valid)

            encoded.append(np.array(x))

        return np.array(encoded)

    def _encode_moves(self, moves):
        legal = np.array(['North', 'South', 'East', 'West', 'Stop']).reshape(-1, 1)
        temp_encoder = OneHotEncoder()
        temp_encoder.fit(legal)

        combined = np.zeros(len(self.legal_labels))

        encoded = np.array(moves).reshape(-1, 1)
        encoded = temp_encoder.transform(encoded).toarray()

        for arr in encoded:
            combined = np.add(combined, arr)

        return np.array(combined)
