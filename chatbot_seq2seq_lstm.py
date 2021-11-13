# -*- coding: utf-8 -*-
import os
import re
import yaml

import numpy as np
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense
from tensorflow.keras.models import Model
from tensorflow.keras import preprocessing, utils
from tensorflow.keras.utils import plot_model


def tokenize(sentences):
    tokens_list = []
    vocabulary = []
    for sentence in sentences:
        sentence = sentence.lower()
        sentence = re.sub('[^a-zA-Z]', ' ', sentence)
        tokens = sentence.split()
        vocabulary += tokens
        tokens_list.append(tokens)
    return tokens_list, vocabulary


""" Load QA data """
dir_path = 'data'
files_list = os.listdir(dir_path + os.sep)

questions = list()
answers = list()
for filepath in files_list:
    stream = open(dir_path + os.sep + filepath, 'rb')
    docs = yaml.safe_load(stream)
    conversations = docs['conversations']
    for con in conversations:
        if len(con) > 2 :
            questions.append(con[0])
            replies = con[1: ]
            ans = ''
            for rep in replies:
                ans += ' ' + rep
            answers.append(ans)
        elif len(con) > 1:
            questions.append(con[0])
            answers.append(con[1])

answers_with_tags = list()
for i in range(len(answers)):
    if type(answers[i]) == str:
        answers_with_tags.append(answers[i])
    else:
        questions.pop(i)

answers = list()
for i in range(len(answers_with_tags)):
    answers.append('<START> ' + answers_with_tags[i] + ' <END>')

tokenizer = preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(questions + answers)
VOCAB_SIZE = len(tokenizer.word_index) + 1
#print( 'VOCAB SIZE : {}'.format( VOCAB_SIZE ))


""" Preparing data for Seq2Seq model """
vocab = []
for word in tokenizer.word_index:
    vocab.append(word)


""" encoder_input_data """
tokenized_questions = tokenizer.texts_to_sequences(questions)
maxlen_questions = max([ len(x) for x in tokenized_questions])
padded_questions = preprocessing.sequence.pad_sequences(tokenized_questions, maxlen=maxlen_questions, padding='post')
encoder_input_data = np.array(padded_questions)
print(encoder_input_data.shape, maxlen_questions)

""" decoder_input_data """
tokenized_answers = tokenizer.texts_to_sequences(answers)
maxlen_answers = max([len(x) for x in tokenized_answers])
padded_answers = preprocessing.sequence.pad_sequences(tokenized_answers, maxlen=maxlen_answers, padding='post' )
decoder_input_data = np.array(padded_answers)
print(decoder_input_data.shape, maxlen_answers)

""" decoder_output_data """
tokenized_answers = tokenizer.texts_to_sequences(answers)
for i in range(len(tokenized_answers)) :
    tokenized_answers[i] = tokenized_answers[i][1:]
padded_answers = preprocessing.sequence.pad_sequences(tokenized_answers, maxlen=maxlen_answers, padding='post')
onehot_answers = utils.to_categorical(padded_answers, VOCAB_SIZE)
decoder_output_data = np.array(onehot_answers)
print(decoder_output_data.shape)

""" Defining the Encoder-Decoder model """
encoder_inputs = Input(shape=(maxlen_questions, ))
encoder_embedding = Embedding(VOCAB_SIZE,200 ,mask_zero=True)(encoder_inputs)
encoder_outputs, state_h, state_c = LSTM(200 ,return_state=True)(encoder_embedding)
encoder_states = [state_h, state_c]

decoder_inputs = Input(shape=(maxlen_answers, ))
decoder_embedding = Embedding(VOCAB_SIZE, 200, mask_zero=True)(decoder_inputs)
decoder_lstm = LSTM(200, return_state=True, return_sequences=True)
decoder_outputs , _, _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = Dense(VOCAB_SIZE, activation='softmax') 
output = decoder_dense(decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], output)
model.compile(optimizer='adam', loss='categorical_crossentropy')

model.summary()
plot_model(model, to_file='model.png', show_shapes=True)


""" Train and save the model """
model.fit([encoder_input_data, decoder_input_data], decoder_output_data, batch_size=50, epochs=500) 
model.save('model.h5')
