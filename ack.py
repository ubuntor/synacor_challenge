import functools
import sys

sys.setrecursionlimit(100000)
mask = 0x7fff
mod =  0x8000

def blah(n, key):
    if key == 0:
        return n
    res = 0
    base = key+1
    for i in range(n):
        res = (res*base+1) & mask
    return res


'''
elif m == 1:
    return (key+n+1) & mask
elif m == 2:
    return ((key+1)*(n+2)-1) & mask
elif m == 3:
    return (key + (key+1)**2 + ((key+1)**3)*blah(n,key)) & mask



(1 + 4 + ((2)**3)*((2)**n - 8))
'''

@functools.lru_cache(maxsize=None)
def ackermann(m,n,key):
    #print(m,n,key)
    if m == 0:
        return (n+1) & mask
    elif m == 1:
        return (key+n+1) & mask
    elif m == 2:
        return ((key+1)*(n+2)-1) & mask
    elif m == 3:
        return (key + (key+1)**2 + ((key+1)**3)*blah(n,key)) & mask
    elif n == 0:
        return ackermann(m-1, key, key)
    return ackermann(m-1, ackermann(m, n-1, key), key)

'''
for n in range(20):
    for key in range(20):
        test = ((key+1)*(n+2)-1) & mask
        res = ackermann(2, n, key)
        print(n, key, test, res, res-test)
    print()
'''

#for key in range(0x8000)[::-1][10:
#    print(ackermann(4, 1, key))

'''
for key in range(10):#range(0x8000)[::-1]:
    #print(i, ((i+1)*(123+2)-1) & mask, ackermann(2, 123, i))
    #assert(((i+1)*(23+2)-1) & mask == ackermann(2, 23, i))
    res = ackermann(4, 1, key)
print()
'''


for key in range(0x8000):
    res = ackermann(4, 1, key)
    #if key % 1000 == 0:
    #    print(key, res)
    if res <= 10:
        print("{} -> {}".format(key, res))

'''
n=0: 0
n=1: (key+1)**3
n=2: (key+2)*(key+1)**3

key=1: 8*(2^n-1)

0: key
1: (2^key - 1)/1
2: (3^key - 1)/2.
3: (4^key - 1)/3.
'''
