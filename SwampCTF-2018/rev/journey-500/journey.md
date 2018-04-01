# journey (rev500)

It's an executable packed with UPX. Run: `upx -d journey`

You get an executable. It asks for a password. The password is the string that, when run against 0x328f3b67d25391, [Gronsfeld deciphers](http://rumkin.com/tools/cipher/gronsfeld.php) to "theresanotherstep"

```python
#!/usr/bin/env python

target = 'theresanotherstep'
x = 0x328F3B67D25391

pwd = ''
for char in target:
    y = x % 10
    x //= 10
    z = chr(ord(char) + y)
    pwd += z

print('flag{%s}' % pwd)
```

flag{wkitfudrpxkgsvviq}

