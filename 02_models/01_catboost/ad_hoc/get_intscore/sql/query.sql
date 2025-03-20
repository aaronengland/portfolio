with tblMin as
(
select
	intDebtorKey,
	min(intLNRiskViewSKey) as intLNRiskViewSKey
from DimLNRiskView
group by intDebtorKey
)
 
select
	DimLNRiskView.intAccountKey as bigAccountId,
	tblMin.intDebtorKey as bigDebtorId,
	DimLNRiskView.dtmStampCreation,
	DimLNRiskView.intScore
from tblMin
left outer join DimLNRiskView on DimLNRiskView.intLNRiskViewSKey=tblMin.intLNRiskViewSKey