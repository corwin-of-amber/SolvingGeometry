#  API
circle(O,r) # Gets radius and center and returns object of type circle
dist(X,Y) # Gets 2 points and returns the dist between them
segment(A,B) # Gets two points, return segment between A and B
rayvec(A,u) # Gets origin of ray (A) and vector (u) - returns ray
linevec(A,u) # Gets point on the line (A) and vector (u) - returns ray

vecOpNegate(v) # Gets vector and negates it
rotateCw(v,a)
rotateCcw(v,a)
angleCcw(A,B,C) # returns the angle between A, B, C (ccw)
vecFrom2Points(z, y) # Gets 2 points and returns the vector z-y (the vector from z to y)

# new to API:
middle(A, B): return the middle point between points A, B
middle1(A, C): return point B, when C is the middle of A, B. (B = 2*C-A)
circleFromDiameter(d): Gets a segment object, return a circle object
circleCenter(c): Gets a circle, return it's center point.
# Rules to handle:





            'circle-center-in-radius': lambda c,O,A,r: bind('dist', (O,A)) # Question: this doesnt make anything known

                                                            

            'arith[-]-0': lambda x,y,z: bind('-', (z,y)),
            'arith[-]-1': lambda x,y,z: bind('-', (z,x)),
            'arith[/]-0': lambda x,y,z: bind('/', (z,y)),
            'arith[*]-0': lambda x,y,z: bind('*', (x,y)),
            'id-0': lambda x,y: y,
            
            
