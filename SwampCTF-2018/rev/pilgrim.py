#!/usr/bin.env python

from pwn import *

from nimblenet.activation_functions import sigmoid_function
from nimblenet.cost_functions import *
from nimblenet.learning_algorithms import *
from nimblenet.data_structures import Instance
from nimblenet.neuralnet import NeuralNet

ins = [1,1,1]`

f = ord('f') / 256.0
l = ord('l') / 256.0
a = ord('a') / 256.0
g = ord('g') / 256.0

dataset = [
    Instance(ins, [f, l, a, g])
]

settings = {
    "n_inputs" : 3,
    "layers" : [(4, sigmoid_function)] * 1
}

network        = NeuralNet(settings)
training_set   = dataset
test_set       = dataset
cost_function  = sum_squared_error

scipyoptimize(
    network,           # the network to train
    training_set,      # specify the training set
    test_set,          # specify the test set
    cost_function,     # specify the cost function to calculate error
)

layer = network.weights[0]

conn = remote('chal1.swampctf.com', 1900)
conn.sendline('1')
conn.sendline('3')
conn.sendline()
for row in layer:
    for col in row:
        conn.sendline('%.14f' % col)
conn.sendline('4')
conn.sendline()
for i in range(8):
    conn.sendline('%.14f' % network.initial_bias_value)
conn.sendline('2')
conn.interactive()

prediction_set = [Instance(ins)]
prediction = network.predict(prediction_set)[0]
s = ''
for val in prediction:
    byte = int((val * 256) + 0.5)
    s += chr(byte)
print('We predicted: %s' % s)
