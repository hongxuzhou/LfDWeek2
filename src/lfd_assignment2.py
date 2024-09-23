#!/usr/bin/env python

import random as python_random
import json
import argparse
import numpy
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout # Add dropout
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import LabelBinarizer
from tensorflow.keras.optimizers import SGD, Adam, RMSprop # Add two optimisers
from keras.callbacks import EarlyStopping # Add early stopping
import tensorflow as tf
# Make reproducible as much as possible
numpy.random.seed(1234)
tf.random.set_seed(1234)
python_random.seed(1234)


def create_arg_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--train_file", default='train_NE.txt', type=str,
                        help="Input file to learn from (default train_NE.txt)")
    parser.add_argument("-d", "--dev_file", default='dev_NE.txt', type=str,
                        help="Development set (default dev_NE.txt)")
    parser.add_argument("-e", "--embeddings", default='/Users/hongxuzhou/LfD/week2/LfDWeek2/data/glove_filtered.json', type=str,
                        help="Embedding file we are using (default glove_filtered.json)")
    parser.add_argument("-ts", "--test_file", type=str,
                        help="Separate test set to read from, for which we do not have labels")
    parser.add_argument("-o", "--output_file", type=str,
                        help="Output file to which we write predictions for test set")
    
    # New arguments for hyperparameters
    parser.add_argument("-hl", "--hidden_layers", nargs="+", type=int, default=[64],
                        help="Number of units in hidden layers, support multiple hidden layers")
    parser.add_argument('-dr', '--dropout', type=float, default=0.0,
                        help='Dropout rate')
    parser.add_argument('-lr', '--learning_rate', type=float, default=0.0005,
                        help='Learning rate')
    parser.add_argument('-bz', '--batch_size', type=int, default=32,
                        help='Batch size')
    parser.add_argument('-ep', '--epochs', type=int, default=10,
                        help='Number of epochs')
    parser.add_argument('-opt', '--optimizer', type=str, default='adam',
                        choices=['adam', 'sgd', 'rmsprop'],
                        help='Optimizer to use')
    args = parser.parse_args()
    if args.test_file and not args.output_file:
        raise ValueError("Always specify an output file if you specify a separate test set")
    if args.output_file and not args.test_file:
        raise ValueError("Output file is specified but test set is not -- probably you made a mistake")
    return args


def write_to_file(lst, out_file):
    '''Write list to file'''
    with open(out_file, "w", encoding="utf-8") as out_f:
        for line in lst:
            out_f.write(line.strip() + '\n')
    out_f.close()


def read_corpus(corpus_file):
    '''Read in the named entity data from a file'''
    names = []
    labels = []
    for line in open(corpus_file, 'r', encoding="utf-8"):
        name, label = line.strip().split()
        names.append(name)
        labels.append(label)
    return names, labels


def read_embeddings(embeddings_file):
    '''Read in word embeddings from file and save as numpy array'''
    embeddings = json.load(open(embeddings_file, 'r'))
    return {word: numpy.array(embeddings[word]) for word in embeddings}


def vectorizer(words, embeddings):
    '''Turn words into embeddings, i.e. replace words by their corresponding embedding'''
    return numpy.array([embeddings[word] for word in words])


def create_model(X_train, Y_train, args):
    '''
    Create and compile the model based on cmd line arguments.
    '''
    # Define settings, you might want to create cmd line args for them
    # (or some other more reproducible method)
    #learning_rate = 0.0005
    # Use softmax here for now, but you can experiment!
    #activation = "softmax"
    # Start with MSE, but again, experiment!
    #loss_function = 'mse'
    # SGD optimizer - yes, you should experiment here as well
    #sgd = SGD(learning_rate=learning_rate)

    # Now build the model
    model = Sequential()
    # Input layer
    model.add(Dense(args.hidden_layers[0], input_dim=X_train.shape[1], activation = 'relu'))
    model.add(Dropout(args.dropout)) # Add dropout for regularisation
    
    # Potentially add your own layers here. Note that you have to change the dimensions of the prev layer
    # so that your final output layer has the correct number of nodes
    # You could also think about using Dropout!
    
    # Hidden layers
    for units in args.hidden_layers[1:]:
        model.add(Dense(units, activation='relu'))
        model.add(Dropout(args.dropout))
    
    # Output layer
    model.add(Dense(Y_train.shape[1], activation = 'softmax'))
    
    # Choose optimiser
    if args.optimizer == 'adam':
        optimizer = Adam(learning_rate = args.learning_rate)
    elif args.optimizer == 'sgd':
        optimizer = SGD(learning_rate = args.learning_rate)
    elif args.optimizer == 'rmsprop':
        optimizer = RMSprop(learning_rate = args.learning_rate)
        
    # Compile model using our settings, check for accuracy
    model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=['accuracy'])
    # reference: https://www.tensorflow.org/api_docs/python/tf/keras/losses/categorical_crossentropy
    return model


