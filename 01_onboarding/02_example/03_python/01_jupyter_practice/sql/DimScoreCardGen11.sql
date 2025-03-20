SELECT intAccountKey, fltDebtorScore, dtmStampCreation, strScoreCardVersion
FROM edw.pfsedw.dbo.DimScoreCard
WHERE strScoreCardVersion IN ('genxi' , 'genxi_v1_1','genxi_v2','genxi_v2_2','genxi_v2_3')