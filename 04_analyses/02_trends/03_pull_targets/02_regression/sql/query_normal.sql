SELECT
	bigAccountId,
	dtmBooking as dtmFunded,
	fltNetChgOff,
	MonthEndDate
FROM riskdb.accountingReports.tblAccounting_LoanCOandNA_ME