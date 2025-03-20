with TblScore as
(
select    
        *,
        Row_number()
              OVER(
                partition BY intAccountKey
                ORDER BY dtmStampCreation desc) RowNum
    from edw.pfsedw.dbo.DimScoreCard
	where strScoreCardVersion in ('genxi','genxi_v1_1','genxi_v2','genxi_v2_1','genxi_v2_2', 'genxi_v2_3')
)

select 
	tblAccount.bigAccountId,
	CONVERT(varchar, tblAccount.dtmStampCreation, 105) as application_date,
	CONVERT(varchar, tblAccount.dtmApproved, 105) as application_date,
	CONVERT(varchar, tblAccount.dtmFunded, 105) as dtmFunded,
	tbltempstaticpool.OriginalInterestRate / 100 as OriginalInterestRate,
	tbltempstaticpool.mnyReserve,
	tbltempstaticpool.mnyDiscount,
	tblGenXI.fltDebtorScore as GEN11_ECNL
from electra.pfsdb.dbo.tblAccount
left outer join riskdb.analytics.tbltempstaticpool on tbltempstaticpool.bigAccountId=tblAccount.bigAccountId
left outer join 
(
    select    
        *
    from TblScore
    where RowNum=1
)tblGenXI on tblGenXI.intAccountKey=tblAccount.bigAccountId
where tblAccount.dtmApproved >= '2022-01-01'
and tblAccount.dtmApproved <= '2022-12-31'
