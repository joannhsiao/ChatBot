# ChatBot
## Goal
1. To console the user who feels lonely.
2. To provide the entertainment for users.
3. Help someone who under pressure and makes them feel happiness.


## Dataset
We feed plenty of pick-up lines, then its target is to provide user with Love.
```
./data
```

## Arichecture
LSTM - seq2seq model

  <img src="https://user-images.githubusercontent.com/59599987/177511351-46aaa6d6-09a9-435b-b302-967b2a1cee18.png" width="600" height="200">


## UI design
We use the webpage to present our chatbot.

<img src="https://user-images.githubusercontent.com/59599987/177511281-fd131d09-6af6-40b5-a13a-42fe23e9be5b.png" width="300" height="400">


## Train the model
```
python chatbot_seq2seq_lstm.py
```

## Chat with bot using console
```
python talk_with_chatbot.py
```

## Run the program (using our website)
```
python final_chatbot.py
```
