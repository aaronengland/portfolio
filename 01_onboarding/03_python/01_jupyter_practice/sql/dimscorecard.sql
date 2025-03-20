select
	IntAccountKey,
	dtmStampCreation,
	strScoreCardVersion,
	fltDebtorScore
from edw.pfsedw.dbo.DimScoreCard
where dtmStampCreation >= '2024-01-01'
	and strScoreCardVersion in ('genxi_v2_3')
	or strScoreCardVersion in ('genxii_v2')
order by dtmStampCreation desc