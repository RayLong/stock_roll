import sys
import stock_dl
import os
import stocks_db
from datetime import datetime, timedelta, date
from optparse import OptionParser
from functools import partial
from tornado import ioloop
import time

def batch_download(db, start_date, end_date, finished):
    stocks=list(db.get_stocks_list())
    print "total stocks = %d" % len(stocks)
    class namespace:
        pass
    ns=namespace()
    ns.dl_count=0
    ns.dl_index=0
    ns.stock_index=0
    def insert_data(stock_code, stock_name, data):
      ns.dl_index+=1
      print "dl[%d], dl total=%d" % (ns.dl_index, ns.dl_count)
      if len(data):
         print "save %06d" % stock_code
         db.insert_stock(stock_code, stock_name, data)
      if ns.dl_index == ns.dl_count:
            if (ns.stock_index) < len(stocks):
               ioloop.IOLoop.instance().add_callback(partial(next_stocks, ns.stock_index))
            else:
               finished(db, start_date)

    def next_stocks(index):
      for stock in stocks[index:index+100]:
          ns.stock_index+=1
          s=[stock.stock_code, stock.stock_name]
          periods=db.check_exists(s[0],start_date.strftime("%Y-%m-%d"),end_date.strftime("%Y-%m-%d"))
               
          if periods[0] is not None:
             ns.dl_count+=1
             result=stock_dl.download_history(s[0], 
                                       periods[0].strftime("%Y-%m-%d"), 
                                       periods[1].strftime("%Y-%m-%d"), 1, 
                                       partial(insert_data,s[0],s[1]))
          if periods[2] is not None:
             ns.dl_count+=1
             result=stock_dl.download_history(s[0], 
                                       periods[2].strftime("%Y-%m-%d"), 
                                       periods[3].strftime("%Y-%m-%d"), 1, 
                                       partial(insert_data,s[0],s[1]))
      

    next_stocks(0)

