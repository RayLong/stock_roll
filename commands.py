#!/usr/bin/python
import sys
import os
import time

from datetime import datetime, timedelta, date
from optparse import OptionParser
from functools import partial
from tornado import ioloop
import tornado.wsgi
import tornado.httpserver

os.environ['DJANGO_SETTINGS_MODULE']='dpin.settings'


from django.contrib.auth.models import User
from django.core.handlers import wsgi as django_wsgi


import dpin
from daemon import  stock_dl
from daemon.drawing import to_image
from daemon.linear_trend import linear_trend
from daemon import stocks_db
from pin.models import Post, Likes
from daemon.batch_download import batch_download, batch_download2


def update_post(db):
   stocks_queryset=db.get_stocks_list()

   stock_list=list(stocks_queryset.order_by('gradient'))
   local_path_name=dpin.settings.MEDIA_ROOT+"/"
   superuser_id=User.objects.filter(is_superuser=True)[0].id
   for x in stock_list:
        cal_date=db.get_latest_date(x.stock_code)
        if cal_date == None:
           print "not data, ignore stock:",x.stock_code
           add = Post.objects.filter(pk=x.stock_code)
           if add.exists():
              add.delete()
           continue
        add = Post.objects.filter(pk=x.stock_code)
        if add.count():
           temp=add[0]
           if temp.create != cal_date:
               try:
                   os.remove(local_path_name+'stock_pics/'+str(x.stock_code)+'-'+temp.create.strftime("%Y-%m-%d")+'.svg')
               except OSError:
                   pass
               temp.create=cal_date
               temp.rating=x.gradient
               temp.text=("%06d %s %f\n" % (x.stock_code, x.stock_name, x.gradient))+'date:'+cal_date.strftime('%Y-%m-%d')
               temp.save()
        else:
           add = Post(image="", 
                   url='', 
                   stock_code=x.stock_code,
                   rating=x.gradient,
                   create=cal_date, 
                   text=("%06d %s %f\n" % (x.stock_code, x.stock_name, x.gradient))+'date:'+cal_date.strftime('%Y-%m-%d'),
                   user_id=superuser_id)
           add.save()


def finished(db, start_date):
    print "finishing"
    for stock in db.get_stocks_list():        
        stock_code=stock.stock_code
        stock_name=stock.stock_name 
        stock_data=db.get_stock_data(stock_code, ['trade_date','open_price','high_price','low_price','close_price'])
        data_count=stock_data.count()
        if data_count:
             if stock_data[data_count-1]['trade_date'] != date.today():
                print "[%06d] data is old ignore" % stock_code, stock_data[data_count-1]['trade_date'].strftime('%Y-%m-%d')
                db.add_stock_gradient(stock_code, 0, 0, 0) 
                continue
             if data_count>20:
                data_count-=20
             else:
                data_count=0
             stock_data=map(lambda m:[m['high_price'], m['open_price'], m['close_price'], m['low_price']], list(stock_data[data_count:]))
             gradient,b,k=linear_trend(stock_data)
             db.add_stock_gradient(stock_code, gradient, b, k) 
        else:
             print "[%06d] data is empty" % stock_code
             db.add_stock_gradient(stock_code, 0, 0, 0) 
    update_post(db)
    ioloop.IOLoop.instance().stop()

def get_stocks_list(file_name):
  f=open(file_name,"r")
  stocks=[]
  for l in f:
     temp=l.strip().split('\t')
     stock_code=temp[0]
     stock_name=temp[1]
     if stock_code.isdigit():
        stocks.append([stock_code,stock_name])
  f.close()
  return stocks

parser = OptionParser()
parser.add_option("-a", "--add", type='string', action='store', dest="list_file",
                  help="add stock list from FILE", metavar="FILE")

parser.add_option("-p", "--period", type='string', action='store',
                  help="the period you need to update \"now - period\" to \"now\"")

parser.add_option("-c", "--calculate", action='store_true',
                  help="get the change history of quantities")

parser.add_option("-g", "--get_one", action='store', type='string',
                  help="update quantity")

parser.add_option("-s", "--run-server", dest="run_server", action="store_true",
                  help="run the http server")

parser.add_option("-d", "--download_today", dest="dl_today", action="store_true",
                  help="download stocks data for today!")


(options, args) = parser.parse_args()

if  options.list_file:
    db=stocks_db.ORM_Stock()
    stocks=get_stocks_list(options.list_file)
    for s in stocks: 
       db.add_stock_name(int(s[0]),s[1])

elif options.run_server:
     application = django_wsgi.WSGIHandler()
     container = tornado.wsgi.WSGIContainer(application)
     http_server = tornado.httpserver.HTTPServer(container)
     http_server.listen(8888)
     tornado.ioloop.IOLoop.instance().start()

elif options.period:
    days=timedelta(days=int(options.period))
    end_date=datetime.now()+timedelta(days=1)
    start_date=end_date-days
    #if not stock_dl.check_istradingday():
    #   print "today is not trading day"
    #   exit(1)
    print "downloading..."
    db=stocks_db.ORM_Stock()
    print start_date, end_date
    if batch_download(db, start_date, end_date, finished):
       ioloop.IOLoop.instance().start() 

elif options.dl_today:
     db=stocks_db.ORM_Stock()
     if batch_download2(db,finished):
        ioloop.IOLoop.instance().start()
                      
elif options.get_one:
   db=stocks_db.ORM_Stock()
   print db.get_stock_data(int(options.get_one),['trade_date','open_price','quantity'])

elif options.calculate:
   db=stocks_db.ORM_Stock()
   finished(db,None) 
