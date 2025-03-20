SELECT tsp.bigAccountId,
tacc.dtmStampCreation,
tsp.intOpenBKType,
tsp.AmtFinanced,
tsp.BookValue,
tloss.fltNetChgOff
FROM electra.riskdb.analytics.tbltempstaticpool as tsp LEFT OUTER JOIN
electra.pfsdb.dbo.tblAccount as tacc ON tsp.bigAccountId=tacc.bigAccountId LEFT OUTER JOIN
 
 
	(SELECT * 
	 FROM electra.riskdb.accountingReports.tblAccounting_LoanCOandNA_ME 
	 WHERE MonthEndDate = '2024-02-29') as tloss
 
ON tsp.bigAccountId=tloss.bigAccountId