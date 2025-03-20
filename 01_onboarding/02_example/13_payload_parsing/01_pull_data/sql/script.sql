select 
	tbltempstaticpool.bigAccountId,
	tbltempstaticpool.dtmFunded,
	tblDove.strRequest
from riskdb.analytics.tbltempstaticpool
left outer join
(
	select
		bigAccountId,
		max(bigDoveId) as bigDoveId
	from zestdb.dbo.tblDove
	group by bigAccountId
)tblMax1 on tblMax1.bigAccountid=tbltempstaticpool.bigAccountId
left outer join zestdb.dbo.tblDove on tblDove.bigDoveId=tblMax1.bigDoveId
where dtmFunded >= '01/01/2023'