x, y = 3,3

print([(y2,x2) for y2 in range(0,x) for x2 in range(0,y)].remove
      ((0,0)))
