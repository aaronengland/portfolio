SELECT 
	am.bigAccountId,
	CASE WHEN Early_Pay_Delinquency_STRDPD_STRTOTAL > 0 THEN 1 ELSE 0 END AS Early_Pay_Delinquency_STRDPD_STRTOTAL_Flag
FROM 
	electra.pfsdb.dbo.tblAccountMaintenance am LEFT OUTER JOIN
	(
		SELECT 
			c.bigAccountId,
			SUM(CASE
					WHEN DATEDIFF(DAY, c.dtmDue, c.dtmClosed) > DPDMINUS1 OR (DATEDIFF(DAY, c.dtmDue, GETDATE()) > DPDMINUS1 AND c.dtmClosed IS NULL) 
					THEN 1
					ELSE 0
				END) AS Early_Pay_Delinquency_STRDPD_STRTOTAL
		FROM pfsdb.dbo.tblCharges c LEFT OUTER JOIN pfsdb.dbo.tblAccountTerms att ON c.bigAccountTermId = att.bigAccountTermId
			INNER JOIN pfsdb.dbo.tblAccountMaintenance am ON c.bigAccountId = am.bigAccountId
		WHERE c.bigChargeTypeId = 1 AND c.bitInvalid = 0 AND c.dtmDue < DATEADD(DAY, STRTOTAL, am.dtmContract)
		GROUP BY c.bigAccountId
	)a
	ON am.bigAccountId = a.bigAccountId