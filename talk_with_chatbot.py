# -*- coding: utf-8 -*-
import os
import re
import yaml

import numpy as np
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense
from tensorflow.keras.models import Model
from tensorflow.keras import preprocessing, utils


def tokenize(sentences):
    tokens_list = []
    vocabulary = []
    for sentence in sentences:
        sentence = sentence.lower()
        sentence = re.sub( '[^a-zA-Z]', ' ', sentence )
        tokens = sentence.split()
        vocabulary += tokens
        tokens_list.append( tokens )
    return tokens_list , vocabulary

""" Defining inference models """
def make_inference_models():
    encoder_model = Model(encoder_inputs, encoder_states)
    decoder_state_input_h = Input(shape=(200 ,))
    decoder_state_input_c = Input(shape=(200 ,))
    decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
    
    decoder_outputs, state_h, state_c = decoder_lstm(decoder_embedding, initial_state=decoder_states_inputs)
    decoder_states = [state_h, state_c]
    decoder_outputs = decoder_dense(decoder_outputs)
    decoder_model = Model(
        [decoder_inputs] + decoder_states_inputs,
        [decoder_outputs] + decoder_states)

    return encoder_model, decoder_model

""" Talking with Chatbot """
def str_to_tokens(sentence : str):
    sentence = sentence.lower()
    sentence = re.sub('[^a-zA-Z]', ' ', sentence)
    words = sentence.split()
    tokens_list = list()
    signal = 0
    for word in words:
        if word not in tokenizer.word_index:
            print("Unintelligible sentence")
            """ send the signal to indicate the unclear sentence """
            signal = -1
        else:
            tokens_list.append(tokenizer.word_index[word]) 
    return preprocessing.sequence.pad_sequences([tokens_list], maxlen=maxlen_questions, padding='post'), signal


""" Load QA data """
dir_path = 'data'
files_list = os.listdir(dir_path + os.sep)

questions = list()
answers = list()
for filepath in files_list:
    stream = open(dir_path + os.sep + filepath , 'rb')
    docs = yaml.safe_load(stream)
    conversations = docs['conversations']
    for con in conversations:
        if len(con) > 2 :
            questions.append(con[0])
            replies = con[1: ]
            ans = ''
            for rep in replies:
                ans += ' ' + rep
            answers.append( ans )
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
for i in range(len(answers_with_tags)) :
    answers.append('<START> ' + answers_with_tags[i] + ' <END>')

tokenizer = preprocessing.text.Tokenizer()
tokenizer.fit_on_texts(questions + answers)
VOCAB_SIZE = len(tokenizer.word_index) + 1
print('VOCAB SIZE : {}'.format(VOCAB_SIZE))


""" Preparing data for Seq2Seq model """
vocab = []
for word in tokenizer.word_index:
    vocab.append(word)


""" encoder_input_data """
tokenized_questions = tokenizer.texts_to_sequences(questions)
maxlen_questions = max([len(x) for x in tokenized_questions])
padded_questions = preprocessing.sequence.pad_sequences(tokenized_questions, maxlen=maxlen_questions ,padding='post')
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
padded_answers = preprocessing.sequence.pad_sequences(tokenized_answers, maxlen=maxlen_answers, padding='post' )
onehot_answers = utils.to_categorical(padded_answers, VOCAB_SIZE)
decoder_output_data = np.array(onehot_answers)
print(decoder_output_data.shape)


""" Defining the Encoder-Decoder model """
encoder_inputs = Input(shape=(maxlen_questions, ))
encoder_embedding = Embedding(VOCAB_SIZE, 200, mask_zero=True) (encoder_inputs)
encoder_outputs, state_h, state_c = LSTM(200, return_state=True)(encoder_embedding)
encoder_states = [state_h, state_c]

decoder_inputs = Input(shape=(maxlen_answers, ))
decoder_embedding = Embedding(VOCAB_SIZE, 200, mask_zero=True) (decoder_inputs)
decoder_lstm = LSTM(200, return_state=True, return_sequences=True)
decoder_outputs , _ , _ = decoder_lstm(decoder_embedding, initial_state=encoder_states)
decoder_dense = Dense(VOCAB_SIZE, activation='softmax') 
output = decoder_dense (decoder_outputs)

model = Model([encoder_inputs, decoder_inputs], output)

model.load_weights('model.h5')


encode_model, decode_model = make_inference_models()

print("Hello :-)")
while True:
    msg = input("> ")
    if msg == "bye":
        print("Have a nice day! See you next time ~")
        break
    #states_values = encode_model.predict(str_to_tokens(text))
    text, signal = str_to_tokens(msg)
    states_values = encode_model.predict(text)
    if signal == -1:
        print("Sorry...I cannot understand what you said.")
        continue
    empty_target_seq = np.zeros((1, 1))
    empty_target_seq[0, 0] = tokenizer.word_index['start']
    stop_condition = False
    decoded_translation = ''
    while not stop_condition :
        dec_outputs, h, c = decode_model.predict([empty_target_seq] + states_values)
        sampled_word_index = np.argmax(dec_outputs[0, -1, :])
        sampled_word = None
        for word, index in tokenizer.word_index.items() :
            if sampled_word_index == index :
                decoded_translation += ' {}'.format(word)
                sampled_word = word
        
        if sampled_word == 'end' or len(decoded_translation.split()) > maxlen_answers:
            stop_condition = True
            
        empty_target_seq = np.zeros((1, 1))  
        empty_target_seq[0, 0] = sampled_word_index
        states_values = [h, c] 

    print(decoded_translation[:-4])
