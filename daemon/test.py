import sys
sys.path.append('../')
from stocks_db import ORM_Stock
db=ORM_Stock()
db.insert_stock(600000, 'pufayinhang',[['2013-4-1',50,50,50,50,100,500],['2013-4-2',60,60,60,60,300,700]],[['2013-3-1',900],['2013-2-1',700]])
print db.get_latest_date(600001)
print db.get_earliest_date(600001)
print db.check_exists(600000, '2013-3-1', '2013-5-2')
