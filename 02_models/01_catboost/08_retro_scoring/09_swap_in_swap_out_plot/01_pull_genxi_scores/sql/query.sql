with tbl1 as
	(
		select DimScoreCard.*,
		tbltempstaticpool.bigaccountID,
		Row_number() OVER(partition BY intAccountKey ORDER BY dtmStampCreation desc) RowNum
		from riskdb.analytics.tbltempstaticpool left outer join edw.pfsedw.dbo.DimScoreCard 
			on tbltempstaticpool.bigAccountId = DimScoreCard.intAccountKey
		where dtmstampcreation >= '2022-01-01'
		and strScoreCardVersion not in ( 'genxii', 'dlv1', 'dlv1_1')

	)
		select
		dtmstampcreation as App_date, 
		bigAccountId, 
		fltDebtorScore, 
		strScoreCardVersion
		from tbl1 
		where RowNum = 1
		order by dtmstampcreation