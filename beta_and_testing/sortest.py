from collections import OrderedDict
import random

d = {}
d.update({'a':(3,5.2),'b':(1.8,2),'c':(1.9,6),'d':(5,7),'e':(4,11),'f':(0,1)})

#print(d)

#print(dir(d))

#print(dict(sorted(d.items(), key = lambda t: t[1])))

a = 'd'

b = (1,2)
print(b + (a,))

"""
d,r
ALLOWED
l,d
l,u
u,d
u,l
r,u
r,l
r,d
    
d, u
ALLOWED:
l,d
u,l
u,d

d,l
ALLOWED:
l,d
u,r
r,u

l,d
ALLOWED:
d,r
d,u
d,l
u,l
u,r
r,l
r,u

l,u
ALLOWED:
d,r
u,l
r,d

l,r
ALLOWED:
l,u
u,l
r,u

u,d
ALLOWED:
d,r
d,u
r,u

u,l
ALLOWED:
d,r
d,u
l,d
l,r
l,u
r,d
r,u

u,r
ALLOWED:
d,l
l,d
r,u

r,d
ALLOWED:
d,r
l,u
u,l

r,l
ALLOWED:
d,r
l,d
l,r


    u

l       r

    d
"""
