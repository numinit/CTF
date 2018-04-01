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

More neural network insanity. By the same author and uses the same libraries
the author did for the "Pilgrim" puzzle, so hopefully will be easier than it
otherwise would have been.

There's a function named `call_function` that’s nice: it runs `arr[idx](void *)`
for an index and an array of function pointers. It doesn’t check the index.

There's only one reference to this function -- in main. This means that the
reference is on the critical path for the exploit.

If you get into the "open box" menu (7) and have gold (2 => 3), you can corrupt
the most significant (highest address in little endian) byte of the first
weight in the array of neuron weights. This gives us control of the sign and
part of the exponent of the first IEEE 754 double there. (This actually doesn’t
end up being necessary.)

Menu 2 is sort of hilarious. You enter a number, and it uses a neural network
to subtract 1 from it, and the result is used to index into an array of
function pointers.

So the gameplan is to train the neural network to spit out a bad index into a
table of function pointers. ASLR is disabled on the machine, so we know where
`print_flag` lives (+0x1b01).

----

That's as far as I got before falling asleep at 7 AM on the last day of
SwampCTF. I woke up with less than an hour before the CTF ended, so this part
was done the following night.

We can create an arbitrary function pointer by poking in a specific IEEE 754
value to the biases array. ~I don't know how well we can control this though -
the weights are pretty important?~ Actually, we can use the biases array
instead. If we train the neural network with those input biases (which are
really used for "data whitening", i.e. adding some signal to the input data), it
will work. 

The stack looks like this (all quadwords):

```c
uint64_t fn_pointers[3];
uint64_t pad1[3];
uint64_t pad2;
uint64_t pad3;
double weights[12];
double biases[4];
```

Menu 2 indexes into the `fn_pointers` array, and doesn't bounds check. So we
can shoot beyond it.

Counting uint64s and doubles: index 19 is the magic index. print_flag lives at
`0x00000555555555b01`, which is a bias of
`4.63557053862839141102593911777e-310` in IEEE 754. Train the neural network to
spit out index 19(ish) with that bias and we get the flag.

`flag{Fire_walk_with_me_}`