def train_model(model, X_train, Y_train, X_dev, Y_dev, args):
    '''This funcition is modified to use cmd line arguments above and to implement early stopping'''
    early_stopping = EarlyStopping(monitor='val_loss', patience = 2, restore_best_weights = True) # Add early stopping

    # Finally fit the model to our data
    model.fit(X_train, Y_train, verbose=1, 
            epochs=args.epochs, 
            batch_size=args.batch_size, 
            validation_data=(X_dev, Y_dev), 
            callbacks = [early_stopping])
    return model


def dev_set_predict(model, X_dev, Y_dev):
    '''Do predictions and measure accuracy on labeled dev or test set'''
    # Get predictions using the trained model
    Y_pred = model.predict(X_dev)
    # Finally, convert to numerical labels to get scores with sklearn
    Y_pred = numpy.argmax(Y_pred, axis=1)
    # Calculate accuracy
    Y_dev = numpy.argmax(Y_dev, axis=1)
    acc = round(accuracy_score(Y_dev, Y_pred), 3)
    print(f"Accuracy on dev set: {acc}")


def separate_test_set_predict(test_set, embeddings, encoder, model, output_file):
    '''Do prediction on a separate test set for which we do not have a gold standard.
    Write predictions to a file'''
    # Read and vectorize data
    #test_emb = vectorizer([x.strip() for x in open(test_set, 'r')], embeddings) original
    test_emb = vectorizer([x.strip() for x in open(test_set, 'r', encoding="utf-8")], embeddings)
    # Make predictions
    pred = model.predict(test_emb)
    # Convert to numerical labels and back to string labels
    test_pred = numpy.argmax(pred, axis=1)
    labels = [encoder.classes_[idx] for idx in test_pred]
    # Finally write predictions to file
    # Create output in the format as the input
    output = [f'{word}\t{label}' for word, label in zip([x.strip() for x in open(test_set, 'r', encoding="utf-8")], labels)]
    
    write_to_file(labels, output_file)


def main():
    '''To put together all the functions above'''
    args = create_arg_parser()

    # Read in the data and embeddings
    X_train, Y_train = read_corpus(args.train_file)
    X_dev, Y_dev = read_corpus(args.dev_file)
    embeddings = read_embeddings(args.embeddings)

    # Transform words to embeddings
    X_train_emb = vectorizer(X_train, embeddings)
    X_dev_emb = vectorizer(X_dev, embeddings)

    # Transform string labels to one-hot encodings
    encoder = LabelBinarizer()
    Y_bin_train = encoder.fit_transform(Y_train)  # Use encoder.classes to find mapping back
    Y_bin_dev = encoder.fit_transform(Y_dev)

    # Create model ADUJUSTED!! to use cmd line arguments
    model = create_model(X_train_emb, Y_bin_train, args)

    # Train the model
    model = train_model(model, X_train_emb, Y_bin_train, X_dev_emb, Y_bin_dev, args)

    # Calculate accuracy on the dev set
    dev_set_predict(model, X_dev_emb, Y_bin_dev)

    # If we specified a test set, there are no gold labels available
    # Do predictions and print them to a separate file
    if args.test_file:
        separate_test_set_predict(args.test_file, embeddings, encoder, model, args.output_file)


if __name__ == '__main__':
    main()
