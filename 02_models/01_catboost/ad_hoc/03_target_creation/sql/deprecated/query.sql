CREATE TABLE #t
(
	RunDate DATE NULL,
	AccountNumber INT NULL,
	LossType VARCHAR(50) NULL,
	LoanStatus VARCHAR(5) NULL,
	NetChargeOff MONEY NULL
)
CREATE NONCLUSTERED INDEX ix_t ON #t(AccountNumber)
 
 
DECLARE db_cursor CURSOR FOR SELECT dtmDaily FROM riskdb.dbo.tblDMR_datesTable WHERE dtmDaily >= '2015-01-31' AND dtmDaily < GETDATE() AND intMonthEndDate = 1
DECLARE @dtmDate DATETIME
 
OPEN db_cursor
FETCH NEXT FROM db_cursor INTO @dtmDate
WHILE @@FETCH_STATUS = 0
BEGIN
 
INSERT #t
SELECT
	RunDate,
	bigAccountId AS AccountNumber,
	CASE WHEN bitDefault_NonBK = 1 THEN 'Non BK Loss' ELSE 'BK Loss' END AS LossType,
	strLoanStatus AS LoanStatus,
	COALESCE(mnyEst_Defaults, mnyEstDefaults_Bankruptcies) AS NetChargeOff
FROM
	riskdb.dbo.tblDMR_History d 
WHERE
	RunDate = @dtmDate   
	AND (bitDefault_NonBK = 1 OR bitDefault_BK = 1)
	AND RunDate >= '2017-06-30'

 
UNION ALL
 
SELECT
	RunDate,
	bigAccountId AS AccountNumber,
	CASE WHEN bitDefault_NonBK = 1 THEN 'Non BK Loss' ELSE 'BK Loss' END AS LossType,
	LoanStatus AS LoanStatus,
	fltEst_Defaults AS NetChargeOff
FROM
	riskdb.dbo.tblDailyManagementRpt_History d 
WHERE
	RunDate = @dtmDate    
	AND (bitDefault_NonBK = 1 OR bitDefault_BK = 1)
	AND bitDefault_NonBK = 1
	AND RunDate < '2017-06-30'
	AND RunDate >= '2015-01-01'
 
	
FETCH NEXT FROM db_cursor INTO @dtmDate
 
END
CLOSE db_cursor
DEALLOCATE db_cursor
 
 
SELECT 
	t.*,
	am.dtmNonAccrual AS NonAccrualDate,
	am.dtmStampCreation AS BookingDate,
	DATEDIFF(MONTH, am.dtmStampCreation, t.RunDate) AS MonthsOnBook,
	DATEDIFF(MONTH, am.dtmNonAccrual, t.RunDate) AS AgeOfDefault_fromRunDate,
	DATEDIFF(MONTH, am.dtmStampCreation, am.dtmNonAccrual) AS AgeOfDefault_fromBookingDate,
	DATEADD(DAY, 60, min_c.dtmDue) AS FirstDate60plus
FROM 
	#t t INNER JOIN electra.pfsdb.dbo.tblAccountMaintenance am
	ON t.AccountNumber = am.bigAccountId LEFT OUTER JOIN 
	(
		SELECT
			att.bigAccountId,
			MIN(c.dtmDue) AS dtmDue
		FROM 
			electra.pfsdb.dbo.tblAccountTerms att INNER JOIN electra.pfsdb.dbo.tblCharges c
			ON att.bigAccountTermId = c.bigAccountTermId
		WHERE
			att.bigAccountTermTypeId = 1
			AND c.bigChargeTypeId = 1
			AND c.bitExtended = 0
			AND c.bitInvalid = 0
			AND DATEDIFF(DAY, c.dtmDue, COALESCE(c.dtmClosed, GETDATE())) > 60
			AND c.dtmDue < GETDATE()
		GROUP BY 
			att.bigAccountId
	)min_c
	ON t.AccountNumber = min_c.bigAccountId
 
DROP TABLE #t