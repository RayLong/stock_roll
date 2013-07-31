import svgwrite
import sys
import os
import re

'''data format: [[high, open, close, low],]'''
WIDTH=603.0

def to_image(filename, data, a, b, k): 
  n=len(data)
  if n < 2:
     return '<svg></svg>'    
  height=WIDTH*0.618
  step=WIDTH/(n+1)
  line_width=step/20.0
  the_max=max(data, key=(lambda d: d[0]))[0]
  the_min=min(data, key=(lambda d: d[3]))[3]
  if the_max == the_min:
    the_max = the_min + the_min/4
    the_min = the_min - the_min/4
  factor=height/(the_max-the_min)
  dwg = svgwrite.Drawing(filename, profile='tiny',viewBox="0 0 "+str(WIDTH)+' '+str(height))
  dwg.add(dwg.line((0.5*step,(the_max-(b-a)*k)*factor),((n-0.5)*step,(the_max-b*k)*factor),stroke_width=line_width, stroke='blue'))
  for j in range(n):
        i=(j+0.5)*step
        (s_high, s_open, s_close, s_low)=data[j]
        
        if s_open >= s_close:
             the_color='green'
        else:
             the_color='red'

        s_high=(the_max-s_high)*factor
        s_open=(the_max-s_open)*factor
        s_close=(the_max-s_close)*factor
        s_low=(the_max-s_low)*factor

        if s_high == s_low:
              s_high-=s_high*0.005
              s_low+=s_low*0.005
        if s_open == s_close:
              s_open+=s_open*0.005
              s_close-=s_close*0.005

        dwg.add(dwg.line((i, s_high), (i, s_low), stroke_width=line_width, stroke=the_color))
        if s_open > s_close:
            dwg.add(dwg.rect((i-step/4,s_close ), (step/2,s_open-s_close), stroke_width=line_width, stroke=the_color, fill=the_color))
        else:
            dwg.add(dwg.rect((i-step/4,s_open ), (step/2,s_close-s_open), stroke_width=line_width, stroke=the_color, fill=the_color))
  dwg.save()
  return dwg.tostring()

if __name__=="__main__":
   #sys.path.append("../")
   #os.environ['DJANGO_SETTINGS_MODULE']='dpin.settings'
   #import stocks_db as DB
   #db=DB.ORM_Stock()
   #data=db.get_stock_data(22,['high_price','open_price','close_price','low_price'])
   #if data.count():
   #    data=map((lambda m : [m['high_price'],m['open_price'],m['close_price'],m['low_price']]), data)
   to_image('test2.svg', [[20,19,15,10],[25,14,21,10],[15,13,13.5,11],[10,9,8,5]],3, 2, 3)
