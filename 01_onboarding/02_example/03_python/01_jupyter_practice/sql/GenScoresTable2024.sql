SELECT tmp.bigAccountId, tmp.bigDealerId, acc.dtmStampCreation, tmp.dtmFunded, tmp.intTerm, tmp.intOpenBKType, tmp.strTier, tmp.AmtFinanced, tmp.OriginalInterestRate, tmp.MaxFico,

MAX(CASE WHEN dim.strScoreCardVersion = 'genxi' OR
			dim.strScoreCardVersion = 'genxi_v1_1' OR
			dim.strScoreCardVersion = 'genxi_v2' OR
			dim.strScoreCardVersion = 'genxi_v2_1' OR
			dim.strScoreCardVersion = 'genxi_v2_2' OR
			dim.strScoreCardVersion = 'genxi_v2_3' 
			THEN dim.fltDebtorScore END) AS 'Gen 11',

MAX(CASE WHEN dim.strScoreCardVersion LIKE 'genxii' OR
			dim.strScoreCardVersion = 'genxii_v2'
			THEN dim.fltDebtorScore END) AS 'Gen 12',

(CASE WHEN acc.dtmStampcreation >= '2024-04-15' AND (tmp.bigAccountId LIKE '%5' OR tmp.bigAccountId LIKE '%0') THEN 'Gen12' ELSE 'Gen11' END) AS 'Gen'

FROM electra.riskdb.analytics.tbltempstaticpool tmp LEFT JOIN electra.pfsdb.dbo.tblaccount acc
ON tmp.bigAccountId = acc.bigAccountId LEFT JOIN 
	(SELECT dim1.intAccountKey, dim1.fltdebtorscore, dim1.strscorecardversion,dim1.dtmstampcreation, Row_number()
              OVER(
                partition BY intAccountKey
                ORDER BY dtmStampCreation desc) as rn FROM edw.pfsedw.dbo.DimScoreCard dim1) dim 
ON tmp.bigAccountId = dim.intAccountkey AND dim.rn = 1 
WHERE tmp.dtmFunded >= '2024-01-01'
GROUP BY tmp.bigAccountId, tmp.bigDealerId, acc.dtmStampCreation, tmp.dtmFunded, tmp.intTerm, tmp.intOpenBKType, tmp.strTier, tmp.AmtFinanced, tmp.OriginalInterestRate, tmp.MaxFico
