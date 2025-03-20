SELECT
	ttsp.bigAccountId,
	ttsp.strTier
FROM riskdb.analytics.tbltempstaticpool AS ttsp
WHERE ttsp.strTier IS NOT NULL