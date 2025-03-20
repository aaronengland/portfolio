with tblMax as
(
select
	bigAccountId,
	max(concat(MonthOnBooks, bigAccountid, bigRunDateKeyId)) as MaxUnique
from riskdb.dbo.tblReportCOStaticPools_StaticPool
where MonthOnBooks<=72
group by bigAccountId
),



tblReportCOStaticPools_StaticPoolNew as
(
select
	concat(MonthOnBooks, bigAccountid, bigRunDateKeyId) as uniqueC,
	*
from riskdb.dbo.tblReportCOStaticPools_StaticPool
where MonthOnBooks<=72
)



select 
	CONCAT(tblAccount.bigAccountId, tblAccount.bigDebtorId, 1) as UniqueID,
	tbltempstaticpool.bigAccountId,
	tblAccount.bigDebtorId,
	1 as bitDebtor,
	tblAccount.dtmStampCreation,
	tbltempstaticpool.dtmFunded,
	case when tbltempstaticpool.LoanStatusCNCombined='Default' then 1 else 0 end as bitDefault,
	tblReportCOStaticPools_StaticPoolNew.MonthOnBooks,
	tblReportCOStaticPools_StaticPoolNew.RunningNetLoss,
	tbltempstaticpool.AmtFinanced,
	tbltempstaticpool.intOpenBKType,
	tbltempstaticpool.intTerm,
	tbltempstaticpool.bitLHMGroup,
	year(tbltempstaticpool.dtmFunded) - tbltempstaticpool.VehicleYear as VehicleAge,
	tbltempstaticpool.bitNew,
	tbltempstaticpool.VehicleMake,
	tbltempstaticpool.VehicleModel,
	tbltempstaticpool.Miles_Odometer,
	tbltempstaticpool.BookValue,
	tbltempstaticpool.fltDownCash,
	tblAccount.fltApprovedDownTotal,
	tbltempstaticpool.income,
	tbltempstaticpool.DTI,
	tbltempstaticpool.PTI,
	tbltempstaticpool.intTermBump,
	tbltempstaticpool.fltServiceContract,
	tbltempstaticpool.bitServiceContract,
	tbltempstaticpool.LoanToValue,
	tbltempstaticpool.fltAdvance,
	tbltempstaticpool.strVehicleType,
	tbltempstaticpool.fltGapInsurance,
	tbltempstaticpool.bitGap,
	tbltempstaticpool.BKOrRecentDischarge,
	tbltempstaticpool.bitRecentDischarge,
	tbltempstaticpool.fltBumpFee,
	tbltempstaticpool.fltMileageFee,
	tbltempstaticpool.DealerType,
	tbltempstaticpool.intVehicleClass,
	tblDealer.dtmStampCreation  as DealerStampCreation
from riskdb.analytics.tbltempstaticpool
left outer join tblMax on tblMax.bigAccountid=tbltempstaticpool.bigAccountId
left outer join tblReportCOStaticPools_StaticPoolNew on tblReportCOStaticPools_StaticPoolNew.uniqueC=tblMax.MaxUnique
left outer join tblAccount on tblAccount.bigAccountId=tbltempstaticpool.bigAccountId
left outer join tblDealer on tblDealer.bigDealerId=tbltempstaticpool.bigDealerId
where tblAccount.dtmStampCreation>='10/01/2013'
and tblAccount.dtmStampCreation<'01/01/2020'

union

select 
	CONCAT(tblAccount.bigAccountId, tblAccount.bigDebtorId, 1) as UniqueID,
	tbltempstaticpool.bigAccountId,
	tblCosigner.bigDebtorId_cosigner as bigDebtorId,
	0 as bitDebtor,
	tblAccount.dtmStampCreation,
	tbltempstaticpool.dtmFunded,
	case when tbltempstaticpool.LoanStatusCNCombined='Default' then 1 else 0 end as bitDefault,
	tblReportCOStaticPools_StaticPoolNew.MonthOnBooks,
	tblReportCOStaticPools_StaticPoolNew.RunningNetLoss,
	tbltempstaticpool.AmtFinanced,
	tbltempstaticpool.intOpenBKType,
	tbltempstaticpool.intTerm,
	tbltempstaticpool.bitLHMGroup,
	year(tbltempstaticpool.dtmFunded) - tbltempstaticpool.VehicleYear as VehicleAge,
	tbltempstaticpool.bitNew,
	tbltempstaticpool.VehicleMake,
	tbltempstaticpool.VehicleModel,
	tbltempstaticpool.Miles_Odometer,
	tbltempstaticpool.BookValue,
	tbltempstaticpool.fltDownCash,
	tblAccount.fltApprovedDownTotal,
	tbltempstaticpool.income,
	tbltempstaticpool.DTI,
	tbltempstaticpool.PTI,
	tbltempstaticpool.intTermBump,
	tbltempstaticpool.fltServiceContract,
	tbltempstaticpool.bitServiceContract,
	tbltempstaticpool.LoanToValue,
	tbltempstaticpool.fltAdvance,
	tbltempstaticpool.strVehicleType,
	tbltempstaticpool.fltGapInsurance,
	tbltempstaticpool.bitGap,
	tbltempstaticpool.BKOrRecentDischarge,
	tbltempstaticpool.bitRecentDischarge,
	tbltempstaticpool.fltBumpFee,
	tbltempstaticpool.fltMileageFee,
	tbltempstaticpool.DealerType,
	tbltempstaticpool.intVehicleClass,
	tblDealer.dtmStampCreation as DealerStampCreation
from riskdb.analytics.tbltempstaticpool
left outer join tblMax on tblMax.bigAccountid=tbltempstaticpool.bigAccountId
left outer join tblReportCOStaticPools_StaticPoolNew on tblReportCOStaticPools_StaticPoolNew.uniqueC=tblMax.MaxUnique
left outer join tblAccount on tblAccount.bigAccountId=tbltempstaticpool.bigAccountId
left outer join tblDealer on tblDealer.bigDealerId=tbltempstaticpool.bigDealerId
left outer join tblCosigner on tblCosigner.bigAccountId=tbltempstaticpool.bigAccountId
where tblAccount.dtmStampCreation>='10/01/2013'
and tblAccount.dtmStampCreation<'01/01/2020'
and tblCosigner.bigDebtorId_cosigner is not null

