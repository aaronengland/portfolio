SELECT strtier AS [Tiers], COUNT(strTier) AS [Amount]
FROM electra.riskdb.analytics.tbltempstaticpool
WHERE dtmFunded >= '2022-01-01' AND dtmFunded <= '2022-12-31' AND strtier NOT IN ('Gold','Platinum')
GROUP BY strtier
