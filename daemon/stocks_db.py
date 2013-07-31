#!/usr/bin/python

import sys
import re
from datetime import datetime, timedelta
from pin.models import StockList, StockData, StockTrend
from django.db.models import Min, Max
from django.core.exceptions import ObjectDoesNotExist

class ORM_Stock:
   def __init__(self):
       pass
   
   def add_stock_name(self, stock_code, stock_name):
       trend=StockTrend(stock_code=stock_code, a=0, b=0, k=0)
       trend.save()
       stock=StockList(stock_code=stock_code, stock_name=stock_name, gradient=0, trend=trend)
       stock.save()

   def add_stock_gradient(self, stock_code, gradient, b, k):
       stocks=StockList.objects.filter(stock_code=stock_code)
       trend=StockTrend.objects.filter(stock_code=stock_code)
       if trend.exists():
          trend=trend[0]
          trend.a=gradient
          trend.b=b
          trend.k=k
          trend.save()
       else:
          trend=StockTrend(stock_code=stock_code, a=gradient, b=b, k=k)
          trend.save()
        
       if stocks.count():
          x=stocks[0]
          x.gradient=gradient
          x.trend=trend
          x.save()

   '''data format: [trade_date, open_price, high_price, low_price, close_price, volume, qunatity]
      quantity_change_history format [change_date, quantity]'''
   def insert_stock(self, stock_code, stock_name, data, quantity_change_history=[]):
       stocks=StockList.objects.filter(stock_code=stock_code)
       if not stocks.exists():
          stock=StockList(stock_code=stock_code, stock_name=stock_name, gradient=0)
          stock.save()
       else:
          stock=stocks[0]
       
       for row in data:
            stock_data_item=StockData.objects.filter(stock_ref=stock, trade_date=row[0])
            if stock_data_item.count()==0 :
                stock_data_item=StockData(stock_ref=stock,
                             trade_date=row[0],
                             open_price=row[1],
                             high_price=row[2],
                             low_price=row[3],
                             close_price=row[4],
                             volume=row[5],
                             quantity=row[6])
            else:
                stock_data_item=stock_data_item[0]
            stock_data_item.open_price=row[1]
            stock_data_item.high_price=row[2]
            stock_data_item.low_price=row[3]
            stock_data_item.close_price=row[4]
            stock_data_item.volume=row[5]
            stock_data_item.quantity=row[6]
            stock_data_item.save()

   def delete_stock(self, stock_code):
       stocks=StockList.objects.filter(stock_code=stock_code)
       if stocks.count():
          for stock in stocks:
              stock_data_all=StockData.objects.filter(stock_ref=stock)
              if stock_data_all.count() !=0:
                  stock_data_all.delete()
          stocks.delete()

   def delete_earlier_than(self, the_date):
       res=StockData.objects.filter(trade_date__lt=the_date)
       if res.count():
          res.delete()

   def get_stock_data(self, stock_code, columns):
       #stocks=StockList.objects.filter(stock_code=stock_code)
       #if stocks.count():
       #   stock=stocks[0]
       try:
           results=StockData.objects.filter(stock_ref_id=stock_code).values(*columns).order_by('trade_date')
       except ObjectDoesNotExist as e:
          return None
       else:
          return results
       #else:
       #   return None

   def get_latest_date(self,stock_code):
       try:
          results=StockData.objects.filter(stock_ref_id=stock_code).aggregate(Max('trade_date'))['trade_date__max']
       except ObjectDoesNotExist as e:
          return None
       else:
          return results
       

   def get_earliest_date(self,stock_code):
       try:
           res=StockData.objects.filter(stock_ref_id=stock_code).aggregate(Min('trade_date'))['trade_date__min']
       except ObjectDoesNotExist as e :
           return None
       else:
           return res

   def get_stocks_list(self):
       return StockList.objects.all()

   def check_exists(self, stock_code, start_date, end_date):
       s_d=self.get_earliest_date(stock_code)
       ss_d=datetime.date(datetime.strptime(start_date,"%Y-%m-%d"))
       ee_d=datetime.date(datetime.strptime(end_date,"%Y-%m-%d"))
       if s_d is None:
          return [ss_d, ee_d, None, None]

       e_d=self.get_latest_date(stock_code)
       if ss_d < s_d:
         s1=ss_d
         s2=s_d
         if ee_d > e_d:
            s3=e_d
            s4=ee_d
         else:
            s3=s4=None
       else:
         s1=s2=None
         if ee_d <= e_d:
            s3=s4=None
         else:
            s3=e_d
            s4=ee_d
       return [s1, s2, s3, s4]

