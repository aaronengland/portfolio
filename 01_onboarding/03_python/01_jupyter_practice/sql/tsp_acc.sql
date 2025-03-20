select
		tsp.bigAccountId,
		--case when (tsp.bigAccountId % 5) = 0 and tsp.dtmFunded >= 'INSERT GEN 12 START DATE' then 1 else 0 end as NewGen12Acc,
		tsp.bigDealerId,
		acc.dtmStampCreation,
		tsp.dtmFunded,
		acc.intTerm,
		tsp.intOpenBKType,
		tsp.strTier,
		tsp.AmtFinanced,
		tsp.OriginalInterestRate,
		tsp.MaxFico
from electra.riskdb.analytics.tbltempstaticpool as tsp
	left outer join tblAccount as acc on tsp.bigAccountId = acc.bigAccountId
where tsp.dtmFunded >= '2024-01-01'
order by tsp.dtmFunded desc