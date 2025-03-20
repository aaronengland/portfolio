SELECT DebtorState AS [State], COUNT(Debtorstate) AS [Amount]
FROM electra.riskdb.analytics.tbltempstaticpool
WHERE dtmFunded >= '2024-01-01' AND DebtorState IS NOT NULL
GROUP BY DebtorState

