SELECT TOP 10000 bigAccountId
FROM electra.pfsdb.dbo.tblaccount
WHERE dtmStampCreation >= '2020'
