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
from daemon.batch_download import batch_download


def update_post(db):
   stocks_queryset=db.get_stocks_list()
   stock_list=list(set(map((lambda a: a.post.stock_code), Likes.objects.exclude(user_id=1))))

   local_path_name=dpin.settings.MEDIA_ROOT+"/stock_pics/"
   if len(stock_list):
      stock_pictures=Post.objects.exclude(stock_code__in=stock_list)
      stock_list=list(stocks_queryset.filter(stock_code__in=stock_list))
   else:
      stock_pictures=Post.objects.all()

   for pp in stock_pictures:
       try:
           os.remove(local_path_name+str(pp.stock_code)+".jpg")
       except OSError:
           print "remove file failed"
   stock_pictures.delete()

   stock_list+=list(stocks_queryset.order_by('gradient')[:20])
   for x in stock_list:
       stock_data=db.get_stock_data(x.stock_code, 
                   ['trade_date','open_price','high_price',
                     'low_price','close_price']).order_by('trade_date')
       if stock_data.count():
            cal_date=stock_data[stock_data.count()-1]['trade_date'].strftime('%Y-%m-%d')
            stock_data=map(lambda m:[m['high_price'], 
                           m['open_price'], m['close_price'], 
                           m['low_price']], stock_data)
            file_name=str(x.stock_code)+".jpg"
            to_image(local_path_name+file_name, stock_data)
            superuser_id=User.objects.filter(is_superuser=True)[0].id
            add = Post.objects.filter(pk=x.stock_code)
            if add.count():
               temp=add[0]
               temp.rating=x.gradient
               temp.create=cal_date
               temp.save()
            else:
               add = Post(image=('stock_pics/'+file_name ), 
                       url=('/media/stock_pics/'+file_name ), 
                       stock_code=x.stock_code,
                       rating=x.gradient,
                       create=cal_date, 
                       text=("%06d %s\n%f" % (x.stock_code, x.stock_name, x.gradient)),
                       user_id=superuser_id)
               add.save()


def finished(db, start_date):
    print "finishing"
    if start_date:
        db.delete_earlier_than(start_date)
    for stock in db.get_stocks_list():        
        stock_code=stock.stock_code
        stock_name=stock.stock_name 
        stock_data=db.get_stock_data(stock_code, ['trade_date','open_price','high_price','low_price','close_price']).order_by('trade_date')
        if stock_data.count():
             stock_data=map(lambda m:[m['high_price'], m['open_price'], m['close_price'], m['low_price']], stock_data)
             v_max=0
             i_max=0
             for i in range(len(stock_data)):
                 if stock_data[i][0] > v_max:
                    v_max=stock_data[i][0]
                    i_max=i
             if i_max < len(stock_data) - 1:
                stock_data=stock_data[i_max:]
                gradient=linear_trend(stock_data)
                db.add_stock_gradient(stock_code, gradient) 
             else:
                 v_min=stock_data[0][0]
                 i_min=0
                 for i in range(len(stock_data)):
                     if stock_data[i][0] < v_min:
                        v_min=stock_data[i][0]
                        i_min=i
                 stock_data=stock_data[i_min:]
                 gradient=linear_trend(stock_data)
                 db.add_stock_gradient(stock_code, gradient)
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
    if not stock_dl.check_istradingday():
       print "today is not trading day"
       exit(1)
    print "downloading..."
    db=stocks_db.ORM_Stock()
    print start_date, end_date
    batch_download(db, start_date, end_date, finished)
    ioloop.IOLoop.instance().start() 
                      
elif options.get_one:
   db=stocks_db.ORM_Stock()
   print db.get_stock_data(int(options.get_one),['trade_date','open_price','quantity'])

elif options.calculate:
   db=stocks_db.ORM_Stock()
   finished(db,None) 
