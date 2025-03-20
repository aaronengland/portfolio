select
	bigAccountId,
	1 as bitDefault,
	dtmStampCreation as defaultDate
from electra.pfsdb.dbo.tblDefault 
where bitInvalid = 0