#################################################################################################################
#################################################################################################################
################################################Music Generation############################################
import numpy as np
import pandas as pd
import wget
from keras.models import Sequential,load_model
from keras.layers import LSTM,TimeDistributed,Dense,Embedding,Activation,Dropout


wget.download("http://abc.sourceforge.net/NMD/nmd/hpps.txt")

#creating dataframe to store loss and accuracy at each step
log=pd.DataFrame(columns=["Epoch","Loss","Accuracy"])
log.loc[0]=[0,0,0]
log.head()


text=""

with open("hpps.txt","r") as fh:
    for line in fh:
        text+=line

text[:50]
#dict to convert characters into integer and vice versa
char_2_idx={j:i for i,j in enumerate(sorted(list(set(text))))}
idx_2_char={i:j for i,j in enumerate(sorted(list(set(text)))) }
print("Number of unique characters ",len(char_2_idx))
print(char_2_idx)


#creating batches for model manually
def read_batches(T,vocab_size):
    length=T.shape[0]
    batch_chars=int(length/batch_size)
    seq_len=64
    for start in range(0,batch_chars-seq_len,seq_len):
        x=np.zeros((batch_size,seq_len)) #16*64
        y=np.zeros((batch_size,seq_len,vocab_size)) #16*64*74
        for i in range(0,batch_size):#0,16
            for j in range(0,seq_len):#0,64
                x[i,j]=T[batch_chars*i+start+j]
                y[i,j,T[batch_chars*i+start+j+1]]=1
        yield x,y

vocab_size=len(char_2_idx)
epochs=100

batch_size=16
seq_len=64

model=Sequential()
model.add(Embedding(vocab_size,512,batch_input_shape=(batch_size, seq_len)))
model.add(LSTM(512,return_sequences=True,stateful=True))
model.add(Dropout(0.2))
model.add(LSTM(512,return_sequences=True,stateful=True))
model.add(Dropout(0.2))
model.add(LSTM(512,return_sequences=True,stateful=True))
model.add(Dropout(0.2))
model.add(TimeDistributed(Dense(vocab_size)))
model.add(Activation("softmax"))
model.summary()

#training model
T=np.asarray([char_2_idx[i] for i in text],dtype=np.int32)
print("Length of text ",T.size)


model.compile(loss="categorical_crossentropy",optimizer="adam",metrics=["accuracy"])

# %cd /content/drive/My Drive/music generation models
# for i in range(1,epochs+1):
#     losses,accu=[],[]
#     for j,(x,y) in enumerate(read_batches(T,vocab_size)):
#         loss,acc=model.train_on_batch(x,y)
        
#         losses.append(loss)
#         accu.append(acc)
#     log.loc[i]=[i,loss,acc]
#     print("Epoch {} Loss {} Accuracy {}".format(i,loss,acc))
#     if i%20==0:
#         model.save_weights("model_512_weights_{}.h5".format(i))
#         print("Model saved at epoch ",i)

def make_model(unique_chars):
    model = Sequential()
    
    model.add(Embedding(input_dim = unique_chars, output_dim = 512, batch_input_shape = (1, 1))) 
  
    model.add(LSTM(512, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(512, return_sequences = True, stateful = True))
    model.add(Dropout(0.2))
    
    model.add(LSTM(512, stateful = True)) 
    #remember, that here we haven't given return_sequences = True because here we will give only one character to generate the
    #sequence. In the end, we just have to get one output which is equivalent to getting output at the last time-stamp. So, here
    #in last layer there is no need of giving return sequences = True.
    model.add(Dropout(0.2))
    
    model.add((Dense(unique_chars)))
    model.add(Activation("softmax"))
    
    return model

index_to_char = {i:ch for ch, i in char_2_idx.items()}
unique_chars = len(index_to_char)
## we are creating this model because we want to input a single character to model to start generating music.
#If we dont build this model again then we need to create a 16*64 size input to start model to generate music


#################################################################################################################


def output_generation(model_name):
    model=model_name[:3]
    model = make_model(unique_chars)
    model.load_weights(model_name)

    sequence_index = [25]
    for _ in range(10000):
        batch = np.zeros((1, 1))
        batch[0, 0] = sequence_index[-1]
        
        predicted_probs = model.predict_on_batch(batch).ravel()
        sample = np.random.choice(range(unique_chars), size = 1, p = predicted_probs)
        
        sequence_index.append(sample[0])
    
    seq = ''.join(index_to_char[c] for c in sequence_index)

    #saving output
    with open("output_{}.txt".format(model_name[10:22]),"w+") as out:
        out.write(seq)

output_generation('model_512_weights_20.h5')
output_generation('model_512_weights_40.h5')
output_generation('model_512_weights_60.h5')
output_generation('model_512_weights_80.h5')
output_generation('model_512_weights_100.h5')

#################################################################################################################

#plotting graph between epochs and loss,epochs and accuracy
# import matplotlib.pyplot as plt
# plt.figure(1,figsize=(10,10))
# plt.plot(log.Epoch,log.Accuracy)
# plt.title("Graph showing increment of Accuracy with number of Epochs")
# plt.figure(2,figsize=(10,10))
# plt.plot(log.Epoch,log.Loss,color="red")
# plt.title("Graph showing decrement of Loss with number of Epochs")
# plt.show()
