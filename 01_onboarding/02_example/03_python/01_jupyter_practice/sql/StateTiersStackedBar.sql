SELECT COUNT(tmp.strTier) AS [NumberOfTiers], debtorstate AS [State], strTier AS [Tier]
FROM electra.riskdb.analytics.tbltempstaticpool tmp LEFT JOIN electra.pfsdb.dbo.tblaccount acc
ON tmp.bigAccountId = acc.bigAccountId
WHERE strtier IS NOT NULL AND tmp.dtmFunded >= '2024-01-01'
GROUP BY debtorstate, strTier
