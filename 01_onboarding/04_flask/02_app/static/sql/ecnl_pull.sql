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
),
TblScore2 as
(
select    
        *,
        Row_number()
              OVER(
                partition BY intAccountKey
                ORDER BY dtmStampCreation desc) RowNum
    from edw.pfsedw.dbo.DimScoreCard
	where strScoreCardVersion in ('genxii', 'genxii_v2', 'genxii_v3', 'genxii_v4', 'genxii_v5')
),
TblScore3 as 
(
select    
        *,
        Row_number()
              OVER(
                partition BY intAccountKey
                ORDER BY dtmStampCreation desc) RowNum
    from edw.pfsedw.dbo.DimScoreCard
	where strScoreCardVersion in ('dlv1','dlv1_1')
),
tblEPD as
(
SELECT 
c.bigAccountId,
	SUM(CASE
			WHEN DATEDIFF(DAY, c.dtmDue, c.dtmClosed) > 29 OR (DATEDIFF(DAY, c.dtmDue, GETDATE()) > 29 AND c.dtmClosed IS NULL) 
				THEN 1
				ELSE 0
				END) AS Early_Pay_Delinquency_30_120,
	SUM(CASE
			WHEN DATEDIFF(DAY, c.dtmDue, c.dtmClosed) > 14 OR (DATEDIFF(DAY, c.dtmDue, GETDATE()) > 14 AND c.dtmClosed IS NULL) 
				THEN 1
				ELSE 0
				END) AS Early_Pay_Delinquency_15_120,
am.dtmNonAccrual,
am.dtmContract
FROM pfsdb.dbo.tblCharges c LEFT OUTER JOIN pfsdb.dbo.tblAccountTerms att ON c.bigAccountTermId = att.bigAccountTermId
INNER JOIN pfsdb.dbo.tblAccountMaintenance am ON c.bigAccountId = am.bigAccountId

WHERE c.bigChargeTypeId = 1 AND c.bitInvalid = 0 AND c.dtmDue < DATEADD(DAY, 120, am.dtmContract)
GROUP BY c.bigAccountId, am.dtmContract, am.dtmNonAccrual
)

select
	tbltempstaticpool.bigAccountId,
	tbltempstaticpool.bigDealerId,
    CASE 
        WHEN DATEPART(day, tbltempstaticpool.dtmFunded) <= 7 THEN 1
        WHEN DATEPART(day, tbltempstaticpool.dtmFunded) <= 14 THEN 2
        WHEN DATEPART(day, tbltempstaticpool.dtmFunded) <= 21 THEN 3
        ELSE 4
    END as week_of_month,
	CONVERT(varchar, tblAccount.dtmStampCreation, 105) as application_date,
    CONVERT(varchar, tbltempstaticpool.dtmFunded, 105) as dtmFunded,
	tblEPD.dtmNonAccrual,
	tbltempstaticpool.intterm,
	tbltempstaticpool.intOpenBKType as open_bk_type,
	CONVERT(varchar, tbltempstaticpool.dtmFirstPayment, 105) as first_pmt_date,
	tbltempstaticpool.paymentsmade,
	--tbltempstaticpool.intVehicleClass,
	--year(tbltempstaticpool.dtmFunded) - tbltempstaticpool.VehicleYear as VehicleAge,
	tbltempstaticpool.strTier as Tier, 
	DebtorState, 
	tbltempstaticpool.AmtFinanced,
	OriginalInterestRate/100 as OriginalInterestRate, 
	fltAPRCurrent/100 as fltAPRCurrent,
	tbltempstaticpool.MaxFico,
	tbltempstaticpool.intBeaconScore,
	mnyReserve,
	mnyDiscount,
	tblEPD.Early_Pay_Delinquency_15_120,
	tblEPD.Early_Pay_Delinquency_30_120,
	CASE 
			WHEN tblEPD.Early_Pay_Delinquency_15_120 > 0 
				AND (tblEPD.dtmNonAccrual IS NOT NULL AND DATEDIFF(DAY, tblEPD.dtmContract, tblEPD.dtmNonAccrual) < 120)
			THEN 1
			ELSE 0
		END AS Early_Pay_Default_15_120,
	CASE 
			WHEN tblEPD.Early_Pay_Delinquency_30_120 > 0 
				AND (tblEPD.dtmNonAccrual IS NOT NULL AND DATEDIFF(DAY, tblEPD.dtmContract, tblEPD.dtmNonAccrual) < 120)
			THEN 1
			ELSE 0
		END AS Early_Pay_Default_30_120,
	--tbltempstaticpool.bitEarlyDefault_15_3 as EPDq,
	tbltempstaticpool.LoanStatus,
	tbltempstaticpool.COSeverity as ChargeOff_Severity,
	tblGenXI.fltDebtorScore * tbltempstaticpool.AmtFinanced as GEN11_ExpectedNetLoss,
	tblGenXI.fltDebtorScore as GEN11_ECNL,
	tblGenXII.fltDebtorScore * tbltempstaticpool.AmtFinanced as GEN12_ExpectedNetLoss,
	tblGenXII.fltDebtorScore as GEN12_ECNL,
	((tblGenXII.fltDebtor_Score_ecnl + tblGenXII.fltCoDebtor_Score_ecnl) /2) as GEN12_ECNL_mod,
	tblDL.fltDebtorScore * tbltempstaticpool.AmtFinanced as DL_ExpectedNetLoss,
	tblDL.fltDebtorScore as DL_ECNL,
	CASE
		WHEN (RIGHT (tbltempstaticpool.bigAccountId, 1) = '0' OR RIGHT (tbltempstaticpool.bigAccountId, 1) = '5') AND tblAccount.dtmStampCreation BETWEEN '2024-01-17' AND '2024-02-07'
		THEN 'gen12'
		WHEN ((RIGHT (tbltempstaticpool.bigAccountId, 1) = '0' OR RIGHT (tbltempstaticpool.bigAccountId, 1) = '5') AND tblAccount.dtmStampCreation >= '2024-05-31')
		THEN 'gen12'
		WHEN tblDL.fltDebtorScore is not NULL
		THEN 'direct lending'
		ELSE 'gen11'
	END AS origination_model

from riskdb.analytics.tbltempstaticpool
left outer join
(
    select    
        *
    from TblScore
    where RowNum=1
)tblGenXI on tblGenXI.intAccountKey=tbltempstaticpool.bigAccountId
left outer join
(
    select    
        *
    from TblScore2
    where RowNum=1
)tblGenXII on tblGenXII.intAccountKey=tbltempstaticpool.bigAccountId
left outer join
(
    select    
        *
    from TblScore3
    where RowNum=1
)tblDL on tblDL.intAccountKey=tbltempstaticpool.bigAccountId
left outer join
electra.pfsdb.dbo.tblAccount on tbltempstaticpool.bigAccountId=tblAccount.bigAccountId
left outer join
tblEPD on tbltempstaticpool.bigAccountId=tblEPD.bigAccountId
where tbltempstaticpool.dtmFunded >= '2024-08-01'
order by dtmFunded 