#!/usr/bin/python
# -*- coding: utf-8 -*- 
import sys
from datetime import datetime
import lxml.html as lxml_html
import urllib2
import re
import time
import random

from tornado import ioloop
from tornado import httpclient
from functools import partial

def reformat_date(s,prefix):
   date_dt=datetime.strptime(s,"%Y-%m-%d")
   return datetime.strftime(date_dt,prefix+"_year=%Y&"+prefix+"_month=%m&"+prefix+"_day=%d")

def stockcode2str(stock_code):
    if stock_code >= 600000:
       return "sh%06d" % stock_code
    else:
       return "sz%06d" % stock_code

def fetch_url(url):
    s=None
    for x in range(5):
       try:
         f=urllib2.urlopen(url)
         s=f.read()
         f.close()
       except urllib2.URLError, e:
          print >> sys.stderr, "failed on url [%s] \nerror:%s" % (url,e)
          break
       except urllib2.HTTPError, e:
          print >> sys.stderr, "failed on url [%s] \nerror:%s" % (url,e)
          f.close()
       if s is not None:
          break
       time.sleep(10)
    return s

def lxml_parse(url):
    s=None
    for x in range(5):
       try:
         f=urllib2.urlopen(url)
         s=lxml_html.fromstring(f.read())
         f.close()
       except urllib2.URLError, e:
          print >> sys.stderr, "failed on url [%s] \nerror:%s" % (url,e)
          break
       except urllib2.HTTPError, e:
          print >> sys.stderr, "failed on url [%s] \nerror:%s" % (url,e)
          f.close()
       if s is not None:
          break
       time.sleep(10)
    return s


'''
#get the total quantity
   url="http://yahoo.compass.cn/stock/realstock.php?code="+stockcode2str(stock_code)
   while True:
     f=None
     try:
       f=urllib2.urlopen(url)
       s=f.read()
     except IOError, e:
       print >> sys.stderr, "failed on url [%s] \nerror:%s" % (url,e)
       time.sleep(5)
     finally:
       f.close()
     if s is not None:
        break

   matches=re.search(r'\\"tq\\": ([0-9\.]+)',s)
   if matches is not None:
      total_equity=matches.group(1)
      if verbose ==  1:
         print "circulating shares:%s" % total_equity
   else:
      if verbose == 1:
         print "failed to parse total equity:%s" % e
      return -1

'''

def download_f10(stock_code):
    stock_type='SH'
    if stock_code < 600000:
       stock_type='SZ'
    #"http://yahoo.compass.cn/mirror/F10/SHHQ600613_d_3.html?r=312314"
    url="http://yahoo.compass.cn/mirror/F10/%sHQ%06d_d_3.html?r=%d" % (stock_type, stock_code, int(random.random()*100000))
    doc=lxml_parse(url)
    if doc is None:
       print "failed to parse %s" % url
       return []
    for x in doc.cssselect('body pre'):
         text=x.text
    lines=text.split("\r\n")
    anchor1=re.compile(u'【历次股本变更状况】', re.U)
    anchor2=re.compile(u'─────', re.U)
    state=0
    index = 0
    change_history_text=[]
    for line in lines:
        if state == 0:
           m=anchor1.search(line)
           if m:
              state+=1
        elif state == 1:
           index +=1
           if index == 3:
              state+=1
        elif state == 2:
            m=anchor2.search(line)
            if m is None:
                res=line.split(u'\u2502')[:2]
                if re.search('\d{4}-\d{2}-\d{2}', res[0]):
                   try:
                        float(res[1])
                   except:
                        pass
                   else:
                        res[0]=res[0].strip()
		        change_history_text.append(res) 
            else:
                break
    return change_history_text  


def check_istradingday():
    url = 'http://hq.sinajs.cn/list=sh000001'
    doc=fetch_url(url)
    if doc is None:
       print 'download failed'
       return False
    if '=' in doc: 
        s=doc.split('=')[1]
        if ',' in s:
            trading_date=s.split(',')[-3]
            if trading_date == datetime.now().strftime("%Y-%m-%d"):
                return True
    return False
    
def async_fetch(url, callback):
    hc=httpclient.AsyncHTTPClient()
    class namespace:
          pass
    ns=namespace()
    ns.callback_count=0
    def on_response(respone):
        ns.callback_count+=1
        if respone.error:
           print respone.error
           if ns.callback_count < 5:
              ioloop.IOLoop.instance().add_timeout(10000, partial(hc.fetch, url, callback=on_response))
              return
           else:
              contents=None
        else:
           contents=respone.buffer.read()
        if callback:
           callback(contents)
    hc.fetch(url, callback=on_response)


def download_history(stock_code, start_date_str, end_date_str, verbose, callback=None):
   url="http://yahoo.compass.cn/stock/frames/frmHistoryDetail.php"
   start_date_para=reformat_date(start_date_str,"start")
   end_date_para=reformat_date(end_date_str,"end")
   url=url+"?his_type=day&code="+stockcode2str(stock_code)+"&"+start_date_para+"&"+end_date_para
   
   if verbose == 1:
     print "handling...",url
   class namespace:
         pass
   ns=namespace()
   ns.all_data=[]
   ns.page_count=1
   ns.page_index=0
   def cb(response,handle_pages=True):
       ns.page_index+=1
       if response:
	       doc=lxml_html.fromstring(response)
	       if handle_pages:
			pages=[]
			for x in doc.cssselect('body div a'):
			     if x is not None and x.text.isdigit():
				 if x.get('href').find('/stock/frames/frmHistoryDetail.php') == 0:
				    pages.append("http://yahoo.compass.cn"+x.get('href'))
			ns.page_count+=len(pages)
			for p in pages:
			    async_fetch(p,partial(cb, handle_pages=False))
		   
	       
	       for trow in doc.cssselect('table[class="table-style1"] tbody tr'):
		   data=[]
		   data.append(trow.cssselect('th')[0].text)
		   for td in trow.cssselect('td'):
		       data.append(td.text.replace(',',''))
		   ns.all_data.append(data)

       if (ns.page_index == ns.page_count) and callback:
              callback(ns.all_data)
   async_fetch(url, cb) 

random.seed()

if __name__=="__main__":
   def insert(*args):
       print args
   if len(sys.argv) == 5:
      download_history(int(sys.argv[1]),sys.argv[2],sys.argv[3],int(sys.argv[4]),insert) 
   elif len(sys.argv) == 2:
      print download_f10(int(sys.argv[1]))
   elif len(sys.argv) == 1:
      #check_istradingday()
      def cb(data):
         print data
         ioloop.IOLoop.instance().stop()
      async_fetch('http://www.google.com',cb)
   else:
      print >>sys.stderr, "need one or four parameters"
      exit(1)
   ioloop.IOLoop.instance().start()
