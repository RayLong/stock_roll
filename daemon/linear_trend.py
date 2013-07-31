import sys
import math

'''input data:
   [[high, open, close, low],[....]....] '''

class Point:
    def __init__(self, x, y):
        self.x=x
        self.y=y
    
    def __repr__(self):
        return "Point: x=%f, y=%f" % (self.x, self.y)

class Line:
    def __init__(self, x, y, theta):
        self.x=x
        self.y=y
        self.theta=theta

    def __repr__(self):
        return "Line: x=%f,y=%f,theta=%f" % (self.x , self.y, self.theta)

'''  weighted generalized least square
        
        weight=a*x+b

        the first value of x is -1, we set the weight as 20%
        
        0.2*(1/N)=a*(-1)+b
        0.2/N=b-a => wei_b_a
        
        sum(a*x+b)=1 => sum(a*x+0.2/N+a)=1
        a=(1-0.2)/sum(x+1)    
 
''' 

def linear_trend(data_a):
    if len(data_a) == 1:
       return 0,0,0
    cntOfData=len(data_a)
    wei_b_a=0.1/cntOfData
    points=[]
    for p in data_a:
        points.append(Point(0,0.15*(p[0]+p[3])+0.35*(p[1]+p[2])))
    p_max_y=max(points, key=(lambda p: p.y)).y
#    p_min_y=min(points, key=(lambda p: p.y)).y

    '''nomarlize the value'''
    zero_x_index=len(points)-1
    k=1.0/zero_x_index
    lines=[]
    for i in range(len(points)):
        p=points[i]
        p.x=k*(i-zero_x_index)
        p.y=p.y/(p_max_y)#-p_min_y)

    wei_a=(1.0-wei_b_a*cntOfData)/sum(map(lambda p: p.x+1, points))
    '''
       sum( weight * (y-a*x-b)^2 )=e

       de/da = 2 sum ( weight * ( y - a*x - b) * (-x)) = 0
       de/db = 2 sum ( weight * ( y - a*x - b) * (-1)) = 0

       sum ( -weight*y*x + weight * a * x^2 + b * weight * x) = 0
       sum ( -weight*y + a* weight *x + b*weight) = 0

       A= sum(weight*x^2)
       B= sum(weight*x)
       M= sum(weight)=1
       C= sum(weight*y)
       D= sum(weight*y*x)

       a*A+b*B=D
       a*B+b=C
        
       b=C-a*B

       a*A+B*C-a*B^2=D

       a=(D-B*C)/(A-B^2)
       b=C-(D-B*C)/(A-B^2)*B
       b=(A*C-B*D)/(A-B^2)

    '''
    A=0.0
    B=0.0
    C=0.0
    D=0.0
    for p in points:
        weight=wei_a*p.x+wei_b_a+wei_a
        A+=weight*p.x*p.x
        B+=weight*p.x
        C+=weight*p.y
        D+=weight*p.y*p.x 

    return (D-B*C)/(A-B*B),(A*C-B*D)/(A-B*B),p_max_y#-p_min_y


if __name__ == "__main__":
    n=linear_trend([
		    [15,15,15,15],
            [14,14,14,14],
            [13,13,13,13],
            [12,12,12,12],
            [11,11,11,11],
            [10,10,10,10]
                    ])
    print n
    
