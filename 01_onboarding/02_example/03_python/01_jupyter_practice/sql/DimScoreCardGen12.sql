SELECT intAccountKey, fltDebtorScore, dtmStampCreation, strScoreCardVersion
FROM edw.pfsedw.dbo.DimScoreCard
WHERE strScoreCardVersion IN ('genxii','genxii_v2', 'genxii_v3')