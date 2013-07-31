#import svgwritea
import Image, ImageDraw
import sys
import os
'''data format: [[high, open, close, low],]'''
WIDTH=603.0

def to_image(filename,data): 
  n=len(data)
  height=WIDTH*0.618
  step=WIDTH/(n+1)
  the_max=max(data, key=(lambda d: d[0]))[0]
  the_min=min(data, key=(lambda d: d[3]))[3]
  factor=height/(the_max-the_min)
  im = Image.new('RGB',(int(WIDTH),int(height)),color=(255,255,255,0))
  dwg = ImageDraw.Draw(im)
  for j in range(n):
        i=(j+0.5)*step
        (s_high, s_open, s_close, s_low)=data[j]
        s_high=(the_max-s_high)*factor
        s_open=(the_max-s_open)*factor
        s_close=(the_max-s_close)*factor
        s_low=(the_max-s_low)*factor
        if s_open > s_close:
             the_color='red'
        else:
             the_color='green'
        dwg.line((i, s_high, i, s_low), fill=the_color)
        if s_open > s_close:
            dwg.rectangle((i-step/4,s_close , i+step/4,s_open), fill=the_color)
        else:
            dwg.rectangle((i-step/4,s_open , i+step/4,s_close), fill=the_color)

  del dwg
  im.save(filename,'jpeg')


if __name__=="__main__":
   sys.path.append("../")
   os.environ['DJANGO_SETTINGS_MODULE']='dpin.settings'
   import stocks_db as DB
   db=DB.ORM_Stock()
   data=db.get_stock_data(601555,['high_price','open_price','close_price','low_price'])
   data=map((lambda m : [m['high_price'],m['open_price'],m['close_price'],m['low_price']]), data)
   to_image('test.gif', data)

