'''
* 8 -  1
4 * 11 *
+ 4 -  18
x - 9  *
'''


floor = '''
*   8  -   1

4   *  11  *

+   4  -   18
 
22  -  9   *
'''.strip().split()
print(floor)

def solve(r,c,moves,state,op):
    tile = floor[r*4+c]
    if len(moves) >= 13:
        return
    if r == 3 and c == 0 and len(moves) != 0:
        return
    if tile in '*-+':
        op = tile
    else:
        if op == '+':
            state += int(tile)
        elif op == '*':
            state *= int(tile)
        elif op == '-':
            state -= int(tile)
        if state < 0 or state >= 0x8000:
            return
    if r == 0 and c == 3:
        if state != 30:
            return
        print(len(moves)+1, moves+[tile])
    if r > 0:
        solve(r-1, c, moves+[tile], state, op)
    if r < 3:
        solve(r+1, c, moves+[tile], state, op)
    if c > 0:
        solve(r, c-1, moves+[tile], state, op)
    if c < 3:
        solve(r, c+1, moves+[tile], state, op)

solve(3,0,[],0,'+')
