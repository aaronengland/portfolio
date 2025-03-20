with tbl1 as
(
select *,
Row_number() OVER(partition BY intAccountKey, strScoreCardVersion ORDER BY DimScoreCard.dtmStampCreation desc) RowNum
from riskdb.dbo.vwReportOpenBKApplications left outer join edw.pfsedw.dbo.DimScoreCard
on vwReportOpenBKApplications.bigaccountid = DimScoreCard.intAccountKey
where dtmStampCreation >= '2024-03-14'
and strScoreCardVersion like 'genxii_v2'
)
select*
from tbl1
where RowNum = 1