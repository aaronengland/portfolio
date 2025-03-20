SELECT strtier AS [Tiers], COUNT(strTier) AS [Amount]
FROM electra.riskdb.analytics.tbltempstaticpool
WHERE dtmFunded >= '2021-01-01' AND dtmFunded <= '2021-12-31' AND strtier NOT IN ('Gold','Platinum')
GROUP BY strtier
