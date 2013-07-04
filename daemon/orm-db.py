import sys
import os
import time
sys.path.append("../")
from pin.models import Post

for dirname, subdirs, files in os.walk('../pin/media/pin/stock_pics'):
   #print "f =",files
   #print "dir =",dirname
   #print "sub =", subdirs
   for f in files:
       add = Post(image=('stock_pics/%s' % f),url=('/media/stock_pics/%s' % f) , timestamp=int(time.time()),user_id=12) 
       add.save()
