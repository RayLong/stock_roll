import unittest
import os
os.environ['DJANGO_SETTINGS_MODULE']='dpin.settings'

import daemon.stocks_db as DB
import daemon.linear_trend as LT
import daemon.drawing_svg as d2svg
import daemon.stock_dl as dl
import json
from tornado import ioloop
class DaemonTestFunctions(unittest.TestCase):
     def test_linear_trend(self):
         data=[[4.09, 3.98, 4.07, 3.98], [4.19, 4.07, 4.16, 4.05], [4.23, 4.16, 4.16, 4.08], [4.25, 4.16, 4.2, 4.12], [4.45, 4.21, 4.35, 4.2], [4.33, 4.31, 4.28, 4.23], [4.3, 4.27, 4.15, 4.1], [4.18, 4.13, 4.17, 4.08], [4.2, 4.17, 4.03, 4.01], [4.05, 4.02, 4.03, 3.99], [4.09, 4.03, 4.08, 4.03], [4.13, 4.1, 4.12, 4.06], [4.12, 4.12, 4.09, 4.05], [4.13, 4.09, 4.1, 4.03], [4.12, 4.07, 4.09, 4.06], [4.11, 4.08, 4.04, 4.01], [4.09, 4.02, 4.08, 4.01], [4.1, 4.08, 4.1, 4.07], [4.1, 4.1, 4.07, 4.04], [4.13, 4.08, 4.11, 4.07], [4.28, 4.11, 4.17, 4.1], [4.2, 4.15, 4.15, 4.12], [4.25, 4.16, 4.23, 4.16], [4.28, 4.19, 4.17, 4.14], [4.22, 4.17, 4.16, 4.13], [4.21, 4.16, 4.21, 4.1], [4.26, 4.2, 4.13, 4.13], [4.23, 4.13, 4.2, 4.13], [4.33, 4.19, 4.32, 4.15], [4.34, 4.31, 4.32, 4.25], [4.65, 4.27, 4.39, 4.25], [4.57, 4.36, 4.46, 4.32], [4.63, 4.45, 4.54, 4.41], [4.53, 4.52, 4.41, 4.33], [4.48, 4.41, 4.37, 4.37], [4.81, 4.39, 4.81, 4.38], [5.29, 4.8, 5.28, 4.61], [5.47, 5.05, 5.25, 5.0], [5.3, 5.2, 5.06, 5.04], [5.13, 5.09, 4.99, 4.93], [5.45, 5.02, 5.22, 4.97], [5.3, 5.2, 5.04, 4.86], [5.34, 5.04, 5.28, 4.94], [5.48, 5.2, 5.21, 5.19], [5.37, 5.18, 5.19, 5.16], [5.63, 5.2, 5.39, 5.2], [5.48, 5.31, 5.39, 5.3], [5.47, 5.44, 5.25, 5.21], [5.25, 5.24, 5.24, 5.01], [5.27, 5.23, 5.21, 5.14], [5.22, 5.21, 5.19, 5.1], [5.26, 5.26, 5.12, 5.1], [5.2, 5.12, 5.17, 5.06], [5.32, 5.18, 5.27, 4.97], [5.53, 5.27, 4.96, 4.9], [4.95, 4.95, 4.72, 4.63], [4.8, 4.7, 4.64, 4.6], [4.66, 4.63, 4.6, 4.54], [4.79, 4.6, 4.77, 4.57]]
         (a,b,k) = LT.linear_trend(data[len(data)-20:])
         print a
         d2svg.to_image('test.svg',data[len(data)-20:],a,b,k)
     
     def test_stocks_db(self):
         db=DB.ORM_Stock() 
         print map((lambda a: [a['high_price'],a['open_price'],a['close_price'],a['low_price']]),db.get_stock_data(2240,
                  ['high_price','open_price','close_price','low_price']))

     def test_download_today(self):
         def on_response(data):
             print data
             ioloop.IOLoop.instance().stop()
         dl.download_today('sh000001',on_response)
         ioloop.IOLoop.instance().start()
if __name__ == "__main__":
   unittest.main()
