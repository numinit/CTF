# Astral Mind (pwn 500)

Done as part of [ＶＡＰＯＲＳＥＣ](https://ctftime.org/team/45771).
Didn't score points for it during the CTF due to waking up an hour before
the CTF ended after working on it for several hours the prior night... :(

$ nc chal1.swampctf.com 1122

```
April 9, 3018, The bottom of the swamp. You have entered the dungeon in the
house of Esic to burgle its riches as the previous owner passed away a thousand
years ago (what primitive times). After passing through a long stone hallway
you notice a small chamber.

The chamber is empty apart from a small stone table with three suspicious flash
drives and a small wooden box.  Enter a number:

        1. Reset Network
        2. Read data
        3. Edit Weights
        4. Edit Bias
        5. print Weights
        6. print Bias
        7. Open box choose input:

 1. The drive labeled: Amerika, Not Korea. I swears.
 2. The drive labeled: Not Hakers
 3. The drive labeled: great passwds
```

This pwn challenge uses a neural network to perform subtraction, and indexes
the result into an array of function pointers without bounds checking.

You can directly edit the weights of the neurons in the network
in addition to controlling the input biases. The network itself is a 2-layer
network with 3 neurons in the hidden layer.

If you get into the "open box" menu (7) and have gold (option 2 => 3),
you can corrupt the most significant (highest address in little endian)
byte of the first weight in the array of neuron weights.
This gives us control of the sign and part of the exponent of the first
IEEE 754 double there. (This actually doesn't end up being necessary.)

Menu 2 is the important one, though. You enter a number, and it uses a
neural network to subtract 1 from it, and the result is used to index into
an array of function pointers.

There's a function named `call_function` called by menu 2 that's a good
target: it runs `arr[idx](void *)` for an index and an array of function
pointers, without checking the index whatsoever. Since `arr` is on the
stack when a pointer to it is passed to `call_function`, we can write
data to the stack and have the program jump there - if we can control
the index with the neural network.

----

That's as far as I got before falling asleep at 7 AM on the last day of
SwampCTF. I woke up with less than an hour before the CTF ended, so this part
was done after the CTF ended.

The stack looks like this:

```c
uint64_t fn_pointers[3];
uint64_t pad1[3];
uint64_t pad2;
uint64_t pad3;
double weights[12];
double biases[4];
```

The `fn_pointers` array is used to select options in Menu 2. Critically, the
neural network is trained to only spit out 0, 1, or 2, which do exist. However,
since we can modify the neuron weights and biases, that can change...

We can create an arbitrary function pointer by poking a specific IEEE 754
value into the biases array. We can't do the weights array, since those
are more important to the functionality of the neural network itself,
and the network must actually "work" to compute the right index in the
first place. If we train the neural network with modified input biases
(which are just used for "data whitening", i.e. adding some signal to
the input data), it will work as long as we tell the server that we
used those biases - and we want to anyway, the biases will contain function
pointers.

Counting uint64s and doubles: index 19 is the magic index. print_flag lives at
`0x00000555555555b01`, which is a bias of
`4.63557053862839141102593911777e-310` in IEEE 754. Train the neural network to
spit out index 19(ish) with that bias and inform the server what weights and
biases we want. After running Menu 2 with our modified weights and biases,
we get the flag.

`flag{Fire_walk_with_me_}`

[Source](astral.py)
