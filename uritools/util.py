from __future__ import unicode_literals

unicode = type('')
byte = chr if isinstance(chr(0), bytes) else lambda x: bytes((x,))

if b'0'[0] == 48:
    iterbytes = lambda x: x
else:
    iterbytes = lambda x: map(ord, x)
