SELECT
	bigAccountId,
	dtmFunded,
	mnyNetGainLoss as fltNetChgOff,
	dtmRunDate as MonthEndDate
FROM riskdb.accountingReports.tblAccounting_ReportV11_ME