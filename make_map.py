import random

# l = int(input('number of level: '))
# x = int(input('number of obstacle: '))

LEVEL = 1
SIZE = 20

with open(f"levels\level{LEVEL}.txt", "w") as f:
    text = ''
    for i in range(SIZE):
        for j in range(SIZE):
            if i == 0 or i == SIZE-1 or j == 0 or j == SIZE-1:
                text += '='
            else:
                text += ' '  
        text += '\n'  
    f.write(text)

print('done')