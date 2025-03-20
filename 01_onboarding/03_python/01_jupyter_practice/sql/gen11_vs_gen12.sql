with Gen11Tbl as
(
	select
		ROW_NUMBER()
			OVER(
				PARTITION BY IntAccountKey
				ORDER BY dtmStampCreation desc) RowNum,
		IntAccountKey,
		strScoreCardVersion,
		fltDebtorScore as Gen11Score
	from edw.pfsedw.dbo.DimScoreCard
	where strScoreCardVersion in ('genxi_v2_2')
	or strScoreCardVersion in('genxi_v2_3')
	and dtmStampCreation >= '2024-01-01'
	--and RowNum = 1
),
Gen12Tbl as
(
	select
		ROW_NUMBER()
			OVER(
				PARTITION BY IntAccountKey
				ORDER BY dtmStampCreation desc) RowNum,
		IntAccountKey,
		strScoreCardVersion,
		fltDebtorScore as Gen12Score
	from edw.pfsedw.dbo.DimScoreCard
	where strScoreCardVersion in ('genxii')
	or strScoreCardVersion in('genxii_v2')
	and dtmStampCreation >= '2024-01-01'
)

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
		tsp.MaxFico,
		tblGen11Row1.Gen11Score,
		tblGen12Row1.Gen12Score
	from electra.riskdb.analytics.tbltempstaticpool as tsp
		left outer join tblAccount as acc on tsp.bigAccountId = acc.bigAccountId
		left outer join (select * from Gen11Tbl where RowNum = 1) as tblGen11Row1 on tsp.bigAccountId = tblGen11Row1.IntAccountKey 
		left outer join (select * from Gen12Tbl where RowNum = 1) as tblGen12Row1 on tsp.bigAccountId = tblGen12Row1.IntAccountKey
	where acc.dtmStampCreation >= '2024-01-01'
	order by tsp.dtmFunded desc
