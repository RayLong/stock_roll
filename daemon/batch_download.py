import sys
import stock_dl
import os
import stocks_db
from datetime import datetime, timedelta, date
from optparse import OptionParser
from functools import partial
from tornado import ioloop
import time

def batch_download2(db, finished):
    stocks=list(db.get_stocks_list())
    print "total stocks = %d" % len(stocks)
    if len(stocks) == 0:
       return False
    class namespace:
        pass
    ns=namespace()
    ns.dl_index=0
    ns.dl_count=0
    def on_data(stock_code, stock_name, data):
        ns.dl_index+=1
        if data:
           print 'save %06d' % stock_code
           db.insert_stock(stock_code, stock_name, 
                     [[datetime.now().strftime('%Y-%m-%d'),
                       data['open'],
                       data['high'],
                       data['low'],
                       data['close'],
                       data['volume'],
                       data['total']]])
        else:
           print 'ignore %06d' % stock_code
        if ns.dl_index == ns.dl_count:
           if (ns.dl_index) < len(stocks): 
              ioloop.IOLoop.instance().add_callback(partial(next_stocks, ns.dl_index))
           else:
              finished(db,None)

    def next_stocks(index):
        for stock in stocks[index:index+100]:
            if stock.stock_code==699001:
               stock_symbol='sh000001'     
            else:
               stock_symbol=stock_dl.stockcode2str(stock.stock_code)
            stock_dl.download_today(stock_symbol,partial(on_data,
                              stock.stock_code, 
                              stock.stock_name))
            ns.dl_count+=1
    next_stocks(0)
    return True

def batch_download(db, start_date, end_date, finished):
    stocks=list(db.get_stocks_list())
    print "total stocks = %d" % len(stocks)
    if len(stocks) == 0:
       return False
    class namespace:
        pass
    ns=namespace()
    ns.dl_count=0
    ns.dl_index=0
    ns.stock_index=0
    def insert_data(stock_code, stock_name, data):
      ns.dl_index+=1
      if len(data):
         print "save %06d" % stock_code
         db.insert_stock(stock_code, stock_name, data)
      else:
         print "ignore %06d" % stock_code
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
          if s[0]==699001:
             stock_symbol='sh000001'     
          else:
             stock_symbol=stock_dl.stockcode2str(s[0])
          if periods[0] is not None:
             ns.dl_count+=1
             result=stock_dl.download_history(stock_symbol, 
                                       periods[0].strftime("%Y-%m-%d"), 
                                       periods[1].strftime("%Y-%m-%d"), 0, 
                                       partial(insert_data,s[0],s[1]))
          if periods[2] is not None:
             ns.dl_count+=1
             result=stock_dl.download_history(stock_symbol, 
                                       periods[2].strftime("%Y-%m-%d"), 
                                       periods[3].strftime("%Y-%m-%d"), 0, 
                                       partial(insert_data,s[0],s[1]))
      
    next_stocks(0)
    return True

