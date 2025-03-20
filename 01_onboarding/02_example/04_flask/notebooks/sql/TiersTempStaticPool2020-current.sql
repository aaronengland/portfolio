SELECT strtier AS [Tiers], COUNT(strTier) AS [Amount]
FROM electra.riskdb.analytics.tbltempstaticpool
WHERE dtmFunded >= '2020-01-01' AND strtier NOT IN ('Gold','Platinum')
GROUP BY strtier
