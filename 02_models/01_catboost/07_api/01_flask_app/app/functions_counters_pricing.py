import pandas as pd
from tqdm import tqdm

##################
##### STATES #####
##################
list_str_state_ignore = [
	'Missouri',
	'Georgia',
	'California',
	'Florida',
	'Texas',
]

##################
###### RATE ######
##################
# dict apr current - BK Franchise
dict_apr_current_bk_franchise = {
    'A1': 0.1195,
    'A': 0.1540,
    'B': 0.1780,
    'C': 0.2385,
    'D': 0.2480,
}
# dict apr current - NonBK Franchise AND BK Independent
dict_apr_current_nonbk_franchise = {
    'A1': 0.1220,
    'A': 0.1540,
    'B': 0.1815,
    'C': 0.2455,
    'D': 0.2525,
}
# dict apr current - NonBK Independent
dict_apr_current_nonbk_independent = {
    'A1': 0.1240,
    'A': 0.1580,
    'B': 0.1870,
    'C': 0.2555,
    'D': 0.2635,
}
# deprecated
dict_apr_current_original = {
    'A1': 0.1500,
    'A': 0.1700,
    'B': 0.1970,
    'C': 0.2590,
    'D': 0.2615,
}

##########################
###### ROE REQUIRED ######
##########################
# dict apr current - BK Franchise
dict_roe_required_bk_franchise = {
    'A1': 0.1500,
    'A': 0.1600,
    'B': 0.1700,
    'C': 0.1750,
    'D': 0.1800,
}
# dict apr current - NonBK Franchise AND BK Independent
dict_roe_required_nonbk_franchise = {
    'A1': 0.2027,
    'A': 0.2027,
    'B': 0.2027,
    'C': 0.2027,
    'D': 0.2027,
}
# dict apr current - NonBK Independent
dict_roe_required_nonbk_independent = {
    'A1': 0.2525,
    'A': 0.2525,
    'B': 0.2525,
    'C': 0.2525,
    'D': 0.2525,
}
# deprecated
dict_roe_required_original = {
    'A1': 0.2750,
    'A': 0.2750,
    'B': 0.2750,
    'C': 0.2750,
    'D': 0.2750,
}

###############################################
###### DISCOUNT (i.e., ACQUISITIOIN FEE) ######
###############################################
# dict apr current - BK Franchise
dict_discount_bk_franchise = {
    'A1': 0,
    'A': 125,
    'B': 250,
    'C': 1150,
    'D': 1400,
}
# dict apr current - NonBK Franchise AND BK Independent
dict_discount_nonbk_franchise = {
    'A1': 140,
    'A': 260,
    'B': 320,
    'C': 1350,
    'D': 1600,
}
# dict apr current - NonBK Independent
dict_discount_nonbk_independent = {
    'A1': 200,
    'A': 360,
    'B': 450,
    'C': 1550,
    'D': 1900,
}

# deprecated
dict_discount_original_nobk = {
    'A1': 252,
    'A': 467,
    'B': 566,
    'C': 1767,
    'D': 2057,
}

# dict discount
dict_discount_original_bk = {
    'A1': 0,
    'A': 190,
    'B': 360,
    'C': 1587,
    'D': 1875,
}

###################
###### OP EX ######
###################
# dict op ex
dict_op_ex = {
    'A1': 0.0564,
    'A': 0.0603,
    'B': 0.0639,
    'C': 0.0639,
    'D': 0.0639,
}

############################
###### RESERVE POINTS ######
############################
# reserve points
dict_reserve_points = {
    'A1': 0,
    'A': 0,
    'B': 0,
    'C': 0,
    'D': 0,
}

# helper function to map ecnl to tier
def get_tier(flt_ecnl, dict_tiers):
    if flt_ecnl <= dict_tiers['A1']:
        return 'A1'
    elif flt_ecnl <= dict_tiers['A']:
        return 'A'
    elif flt_ecnl <= dict_tiers['B']:
        return 'B'
    elif flt_ecnl <= dict_tiers['C']:
        return 'C'
    elif flt_ecnl <= dict_tiers['D']:
        return 'D'
    else:
        return 'Decline'

