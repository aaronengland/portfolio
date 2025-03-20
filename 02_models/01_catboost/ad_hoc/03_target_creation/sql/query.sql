SELECT 
	sp.bigAccountId,
	sp.FundingMonth,
	DATEADD(MONTH, 24, sp.FundingMonth) AS FundingMonthPlus24,
	sp.MonthOnBooks,
	sp.AccountChargeOff,
	sp.monthOfDefault,
	sp.NetChargeOff,
	sp.RunningNetLoss,
	DATEADD(DAY, 60, c.dtmDue) AS FirstDate60plus,
	CASE 
		WHEN RunningNetLoss > 0 AND DATEADD(DAY, 60, c.dtmDue) < DATEADD(MONTH, 24, sp.FundingMonth)
		THEN 1
		ELSE 0
	END AS bitTarget24Months
FROM 
	electra.riskdb.dbo.tblReportCOStaticPools_StaticPool sp LEFT OUTER JOIN
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
	)c
	ON sp.bigAccountId = c.bigAccountId
WHERE MonthOnBooks = 24