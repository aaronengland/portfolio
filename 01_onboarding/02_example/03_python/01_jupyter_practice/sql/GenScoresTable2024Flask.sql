WITH gen11tbl AS (
SELECT *, ROW_NUMBER() 
	OVER(PARTITION BY intAccountKey
ORDER BY dtmStampCreation DESC) RN
FROM edw.pfsedw.dbo.DimScoreCard
WHERE strScoreCardVersion IN ('genxi','genxi_v1_1','genxi_v2','genxi_v2_1','genxi_v2_2', 'genxi_v2_3')
),

gen12tbl AS (
SELECT *, ROW_NUMBER()
	OVER(PARTITION BY intAccountKey
ORDER BY dtmStampCreation DESC) RN
FROM edw.pfsedw.dbo.DimScoreCard
WHERE strScoreCardVersion IN ('genxii','genxii_v2', 'genxii_v3')
)

SELECT tmp.bigAccountId, tmp.DebtorState, tmp.bigDealerId, acc.dtmStampCreation, tmp.dtmFunded, tmp.intTerm, tmp.intOpenBKType, tmp.strTier, tmp.AmtFinanced, tmp.OriginalInterestRate, tmp.MaxFico, 
tblgen11.fltDebtorScore AS [Gen 11], 
tblgen12.fltDebtorScore AS [Gen 12],
(CASE WHEN acc.dtmStampcreation >= '2024-04-15' AND (tmp.bigAccountId LIKE '%5' OR tmp.bigAccountId LIKE '%0') THEN 'Gen12' ELSE 'Gen11' END) AS 'Gen'
FROM electra.riskdb.analytics.tbltempstaticpool tmp LEFT JOIN electra.pfsdb.dbo.tblaccount acc
ON tmp.bigAccountId = acc.bigAccountId LEFT OUTER JOIN 
	(SELECT * 
	FROM gen11tbl
	WHERE RN = 1) tblgen11 ON tblgen11.intAccountKey = tmp.bigAccountId LEFT OUTER JOIN
	(SELECT *
	FROM gen12tbl
	WHERE RN = 1) tblgen12 ON tblgen12.intAccountKey = tmp.bigAccountId
WHERE tmp.dtmFunded >= '2024-01-01'