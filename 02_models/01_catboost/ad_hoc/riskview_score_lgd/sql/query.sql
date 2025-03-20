with tblMin as
(
select
	bigDebtorId,
	min(bigLNRiskViewScoreId) as bigLNRiskViewScoreId
from tblLNRiskViewScore
group by bigDebtorId
)
 
select
	tblLNRiskViewScore.bigAccountId,
	tblMin.bigDebtorId,
	tblLNRiskViewScore.dtmStampCreation,
	tblLNRiskViewScore.intScore
from tblMin
left outer join tblLNRiskViewScore on tblLNRiskViewScore.bigLNRiskViewScoreId=tblMin.bigLNRiskViewScoreId