# helper function to get raw discount adjustment
def get_raw_discount_adjustment(flt_raw_apr, flt_current_apr, flt_amt_financed, flt_avg_life):
    # get difference in raw apr and current apr
    flt_diff = flt_raw_apr - flt_current_apr
    # logic
    if flt_diff < 0:
        return flt_diff * flt_amt_financed * flt_avg_life
    else:
        return 0

# helper function to get the raw apr adjustment
def get_raw_apr_adjustment(flt_raw_discount_adjustment, flt_current_apr, flt_raw_apr):
    # logic
    if flt_raw_discount_adjustment != 0:
        # get diff
        flt_diff = flt_current_apr - flt_raw_apr
        return flt_diff
    else:
        return 0

# helper function to get rate cap handicap
def get_rate_cap_handicap(flt_raw_apr, flt_raw_apr_adjustment, flt_state_rate_cap):
    # get the sum
    flt_sum = flt_raw_apr + flt_raw_apr_adjustment - flt_state_rate_cap
    # logic
    if flt_sum <= 0:
        return 0
    else:
        return flt_sum

# class
class PricingCounters:
	# init
	def __init__(self, df, bool_bk, str_tiers, flt_cnl_scaler, flt_avg_life, flt_equity_intercept, flt_equity_slope, flt_securitization, flt_late_fee_income, flt_state_rate_cap, int_dollars_round_fees, str_vehicle_class, str_dealer_type, str_dealer_state):
		self.df = df
		self.bool_bk = bool_bk
		self.str_tiers = str_tiers
		self.flt_cnl_scaler = flt_cnl_scaler
		self.flt_avg_life = flt_avg_life
		self.flt_equity_intercept = flt_equity_intercept
		self.flt_equity_slope = flt_equity_slope
		self.flt_securitization = flt_securitization
		self.flt_late_fee_income = flt_late_fee_income
		self.flt_state_rate_cap = flt_state_rate_cap
		self.int_dollars_round_fees = int_dollars_round_fees
		self.str_vehicle_class = str_vehicle_class
		self.str_dealer_type = str_dealer_type
		self.list_str_ecnl_type = ['amt', 'down']
		self.str_dealer_state = str_dealer_state
	# logic
	def pricing_test_logic(self):
		# logic for mapping
		if (self.str_dealer_state in list_str_state_ignore) and (self.bool_bk == True): 
			self.str_applicant_label = 'no pricing logic conditions apply (BK)'
			self.dict_apr_current = dict_apr_current_original # rate
			self.dict_roe_required = dict_roe_required_original # roe required
			self.dict_discount = dict_discount_original_bk # discount
			#self.flt_equity_intercept = 0.0807 # original
			self.flt_equity_intercept = 0.08035 # origin
			self.flt_equity_slope = 0.59 # original
			self.flt_securitization = 0.064 # original
		elif (self.str_dealer_state in list_str_state_ignore) and (self.bool_bk == False): 
			self.str_applicant_label = 'no pricing logic conditions apply (No BK)'
			self.dict_apr_current = dict_apr_current_original # rate
			self.dict_roe_required = dict_roe_required_original # roe required
			self.dict_discount = dict_discount_original_nobk # discount
			#self.flt_equity_intercept = 0.0807 # original
			self.flt_equity_intercept = 0.08035 # original
			self.flt_equity_slope = 0.59 # original
			self.flt_securitization = 0.064 # original
		elif (self.bool_bk == True) and (self.str_dealer_type in ['Franchise', 'Referral']): # BK-Franchise
			self.str_applicant_label = 'BK-Franchise'
			self.dict_apr_current = dict_apr_current_bk_franchise # rate
			self.dict_roe_required = dict_roe_required_bk_franchise # roe required
			self.dict_discount = dict_discount_bk_franchise # discount
		elif (self.bool_bk == False) and (self.str_dealer_type in ['Franchise', 'Referral']): # nonBK-Franchise
			self.str_applicant_label = 'nonBK-Franchise'
			self.dict_apr_current = dict_apr_current_nonbk_franchise # rate
			self.dict_roe_required = dict_roe_required_nonbk_franchise # roe required
			self.dict_discount = dict_discount_nonbk_franchise # discount
		elif (self.bool_bk == True) and (self.str_dealer_type == 'Independent'): # BK-Independent
			self.str_applicant_label = 'BK-Independent'
			self.dict_apr_current = dict_apr_current_nonbk_franchise # rate
			self.dict_roe_required = dict_roe_required_nonbk_franchise # roe required
			self.dict_discount = dict_discount_nonbk_franchise # discount
		elif (self.bool_bk == False) and (self.str_dealer_type == 'Independent'): # nonBK-Indpendent
			self.str_applicant_label = 'nonBK-Independent'
			self.dict_apr_current = dict_apr_current_nonbk_independent # rate
			self.dict_roe_required = dict_roe_required_nonbk_independent # roe required
			self.dict_discount = dict_discount_nonbk_independent # discount
		else:
			pass
		print(f'Applicant Label: {self.str_applicant_label}')
		print(f'Equity Intercept: {self.flt_equity_intercept}')
		print(f'Equity Slope: {self.flt_equity_slope}')
		print(f'Securitization: {self.flt_securitization}')
		# return
		return self
	# map to tier
	def map_to_tier(self):
		# convert str_tiers to dict
		dict_tiers = eval(self.str_tiers)
		# map
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'tier_{str_ecnl_type}'] = self.df[f'ecnl_{str_ecnl_type}'].apply(
				lambda x: get_tier(
					flt_ecnl=x,
					dict_tiers=dict_tiers,
				),
			)
			# get current apr
			self.df[f'current_apr_{str_ecnl_type}'] = self.df[f'tier_{str_ecnl_type}'].map(self.dict_apr_current)
			# get roe required
			self.df[f'roe_required_{str_ecnl_type}'] = self.df[f'tier_{str_ecnl_type}'].map(self.dict_roe_required)
			# get discount 
			self.df[f'raw_discount_{str_ecnl_type}'] = self.df[f'tier_{str_ecnl_type}'].map(self.dict_discount)
			# get op ex
			self.df[f'operating_expenses_{str_ecnl_type}'] = self.df[f'tier_{str_ecnl_type}'].map(dict_op_ex)
			# get reserve points
			self.df[f'reserve_{str_ecnl_type}'] = self.df[f'tier_{str_ecnl_type}'].map(dict_reserve_points)
		# return
		return self
	# get equity
	def get_equity(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'equity_{str_ecnl_type}'] = self.flt_equity_intercept + (self.df[f'ecnl_{str_ecnl_type}'] * self.flt_equity_slope)
		# return
		return self
	# get profit
	def get_profit(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'profit_{str_ecnl_type}'] = self.df[f'roe_required_{str_ecnl_type}'] * self.df[f'equity_{str_ecnl_type}']
		# return
		return self
	# get discount
	def get_discount(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'discount_{str_ecnl_type}'] = self.df[f'raw_discount_{str_ecnl_type}'] / self.df['Amount Financed'] / self.flt_avg_life
		# return
		return self
	# get late fee
	def get_late_fee(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'late_fee_{str_ecnl_type}'] = self.df[f'ecnl_{str_ecnl_type}'] * self.flt_late_fee_income
		# return
		return self
	# get funding cost
	def get_funding_cost(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'funding_cost_{str_ecnl_type}'] = self.flt_securitization * (1 - self.df[f'equity_{str_ecnl_type}'])
		# return
		return self
	# get adjusted ecnl
	def get_adjusted_ecnl(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'adjusted_ecnl_{str_ecnl_type}'] = self.df[f'ecnl_{str_ecnl_type}'] * self.flt_cnl_scaler
		# return
		return self
	# get expected losses
	def get_expected_losses(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'expected_losses_{str_ecnl_type}'] = self.df[f'adjusted_ecnl_{str_ecnl_type}'] / self.flt_avg_life
		# return
		return self
	# get buy rate
	def get_buy_rate(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'buy_rate_{str_ecnl_type}'] = self.df[f'profit_{str_ecnl_type}'] - self.df[f'discount_{str_ecnl_type}'] - self.df[f'late_fee_{str_ecnl_type}'] + self.df[f'operating_expenses_{str_ecnl_type}'] + self.df[f'expected_losses_{str_ecnl_type}'] + self.df[f'funding_cost_{str_ecnl_type}']
		# return
		return self
	# get raw apr
	def get_raw_apr(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'raw_apr_{str_ecnl_type}'] = self.df[f'buy_rate_{str_ecnl_type}'] - self.df[f'reserve_{str_ecnl_type}']
		# return
		return self
	# get raw discount adjustment
	def get_raw_discount_adjustment(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'raw_discount_adjustment_{str_ecnl_type}'] = self.df.apply(
				lambda x: get_raw_discount_adjustment(
					flt_raw_apr=x[f'raw_apr_{str_ecnl_type}'], 
					flt_current_apr=x[f'current_apr_{str_ecnl_type}'], 
					flt_amt_financed=x['Amount Financed'], 
					flt_avg_life=self.flt_avg_life,
				),
				axis=1,
			)
		# return
		return self
	# get raw apr adjustment
	def get_raw_apr_adjustment(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'raw_apr_adjustment_{str_ecnl_type}'] = self.df.apply(
				lambda x: get_raw_apr_adjustment(
					flt_raw_discount_adjustment=x[f'raw_discount_adjustment_{str_ecnl_type}'], 
					flt_current_apr=x[f'current_apr_{str_ecnl_type}'], 
					flt_raw_apr=x[f'raw_apr_{str_ecnl_type}'],
				),
				axis=1,
			)
		# return
		return self
	# get rate cap  handicap
	def get_rate_cap_handicap(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'rate_cap_handicap_{str_ecnl_type}'] = self.df.apply(
				lambda x: get_rate_cap_handicap(
					flt_raw_apr=x[f'raw_apr_{str_ecnl_type}'], 
					flt_raw_apr_adjustment=x[f'raw_apr_adjustment_{str_ecnl_type}'], 
					flt_state_rate_cap=self.flt_state_rate_cap,
				),
				axis=1,
			)
		# return
		return self
	# get additional discount needed
	def get_additional_discount_needed(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'additional_discount_needed_{str_ecnl_type}'] = self.df[f'rate_cap_handicap_{str_ecnl_type}'] * self.df['Amount Financed'] * self.flt_avg_life
		# return
		return self
	# get apr
	def get_apr(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'apr_{str_ecnl_type}'] = self.df[f'raw_apr_{str_ecnl_type}'] + self.df[f'raw_apr_adjustment_{str_ecnl_type}'] - self.df[f'rate_cap_handicap_{str_ecnl_type}']
			# logic for Class 1 vehicles
			print(f'Vehicle Class: {self.str_vehicle_class}')
			if self.str_vehicle_class == 'Class 1':
				self.df[f'apr_{str_ecnl_type}'] = self.df[f'apr_{str_ecnl_type}'] - 0.01 # subtracting 1% off Class 1 vehicles
			else:
				pass
		# return
		return self
	# get net discount
	def get_net_discount(self):
		for str_ecnl_type in tqdm(self.list_str_ecnl_type):
			self.df[f'net_discount_{str_ecnl_type}'] = self.df[f'raw_discount_{str_ecnl_type}'] + self.df[f'additional_discount_needed_{str_ecnl_type}'] + self.df[f'raw_discount_adjustment_{str_ecnl_type}']
			# round to nearest X dollars
			self.df[f'net_discount_{str_ecnl_type}'] = (self.df[f'net_discount_{str_ecnl_type}'] / self.int_dollars_round_fees).round() * self.int_dollars_round_fees
		# return
		return self
	# get down and sales price all
	def get_down_and_sales_price_all(self):
		# logic
		if self.str_ecnl == 'ECNL (Down)': # if pivoting on down
			str_down_cash = 'Down Cash' # use the down cash that changes
			str_down_total = 'Down Total' # use the down total that changes
			str_sales_price = 'Sales Price Original'
		# if pivoting on amt financed
		else:
			str_down_cash = 'Down Cash Original' # use the original down cash
			str_down_total = 'Down Total Original' # use the original down total
			str_sales_price = 'Sales Price'

		# create down cash all column
		self.df['down_cash_all'] = self.df.apply(
			lambda x: x['Down Cash Original'] if x['Offer'] < 0 else x[str_down_cash],
			axis=1,
		)

		# create down total all column
		self.df['down_total_all'] = self.df.apply(
			lambda x: x['Down Total Original'] if x['Offer'] < 0 else x[str_down_total],
			axis=1,
		)

		# create sales price all column
		self.df['sales_price_all'] = self.df.apply(
			lambda x: x['Sales Price'] if x['Offer'] < 0 else x[str_sales_price],
			axis=1,
		)

		# save to object
		self.str_down_cash = str_down_cash
		self.str_down_total = str_down_total
		self.str_sales_price = str_sales_price
		# return
		return self

