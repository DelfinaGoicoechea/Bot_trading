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
		self.short_sma=bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period_short_sma)
		self.long_sma=bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.period_long_sma)
		self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)
		self.macd = bt.indicators.MACD(
			self.dataclose,
			period_me1=self.params.macd_short,
			period_me2=self.params.macd_long,
            period_signal=self.params.macd_signal
		)
		self.bollinger = bt.indicators.BollingerBands(
            self.data.close,
            period=self.params.bollinger_period,
            devfactor=self.params.bollinger_dev
        )
		
	def log(self, txt, dt=None):
		dt = dt or self.datas[0].datetime.date(0)
		print('%s, %s' % (dt.isoformat(), txt))

	def vol_buy(self) -> int:
		if self.broker.cash >= self.dataclose[0]:
			cash = self.broker.get_cash()*self.params.capital_fraction
			cash = cash-cash*self.params.commision
			return int(cash/self.dataclose[0])
		return 0 
	
	def condition_buy(self):
		golden_cross=self.short_sma[0]>self.long_sma[0]
		rsi_compra=self.rsi[0]<35
		macd_compra=self.macd.macd[0] > 0 and self.macd.signal[0] > 0 and self.macd.macd[0] > self.macd.signal[0]
		bollinger_compra=self.dataclose[0] < self.bollinger.lines.bot
		condiciones = [golden_cross, rsi_compra, macd_compra, bollinger_compra]
		condiciones_verdaderas = sum(condiciones)
		#if (condiciones_verdaderas>=3):
		#	print(golden_cross)
		#	print(rsi_compra)
		#	print(macd_compra)
		#	print(bollinger_compra)
		return condiciones_verdaderas >= 3
	
	def condition_shell(self):
		death_cross=self.short_sma[0]<self.long_sma[0]
		rsi_venta=self.rsi[0]>65
		macd_venta=self.macd.macd[0] < 0 and self.macd.signal[0] < 0 and self.macd.macd[0] < self.macd.signal[0]
		bollinger_venta=self.dataclose[0] > self.bollinger.lines.top
		condiciones = [death_cross, rsi_venta, macd_venta, bollinger_venta]
		condiciones_verdaderas = sum(condiciones)
		if (condiciones_verdaderas>=3):
			print(death_cross)
			print(rsi_venta)
			print(macd_venta)
			print(bollinger_venta)
		return condiciones_verdaderas >= 3

	def next(self):
		if not self.position and self.condition_buy():
			vol=self.vol_buy()
			if vol>0: 
				self.log('ORDEN DE COMPRA CREADA, %.2f - Cantidad: %i' % (self.dataclose[0], vol))
				self.buy(size=vol)
		elif self.position and self.condition_shell():
			self.log(f"ORDEN DE VENTA CREADA, {self.dataclose[0]}")
			self.sell(size=self.position.size)

	def notify_order(self, order):
		if order.status in [order.Completed]:
			if order.isbuy():
				self.log('COMPRA EJECUTADA, %.2f, COMM: %.2f, SIZE: %i' % (order.executed.price, order.executed.comm, order.executed.size))
			elif order.issell():
				self.log('VENTA EJECUTADA, %.2f, COMM: %.2f, SIZE: %i' % (order.executed.price, order.executed.comm, order.executed.size))
		elif order.status in [order.Canceled]:
			self.log("ORDEN CANCELADA")
			
		elif order.status in [order.Margin]:
			self.log("ORDEN MARGINADA")
		
		elif order.status in [order.Rejected]:
			self.log("ORDEN RECHAZADA")