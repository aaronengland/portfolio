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
),

debt AS
(
	SELECT
		bigAccountId,
		bigDebtorId,
		ISNULL(SUM(fltMonthlyPayment), 0) AS debt 
	FROM electra.pfsdb.dbo.tblDebt d
	WHERE bitUse = 1 AND fltMonthlyPayment IS NOT NULL
	GROUP BY bigAccountId, bigDebtorId
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
	tbltempstaticpool.VehicleYear,
	tbltempstaticpool.bitNew,
	tbltempstaticpool.VehicleMake,
	tbltempstaticpool.Miles_Odometer,
	tbltempstaticpool.BookValue,
	tbltempstaticpool.fltDownCash,
	tblAccount.fltApprovedDownTotal,
	tbltempstaticpool.fltPaymentOriginal as Payment,
	tbltempstaticpool.DTI,
	tbltempstaticpool.PTI,
	tbltempstaticpool.bitServiceContract,
	tbltempstaticpool.fltAdvance,
	tbltempstaticpool.strVehicleType,
	tbltempstaticpool.bitGap,
	tblDealer.dtmStampCreation as DealerStampCreation,
	debt.debt as totaldebt
from riskdb.analytics.tbltempstaticpool
left outer join tblMax on tblMax.bigAccountid=tbltempstaticpool.bigAccountId
left outer join tblReportCOStaticPools_StaticPoolNew on tblReportCOStaticPools_StaticPoolNew.uniqueC=tblMax.MaxUnique
left outer join tblAccount on tblAccount.bigAccountId=tbltempstaticpool.bigAccountId
left outer join tblDealer on tblDealer.bigDealerId=tbltempstaticpool.bigDealerId
left outer join debt on tbltempstaticpool.bigaccountId = debt.bigAccountId AND tblAccount.bigDebtorId = debt.bigDebtorId
where tblAccount.dtmStampCreation>='01/01/2021'

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
	tbltempstaticpool.VehicleYear,
	tbltempstaticpool.bitNew,
	tbltempstaticpool.VehicleMake,
	tbltempstaticpool.Miles_Odometer,
	tbltempstaticpool.BookValue,
	tbltempstaticpool.fltDownCash,
	tblAccount.fltApprovedDownTotal,
	tbltempstaticpool.fltPaymentOriginal as Payment,
	tbltempstaticpool.DTI,
	tbltempstaticpool.PTI,
	tbltempstaticpool.bitServiceContract,
	tbltempstaticpool.fltAdvance,
	tbltempstaticpool.strVehicleType,
	tbltempstaticpool.bitGap,
	tblDealer.dtmStampCreation as DealerStampCreation,
	debt.debt as totaldebt
from riskdb.analytics.tbltempstaticpool
left outer join tblMax on tblMax.bigAccountid=tbltempstaticpool.bigAccountId
left outer join tblReportCOStaticPools_StaticPoolNew on tblReportCOStaticPools_StaticPoolNew.uniqueC=tblMax.MaxUnique
left outer join tblAccount on tblAccount.bigAccountId=tbltempstaticpool.bigAccountId
left outer join tblDealer on tblDealer.bigDealerId=tbltempstaticpool.bigDealerId
left outer join tblCosigner on tblCosigner.bigAccountId=tbltempstaticpool.bigAccountId
left outer join debt on tbltempstaticpool.bigAccountId = debt.bigAccountId AND tblCosigner.bigDebtorId_cosigner = debt.bigDebtorId
where tblAccount.dtmStampCreation>='01/01/2021'
and tblCosigner.bigDebtorId_cosigner is not null