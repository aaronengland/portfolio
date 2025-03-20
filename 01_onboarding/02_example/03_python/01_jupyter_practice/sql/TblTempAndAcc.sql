SELECT tmp.bigAccountId, tmp.bigDealerId, acc.dtmStampCreation, tmp.dtmFunded, tmp.intTerm, tmp.intOpenBKType, tmp.strTier, tmp.AmtFinanced, tmp.OriginalInterestRate, tmp.MaxFico 
FROM electra.riskdb.analytics.tbltempstaticpool tmp LEFT OUTER JOIN electra.pfsdb.dbo.tblaccount acc
ON tmp.bigAccountId = acc.bigAccountId
WHERE tmp.dtmFunded >= '2024-01-01'