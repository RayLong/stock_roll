#!/usr/bin/python
import sys
import sqlite3
import re
from datetime import datetime, timedelta
from pin.models import StockList, StockData, StockQuantityHistory
from django.db.models import Min
from django.core.exceptions import ObjectDoesNotExist

class ORM_Stock:
   def __init__(self):
       pass
   
   def add_stock_name(self, stock_code, stock_name):
       stock=StockList(stock_code=stock_code, stock_name=stock_name,gradient=0)
       stock.save()

   def add_stock_gradient(self, stock_code, gradient):
       stocks=StockList.objects.filter(stock_code=stock_code)
       if stocks.count():
          x=stocks[0]
          x.gradient=gradient
          x.save(update_fields=['gradient'])

   '''data format: [trade_date, open_price, high_price, low_price, volume, qunatity]
      quantity_change_history format [change_date, quantity]'''
   def insert_stock(self, stock_code, stock_name, data, quantity_change_history=[]):
       stocks=StockList.objects.filter(stock_code=stock_code)
       if stocks.count():
          stock=stocks[0]
       else:
          stock=StockList(stock_code=stock_code, stock_name=stock_name, gradient=0)
          stock.save()
       
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
              stock_history_all=StockQuantityHistory.objects.filter(stock_ref=stock)
              if stock_data_all.count() !=0:
                  stock_data_all.delete()
              if stock_history_all.count() !=0:
	          stock_history_all.delete()
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
           results=StockData.objects.filter(stock_ref_id=stock_code).values(*columns)
       except ObjectDoesNotExist as e:
          return None
       else:
          return results
       #else:
       #   return None

   def get_latest_date(self,stock_code):
       try:
          results=StockData.objects.filter(stock_ref_id=stock_code).latest('trade_date').trade_date
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

'''       

class stocks_db:
   def __init__(self):
       self.cx=sqlite3.connect("./stocks.db")
       self.cu=self.cx.cursor()
       self.cu.execute("create table if not exists stock_data (code int, sdate date, open decimal(5,2), high decimal(5,2), low decimal(5,2), close decimal(5,2), volume decimal(10,2), quantity float, primary key(code, sdate))")
       self.cu.execute("create table if not exists stock_list (code int, name text, primary key(code))")
       self.cu.execute("create table if not exists stock_f10 (code int, change_date date, quantity float, primary key(code, change_date))")
       self.cx.commit()

   def insert_data(self, stock_code, sdate, open_price, high_price, low_price, close_price, volume, amount):
       
       all_str="','".join([sdate, open_price, high_price, low_price, close_price, volume, amount])
       self.cu.execute("insert or replace into stock_data values ('"+str(stock_code)+"','"+all_str+"')")
       self.cx.commit()

   def stock_set_change_history(self, stock_code, history_data):
       for x in history_data:
           self.cu.execute("insert or replace into stock_f10 values ( '%d', '%s', '%f' )" %
                            (stock_code, x[0], float(x[1])))
       self.cx.commit()


   def update_quantity(self):
       self.cu.execute("select code from stock_list")
       x = self.cu.fetchall()
       for c in x:
           code=c[0]
           self.cu.execute("select sdate, quantity from stock_data where code =%d " % code)
           current_data=self.cu.fetchall()
           
           self.cu.execute("select change_date, quantity from stock_f10 where code = %d " % code )
           history = list(self.cu.fetchall())
           history.sort(key=(lambda d: datetime.strptime(d[0].strip(),"%Y-%m-%d")),reverse=True)
           for cd in current_data:
               stock_date=datetime.strptime(str(cd[0]),"%Y%m%d")
               if cd[1]:
                  is_updated = 0
                  for his in history:
                      his_date=datetime.strptime(his[0].strip(),"%Y-%m-%d")
                      if stock_date >= his_date:
                         self.cu.execute("update stock_data set quantity = '%f' where code = '%d' and sdate = '%s'" % ( his[1], code, cd[0]))
			 is_updated = 1
                         break
                  if is_updated == 0:
                       print "failed to update"
           self.cx.commit()
               

   def add_name(self, stock_code, name):
       self.cu.execute("insert or replace into stock_list values ('"+str(stock_code)+"','"+name+"')")
       self.cx.commit()

   def delete_data(self, stock_code, sdate):
       self.cu.execute("delete from stock_data where code = %s and sdate = %s" % (stock_code,sdate))
       self.cx.commit()

   def close(self):
       self.cu.close()
       self.cx.close()

   def show(self):
       self.cu.execute("select * from stock_data")
       for x in self.cu.fetchall():
           print x

   def get_all(self, stock_code):
       self.cu.execute("select high, open, close, low, quantity from stock_data where code=%d" % stock_code )
       return self.cu.fetchall()
       
   def get(self, columns, stock_code, date1, date2):
       d1=datetime.strptime(date1,"%Y-%m-%d").strftime("%Y%m%d")
       d2=datetime.strptime(date2,"%Y-%m-%d").strftime("%Y%m%d")
       sql="select "+columns+" from stock_data where code="+str(stock_code)+" and sdate >='"+d1+"' and sdate <='"+d2+"'"
       self.cu.execute(sql)
       return self.cu.fetchall()
 
   def get_earliest(self,stock_code):
       self.cu.execute("select min(sdate) from stock_data where code="+str(stock_code))
       return str(self.cu.fetchall()[0][0])

   def get_latest(self,stock_code):
       self.cu.execute("select max(sdate) from stock_data where code="+str(stock_code))
       return str(self.cu.fetchall()[0][0])

   def check_exists(self, stock_code, start_date, end_date):
       s=self.get_earliest(stock_code)
       ss_d=datetime.strptime(start_date,"%Y-%m-%d")
       ee_d=datetime.strptime(end_date,"%Y-%m-%d")
       
       if s != "None":
          s_d=datetime.strptime(s,"%Y%m%d")
       else:
          return [ss_d, ee_d, None, None]

       e=self.get_latest(stock_code)
       e_d=datetime.strptime(e,"%Y%m%d")

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

   def show_list(self):
       self.cu.execute("select * from stock_list")
       for x in self.cu.fetchall():
            stock_code, stock_name = x
            print stock_code, stock_name

   def get_stock_list(self):
       self.cu.execute("select * from stock_list")
       return self.cu.fetchall()
         
   
  '''                
