with tbl1 as
(
select
tblAccount.bigAccountId,
tblAccount.dtmStampCreation, 
tblaccount.dtmApproved, 
tblAccount.dtmFunded,
strScoreCardVersion, 
fltDebtorScore,
fltDebtor_Score_lgd,
fltDebtor_Score_pd,
fltDebtor_Score_ad,
Row_number() OVER(partition BY intAccountKey, strScoreCardVersion ORDER BY DimScoreCard.dtmStampCreation desc) RowNum
from tblAccount left outer join edw.pfsedw.dbo.DimScoreCard
on tblAccount.bigaccountid = DimScoreCard.intAccountKey
--where dtmStampCreation >= '2024-01-01'
)
select*
from tbl1
where RowNum = 1
and strScoreCardVersion like 'genxii_v2'
and tbl1.dtmStampCreation >= '2024-03-14'