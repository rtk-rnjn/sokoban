from os import system as s
import random

array = [
	[[0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6]],
	[[1, 0], [1, 1], [1, 2], [1, 3], [1, 4], [1, 5], [1, 6]],
	[[2, 0], [2, 1], [2, 2], [2, 3], [2, 4], [2, 5], [2, 6]],
	[[3, 0], [3, 1], [3, 2], [3, 3], [3, 4], [3, 5], [3, 6]],
	[[4, 0], [4, 1], [4, 2], [4, 3], [4, 4], [4, 5], [4, 6]],
	[[5, 0], [5, 1], [5, 2], [5, 3], [5, 4], [5, 5], [5, 6]],
	[[6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6]],
    ]

while True:
    man_pos = [random.randint(0,6), random.randint(0,6)]
    block_pos = [random.randint(1,5), random.randint(1,5)]
    target_pos = [random.randint(0,6), random.randint(0,6)]

    if (man_pos == block_pos) or (block_pos == target_pos) or (target_pos == man_pos): pass
    else: break


for pos in array:
    x = str(pos).replace(str(man_pos), '^ ').replace(str(target_pos), '* ').replace(str(block_pos), '# ').replace('[', '_').replace(']', '').replace(',', '')
    x = x.replace('6', '').replace('5', '').replace('4', '').replace('3', '').replace('2', '').replace('1', '').replace('0', '')
    print(x)

print man_pos
print block_pos
print target_pos 

while True:
    cmd = raw_input("Enter the command (w, a, s, d):\n")
    if cmd.lower() == 'q' or cmd.lower() == 'quit': break
    else:
        if cmd.lower() == 'w':
            if man_pos[0] == 0: pass
            else: 
                if [man_pos[0] - 1, man_pos[1]] == block_pos:
                    if block_pos[0] == 0: pass
                    else:
                        block_pos = [block_pos[0] - 1, block_pos[1]]
                        man_pos = [man_pos[0] - 1, man_pos[1]]
                else:
                    man_pos = [man_pos[0] - 1, man_pos[1]]
            s('cls')
            for pos in array:
                x = str(pos).replace(str(man_pos), '^ ').replace(str(target_pos), '* ').replace(str(block_pos), '# ').replace('[', '_').replace(']', '').replace(',', '')
                x = x.replace('6', '').replace('5', '').replace('4', '').replace('3', '').replace('2', '').replace('1', '').replace('0', '')
                print(x)
            print man_pos
            print block_pos
            print target_pos 

        elif cmd.lower() == 's':
            if man_pos[0] == 6: pass
            else: 
                if [man_pos[0] + 1, man_pos[1]] == block_pos:
                    if block_pos[0] == 6: pass
                    else:
                        block_pos = [block_pos[0] + 1, block_pos[1]]
                        man_pos = [man_pos[0] + 1, man_pos[1]]
                else:
                    man_pos = [man_pos[0] + 1, man_pos[1]]
        
            s('cls')
            for pos in array:
                x = str(pos).replace(str(man_pos), '^ ').replace(str(target_pos), '* ').replace(str(block_pos), '# ').replace('[', '_').replace(']', '').replace(',', '')
                x = x.replace('6', '').replace('5', '').replace('4', '').replace('3', '').replace('2', '').replace('1', '').replace('0', '')
                print(x)
            print man_pos
            print block_pos
            print target_pos 

        elif cmd.lower() == 'a':
            if man_pos[1] == 0: pass
            else:
                if [man_pos[0], man_pos[1] - 1] == block_pos:
                    print 'get it 2'
                    if block_pos[1] == 0: pass
                    else:
                        print 'get it 3'
                        block_pos = [block_pos[0], block_pos[1] - 1]
                        man_pos = [man_pos[0], man_pos[1] - 1]
                else:
                    man_pos = [man_pos[0], man_pos[1] - 1]
        
            s('cls')
            for pos in array:
                x = str(pos).replace(str(man_pos), '^ ').replace(str(target_pos), '* ').replace(str(block_pos), '# ').replace('[', '_').replace(']', '').replace(',', '')
                x = x.replace('6', '').replace('5', '').replace('4', '').replace('3', '').replace('2', '').replace('1', '').replace('0', '')
                print(x)
            print man_pos
            print block_pos
            print target_pos 

        elif cmd.lower() == 'd':
            if man_pos[1] == 6: pass
            else: 
                if [man_pos[0], man_pos[1] + 1] == block_pos:
                    if block_pos[1] == 6: pass
                    else:
                        block_pos = [block_pos[0], block_pos[1] + 1]
                        man_pos = [man_pos[0], man_pos[1] + 1]
                else:
                    man_pos = [man_pos[0], man_pos[1] + 1]
        
            s('cls')
            for pos in array:
                x = str(pos).replace(str(man_pos), '^ ').replace(str(target_pos), '* ').replace(str(block_pos), '# ').replace('[', '_').replace(']', '').replace(',', '')
                x = x.replace('6', '').replace('5', '').replace('4', '').replace('3', '').replace('2', '').replace('1', '').replace('0', '')
                print(x)
            print man_pos
            print block_pos
            print target_pos 
    if block_pos == target_pos: break

print "YOU WIN"
