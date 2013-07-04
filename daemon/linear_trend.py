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

def linear_trend(data_a):
    if len(data_a) == 1:
       return 0
    points=[]
    for p in data_a:
        points.append(Point(0,0.15*(p[0]+p[3])+0.35*(p[1]+p[2])))
    p_max_y=max(points, key=(lambda p: p.y)).y
    '''nomarlize the value'''
    zero_x_index=len(points)-1
    k=1.0/zero_x_index
    lines=[]
    for i in range(len(points)):
        p=points[i]
        p.y=p.y/p_max_y
	p.x=k*(i-zero_x_index)
    z_x=points[zero_x_index].x
    z_y=points[zero_x_index].y
    for p in points[:zero_x_index]:
        theta=math.atan2(p.y-z_y,p.x-z_x)
        if theta < 0 : 
             theta = math.pi*2+theta
        l=Line(p.x,p.y,theta)
        lines.append(l)
    theta_min=min(lines, key=(lambda l: l.theta)).theta
    theta_max=max(lines, key=(lambda l: l.theta)).theta
    theta_middle= (theta_min + theta_max) / 2
    while True:
        distance = 0
        for l in lines:
            if theta_middle > l.theta:
               d = -1.0 * math.sqrt(l.x*l.x+l.y*l.y)*math.sin(theta_middle - l.theta)
            elif theta_middle < l.theta:
               d = math.sqrt(l.x*l.x+l.y*l.y)*math.sin(l.theta - theta_middle)
            else :
               d = 0
            distance = distance + d
        if math.fabs(distance) < 0.00001:
            break
        if distance < 0:
            theta_max = theta_middle
        elif distance > 0:
            theta_min = theta_middle
	theta_middle = (theta_max + theta_min) / 2

    if theta_middle > math.pi:
        return math.tan(theta_middle-math.pi)
    elif theta_middle < math.pi:
        return -math.tan(math.pi-theta_middle)

if __name__ == "__main__":
    n=linear_trend([
		    [5,5,5,5],
                    [4,4,4,4],
                    [3,3,3,3],
                    [2,2,2,2],
                    [1,1,1,1],
                    [0,0,0,0]
                    ])
    print n
    
