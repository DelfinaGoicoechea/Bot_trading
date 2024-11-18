import backtrader as bt

class Strategy(bt.Strategy):
	params=(
		("period_short_sma",50),
		("period_long_sma",200),
		("rsi_period",14),
		("macd_short",24),
		("macd_long",52),
		("macd_signal",18),
		("bollinger_period",20),
		("bollinger_dev",2),
		("capital_fraction",0.9),
		("commision", 0.001),
	)

	def __init__(self):
		self.dataclose=self.datas[0].close
		
		self.short_sma=bt.indicators.SimpleMovingAverage(
			self.dataclose, 
			period=self.params.period_short_sma
		)

		self.long_sma=bt.indicators.SimpleMovingAverage(
			self.dataclose, 
			period=self.params.period_long_sma
		)

		self.rsi = bt.indicators.RelativeStrengthIndex(
			period=self.params.rsi_period
		)

		self.macd = bt.indicators.MACD(
			self.dataclose,
			period_me1=self.params.macd_short,
			period_me2=self.params.macd_long,
            period_signal=self.params.macd_signal
		)

		self.bollinger = bt.indicators.BollingerBands(
            self.dataclose,
            period=self.params.bollinger_period,
            devfactor=self.params.bollinger_dev
    )
		
	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def volume_to_buy(self) -> int:
		if self.broker.cash >= self.dataclose[0]:
			cash = self.broker.get_cash()*self.params.capital_fraction
			cash = cash-cash*self.params.commision
			return int(cash/self.dataclose[0])
		return 0 
	
	def condition_buy(self):
		golden_cross=self.short_sma[0]>self.long_sma[0]
		rsi_buy=self.rsi[0]<35
		macd_buy=self.macd.macd[0] > 0 and self.macd.signal[0] > 0 and self.macd.macd[0] > self.macd.signal[0]
		bollinger_buy=self.dataclose[0] < self.bollinger.lines.bot
		conditions = [golden_cross, rsi_buy, macd_buy, bollinger_buy]
		true_conditions = sum(conditions)
		return true_conditions >= 3
	
	def condition_sell(self):
		death_cross=self.short_sma[0]<self.long_sma[0]
		rsi_sell=self.rsi[0]>65
		macd_sell=self.macd.macd[0] < 0 and self.macd.signal[0] < 0 and self.macd.macd[0] < self.macd.signal[0]
		bollinger_sell=self.dataclose[0] > self.bollinger.lines.top
		conditions = [death_cross, rsi_sell, macd_sell, bollinger_sell]
		true_conditions = sum(conditions)
		return true_conditions >= 3

	def next(self):
		if not self.position and self.condition_buy():
			vol=self.volume_to_buy()
			if vol>0: 
				self.log('ORDEN DE COMPRA CREADA, %.2f - Cantidad: %i' % (self.dataclose[0], vol))
				self.buy(size=vol)

		elif self.position and self.condition_sell():
			self.log(f"ORDEN DE VENTA CREADA, {self.dataclose[0]}")
			self.sell(size=self.position.size)

	def notify_order(self, order):
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log('COMPRA EJECUTADA, %.2f, COMM: %.2f, SIZE: %i' % 
			 			(order.executed.price, 
						order.executed.comm, 
						order.executed.size))
			elif order.issell():
				self.log('VENTA EJECUTADA, %.2f, COMM: %.2f, SIZE: %i' % 
			 			(order.executed.price, 
						order.executed.comm, 
						order.executed.size))
		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			self.log("ORDEN CANCELADA/MARGINADA/RECHAZADA")