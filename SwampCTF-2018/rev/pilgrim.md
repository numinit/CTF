# Pilgrim (rev500)

$ nc chal1.swampctf.com 1900

```
You awake in the swamp temple, july 3, 3085. The mist of the early morning dampens your leather armor while you hear the wildlife of the wetlands begin the day.

A pilgrim approaches.
Hi:)
Enter a number:
        1. Reset Network
        2. Speak
        3. Directly Edit Weights
        4. Directly Edit bias
```

Download "NNawkward_pilgrim" - it’s an x86_64 binary. Run strings, and... oh boy.

It's not stripped, which is a breath of fresh air after the gameboy challenge,
but it's full of C++ templates.

```
/home/ambrose/eigen/Eigen/src/Core/PlainObjectBase.h
(!(RowsAtCompileTime!=Dynamic) || (rows==RowsAtCompileTime)) && (!(ColsAtCompileTime!=Dynamic) || (cols==ColsAtCompileTime)) && (!(RowsAtCompileTime==Dynamic && MaxRowsAtCompileTime!=Dynamic) || (rows<=MaxRowsAtCompileTime)) && (!(ColsAtCompileTime==Dynamic && MaxColsAt>
((SizeAtCompileTime == Dynamic && (MaxSizeAtCompileTime==Dynamic || size<=MaxSizeAtCompileTime)) || SizeAtCompileTime == size) && size>=0
/home/ambrose/eigen/Eigen/src/Core/DenseCoeffsBase.h
index >= 0 && index < size()
row >= 0 && row < rows() && col >= 0 && col < cols()
/home/ambrose/eigen/Eigen/src/Core/CommaInitializer.h
m_row<m_xpr.rows() && "Too many rows passed to comma initializer (operator<<)"
m_col<m_xpr.cols() && "Too many coefficients passed to comma initializer (operator<<)"
```

As it turns out, it's statically linked with
[Eigen](http://eigen.tuxfamily.org/index.php?title=Main_Page) and contains a
4x4 feedforward neural network that by default responds with "Hi:)". After some
reverse engineering, the goal is to manually train it to say "flag" by mucking
with the weights of the neurons.

The neural network outputs values normalized in (0..1) that are multiplied
by 256 and floored to get each byte of the network's response to the user.
If the response is "flag", the flag is printed.

This is a very standard neural network and I had no idea how the libraries for
dealing with these worked before this challenge. Nimblenet is seemingly used
for creating tiny neural nets, I guess? Change the cost function to something
that I've heard of and interact with the server using pwntools.

Ask the server to change the weights to our calculated weights, and set the
biases to our generated network's input biases. Then "speak" with the pilgrim,
and we get our flag...

`flag{its_a_Mind_Flayer_}`

[Source](pilgrim.py)
