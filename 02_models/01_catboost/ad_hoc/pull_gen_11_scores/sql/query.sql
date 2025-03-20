with tbl1 as
(
	select
		intAccountKey as bigAccountId,
		fltDebtor_Score_pd,
		fltDebtor_Score_lgd,
		fltDebtorScore,
		strScoreCardVersion, 
		dtmStampCreation,
		Row_number() OVER(partition BY intAccountKey, strScoreCardVersion ORDER BY dtmStampCreation desc) RowNum
	from edw.pfsedw.dbo.DimScoreCard
	where strScoreCardVersion in ('genxi_v2_2', 'genxi_v2_3')
	and dtmStampCreation >= '2024-03-01'
)
select*
from tbl1
where RowNum = 1



