from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import os.path
import datetime
from strategy import Strategy

if __name__ == '__main__':
	# create a cerebro entity
	cerebro = bt.Cerebro()
	cerebro.addstrategy(Strategy)

	#datapath = os.path.join('Datafeeds', 'orcl-1995-2014.txt')
	#datapath = os.path.join('Datafeeds', 'nvda-1999-2014.txt')
	datapath = os.path.join('Datafeeds', 'yhoo-1996-2015.txt')

	data = bt.feeds.YahooFinanceCSVData(
		dataname=datapath,
		#fromdate=datetime.datetime(1995, 12, 30),
		#todate=datetime.datetime(2000, 12, 30),
		reverse=False
	)

	# Add the Data Feed to Cerebro
	cerebro.adddata(data) 
	cerebro.broker.setcommission(commission=0.001)
	cerebro.broker.setcash(100000.0)

	# Print out the starting conditions
	print('Valor inicial de la cartera: %.2f' % cerebro.broker.getvalue())

	cerebro.run()

	# Print out the final result
	print('Valor final de la cartera: %.2f' % cerebro.broker.getvalue())
	cerebro.plot()