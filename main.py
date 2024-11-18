from __future__ import (absolute_import, division, print_function,unicode_literals)
import backtrader as bt
import os.path
from strategy import Strategy

    
if __name__ == '__main__':
	# create a cerebro entity
	cerebro = bt.Cerebro()
	cerebro.addstrategy(Strategy)

	#datapath  = os.path.join('Datafeeds', 'orcl-1995-2014.txt')
	#datapath = os.path.join('Datafeeds', 'nvda-1999-2014.txt')
	#datapath = os.path.join('Datafeeds', 'yhoo-1996-2015.txt')
	#datapath = os.path.join('Datafeeds', 'AAPL-14-24.csv')
	datapath = os.path.join('Datafeeds', 'AMZN-14-24.csv')
	#datapath = os.path.join('Datafeeds', 'GOOGL-14-24.csv')
	#datapath = os.path.join('Datafeeds', 'MSFT-14-24.csv')

	data = bt.feeds.YahooFinanceCSVData(
		dataname=datapath,
		reverse=False,
    adjclose=False
	)

	# Add the Data Feed to Cerebro
	cerebro.adddata(data) 
	cerebro.broker.setcommission(commission=0.001)
	cerebro.broker.setcash(100000.0)

	print('Valor inicial de la cartera: %.2f' % cerebro.broker.getvalue())

	cerebro.run()

	print('Valor final de la cartera: %.2f' % cerebro.broker.getvalue())
	
	cerebro.plot()