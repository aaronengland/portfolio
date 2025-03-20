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

# dict tiers
dict_tiers = {
	'A1': 0.0760,
	'A': 0.1320,
	'B': 0.2650,
	'C': 0.3220,
	'D': 0.3500, 
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
class Pricing:
	# init
	def __init__(self, df, bool_bk, dict_tiers, flt_cnl_scaler, flt_avg_life, flt_equity_intercept, flt_equity_slope, flt_securitization, flt_late_fee_income, flt_state_rate_cap, int_dollars_round_fees, str_vehicle_class, str_dealer_type, str_dealer_state):
		self.df = df
		self.bool_bk = bool_bk
		self.dict_tiers = dict_tiers
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
		# map
		self.df[f'tier'] = self.df[f'ecnl'].apply(
			lambda x: get_tier(
				flt_ecnl=x,
				dict_tiers=self.dict_tiers,
			),
		)
		# get current apr
		self.df['current_apr'] = self.df['tier'].map(self.dict_apr_current)
		# get roe required
		self.df['roe_required'] = self.df['tier'].map(self.dict_roe_required)
		# get discount 
		self.df['raw_discount'] = self.df['tier'].map(self.dict_discount)
		# get op ex
		self.df['operating_expenses'] = self.df['tier'].map(dict_op_ex)
		# get reserve points
		self.df['reserve'] = self.df['tier'].map(dict_reserve_points)
		# return
		return self
	# get equity
	def get_equity(self):
		self.df['equity'] = self.flt_equity_intercept + (self.df[f'ecnl'] * self.flt_equity_slope)
		# return
		return self
	# get profit
	def get_profit(self):
		self.df['profit'] = self.df[f'roe_required'] * self.df[f'equity']
		# return
		return self
	# get discount
	def get_discount(self):
		self.df['discount'] = self.df['raw_discount'] / self.df['amtfinanced__app'] / self.flt_avg_life
		# return
		return self
	# get late fee
	def get_late_fee(self):
		self.df['late_fee'] = self.df['ecnl'] * self.flt_late_fee_income
		# return
		return self
	# get funding cost
	def get_funding_cost(self):
		self.df['funding_cost'] = self.flt_securitization * (1 - self.df['equity'])
		# return
		return self
	# get adjusted ecnl
	def get_adjusted_ecnl(self):
		self.df['adjusted_ecnl'] = self.df['ecnl'] * self.flt_cnl_scaler
		# return
		return self
	# get expected losses
	def get_expected_losses(self):
		self.df['expected_losses'] = self.df['adjusted_ecnl'] / self.flt_avg_life
		# return
		return self
	# get buy rate
	def get_buy_rate(self):
		self.df['buy_rate'] = self.df['profit'] - self.df['discount'] - self.df['late_fee'] + self.df['operating_expenses'] + self.df['expected_losses'] + self.df['funding_cost']
		# return
		return self
	# get raw apr
	def get_raw_apr(self):
		self.df['raw_apr'] = self.df['buy_rate'] - self.df['reserve']
		# return
		return self
	# get raw discount adjustment
	def get_raw_discount_adjustment(self):
		self.df['raw_discount_adjustment'] = self.df.apply(
			lambda x: get_raw_discount_adjustment(
				flt_raw_apr=x['raw_apr'], 
				flt_current_apr=x['current_apr'], 
				flt_amt_financed=x['amtfinanced__app'], 
				flt_avg_life=self.flt_avg_life,
			),
			axis=1,
		)
		# return
		return self
	# get raw apr adjustment
	def get_raw_apr_adjustment(self):
		self.df['raw_apr_adjustment'] = self.df.apply(
			lambda x: get_raw_apr_adjustment(
				flt_raw_discount_adjustment=x['raw_discount_adjustment'], 
				flt_current_apr=x['current_apr'], 
				flt_raw_apr=x['raw_apr'],
			),
			axis=1,
		)
		# return
		return self
	# get rate cap  handicap
	def get_rate_cap_handicap(self):
		self.df['rate_cap_handicap'] = self.df.apply(
			lambda x: get_rate_cap_handicap(
				flt_raw_apr=x['raw_apr'], 
				flt_raw_apr_adjustment=x['raw_apr_adjustment'], 
				flt_state_rate_cap=self.flt_state_rate_cap,
			),
			axis=1,
		)
		# return
		return self
	# get additional discount needed
	def get_additional_discount_needed(self):
		self.df['additional_discount_needed'] = self.df['rate_cap_handicap'] * self.df['amtfinanced__app'] * self.flt_avg_life
		# return
		return self
	# get apr
	def get_apr(self):
		self.df['apr'] = self.df['raw_apr'] + self.df['raw_apr_adjustment'] - self.df['rate_cap_handicap']
		# logic for Class 1 vehicles
		print(f'Vehicle Class: {self.str_vehicle_class}')
		if self.str_vehicle_class == 'Class 1':
			self.df['apr'] = self.df['apr'] - 0.01 # subtracting 1% off Class 1 vehicles
		else:
			pass
		# return
		return self
	# get net discount
	def get_net_discount(self):
		self.df['net_discount'] = self.df['raw_discount'] + self.df['additional_discount_needed'] + self.df['raw_discount_adjustment']
		# round to nearest X dollars
		self.df['net_discount'] = (self.df['net_discount'] / self.int_dollars_round_fees).round() * self.int_dollars_round_fees
		# return
		return self

