with TblScore as
(
select    
        *,
        Row_number()
              OVER(
                partition BY ACCOUNTID
                ORDER BY STAMPCREATION desc) RowNum
    from raw.source_mongo.score_scoreresult
	where SCORECARDVERSION in ('genxi','genxi_v1_1','genxi_v2','genxi_v2_1','genxi_v2_2', 'genxi_v2_3')
),
TblScore2 as
(
select    
        *,
        Row_number()
              OVER(
                partition BY ACCOUNTID
                ORDER BY STAMPCREATION desc) RowNum
    from raw.source_mongo.score_scoreresult
	where SCORECARDVERSION in ('genxii', 'genxii_v2', 'genxii_v3', 'genxii_v4', 'genxii_v5', 'genxii_v6')
),
TblScore3 as 
(
select    
        *,
        Row_number()
              OVER(
                partition BY ACCOUNTID
                ORDER BY STAMPCREATION desc) RowNum
    from raw.source_mongo.score_scoreresult
	where SCORECARDVERSION in ('dlv1','dlv1_1')
),
TblScore4 as 
(
select    
        *,
        Row_number()
              OVER(
                partition BY ACCOUNTID
                ORDER BY STAMPCREATION desc) RowNum
    from raw.source_mongo.score_scoreresult
	where SCORECARDVERSION in ('genxiii','genxiii_')
),
TblBookValue as
(
select    
        *,
        Row_number()
              OVER(
                partition BY ACCOUNT_ID
                ORDER BY VEHICLE_CREATION_DATE desc) RowNum
    from DATAWAREHOUSE.PUBLIC.DIM_ACCOUNT_VEHICLE
),
TempStaticPool as
(
SELECT
tbltempstaticpool.ACCOUNT_NUMBER,
tbldealer.PHYSICAL_STATE,
tbldealer.DEALER_TRACKER_TYPE,
tblaccount.APPLICATION_DATE,
tblaccount.FUNDED_DATE,
tblaccount.TIER,
tblpipe.TERM,
tblaccount.OPEN_BK_TYPE,
tbltempstaticpool.AMOUNT_FINANCED,
tbltempstaticpool.MONTHLY_PAYMENT,
tblpipe.CASH_DOWN_AMOUNT,
tblpipe.SERVICE_CONTRACT_AMOUNT,
tblpipe.GUARANTEED_AUTO_PROTECTION_AMOUNT,
tblaccount.FIRST_PAYMENT_DATE,
tbltempstaticpool.MONTHS_ON_BOOKS,
tbltempstaticpool.INSTALLMENTS_CLOSED_ON_TIME,
tbltempstaticpool.APR_CURRENT,
tbltempstaticpool.DELINQUENCY_BUCKET,
tbltempstaticpool.EARLY_PAY_DELINQUENCY_15_120,
tbltempstaticpool.EARLY_PAY_DELINQUENCY_30_120,
tbltempstaticpool.EARLY_PAY_DEFAULT_15_120,
tbltempstaticpool.EARLY_PAY_DEFAULT_30_120,
tbltempstaticpool.APR_ORIGINAL,
tbltempstaticpool.RESERVE_AT_FUNDING,
tbltempstaticpool.DISCOUNT_AT_FUNDING,
FROM DATAWAREHOUSE.PUBLIC.FACT_ACCOUNT_DAILY as tbltempstaticpool 
LEFT OUTER JOIN 
DATAWAREHOUSE.PUBLIC.DIM_APPLICATION_ACCOUNT as tblaccount ON tbltempstaticpool.ACCOUNT_NUMBER=tblaccount.ACCOUNT_ID
LEFT OUTER JOIN
DATAWAREHOUSE.PUBLIC.FACT_APPLICANT_PIPELINE as tblpipe ON tbltempstaticpool.ACCOUNT_NUMBER=tblpipe.ACCOUNT_ID
LEFT OUTER JOIN 
DATAWAREHOUSE.PUBLIC.DIM_DEALER as tbldealer ON tbltempstaticpool.DEALER_KEY=tbldealer.DEALER_KEY

WHERE tbltempstaticpool.PERIODIC_RUN_DATE = (SELECT MAX(PERIODIC_RUN_DATE) FROM  DATAWAREHOUSE.PUBLIC.FACT_ACCOUNT_DAILY)
)

SELECT
TempStaticPool.ACCOUNT_NUMBER,
    CASE 
        WHEN DATE_PART('day', TempStaticPool.FUNDED_DATE) <= 7 THEN 1
        WHEN DATE_PART('day', TempStaticPool.FUNDED_DATE) <= 14 THEN 2
        WHEN DATE_PART('day', TempStaticPool.FUNDED_DATE) <= 21 THEN 3
        ELSE 4
    END as week_of_month,
TempStaticPool.DEALER_TRACKER_TYPE,
TempStaticPool.PHYSICAL_STATE as DEALER_STATE,
TempStaticPool.OPEN_BK_TYPE,
TempStaticPool.APPLICATION_DATE,
TempStaticPool.FUNDED_DATE,
TempStaticPool.TIER,
TempStaticPool.TERM,
TempStaticPool.FIRST_PAYMENT_DATE,
TempStaticPool.MONTHS_ON_BOOKS,
TempStaticPool.MONTHLY_PAYMENT,
TempStaticPool.INSTALLMENTS_CLOSED_ON_TIME,
TempStaticPool.AMOUNT_FINANCED,
TempStaticPool.RESERVE_AT_FUNDING,
TempStaticPool.DISCOUNT_AT_FUNDING,
tblbookvalue.VEHICLE_BOOK_VALUE,
(TempStaticPool.AMOUNT_FINANCED / tblbookvalue.VEHICLE_BOOK_VALUE) as LTV_CALC,
TempStaticPool.CASH_DOWN_AMOUNT,
TempStaticPool.SERVICE_CONTRACT_AMOUNT,
TempStaticPool.GUARANTEED_AUTO_PROTECTION_AMOUNT as GAP_AMOUNT,
TempStaticPool.APR_ORIGINAL/100 as APR_ORIGINAL,
TempStaticPool.APR_CURRENT/100 as APR_CURRENT,
TempStaticPool.DELINQUENCY_BUCKET,
TempStaticPool.EARLY_PAY_DELINQUENCY_15_120,
TempStaticPool.EARLY_PAY_DELINQUENCY_30_120,
TempStaticPool.EARLY_PAY_DEFAULT_15_120,
TempStaticPool.EARLY_PAY_DEFAULT_30_120,
tblDL.DEBTORSCORE as DL_ECNL,
tblGenXI.DEBTORSCORE as GEN11_ECNL,
tblGENXII.DEBTORSCORE as GEN12_ECNL,
    (COALESCE(NULLIF(tblGENXII.DEBTOR_SCORE_ECNL, 0), 0) + COALESCE(NULLIF(tblGENXII.CODEBTOR_SCORE_ECNL, 0), 0)) / 
    (CASE WHEN tblGENXII.DEBTOR_SCORE_ECNL != 0 AND tblGENXII.CODEBTOR_SCORE_ECNL != 0 THEN 2
          WHEN tblGENXII.DEBTOR_SCORE_ECNL != 0 OR tblGENXII.CODEBTOR_SCORE_ECNL != 0 THEN 1
          ELSE NULL
     END) AS GEN12_ECNL_MOD,
     
tblGenXIII.DEBTORSCORE as GEN13_ECNL,

    (COALESCE(NULLIF(tblGenXIII.DEBTOR_SCORE_ECNL, 0), 0) + COALESCE(NULLIF(tblGenXIII.CODEBTOR_SCORE_ECNL, 0), 0)) / 
    (CASE WHEN tblGenXIII.DEBTOR_SCORE_ECNL != 0 AND tblGenXIII.CODEBTOR_SCORE_ECNL != 0 THEN 2
          WHEN tblGenXIII.DEBTOR_SCORE_ECNL != 0 OR tblGenXIII.CODEBTOR_SCORE_ECNL != 0 THEN 1
          ELSE NULL
     END) AS GEN13_ECNL_MOD,
     
(COALESCE(NULLIF(tblGenXIII.DEBTOR_SCORE_PD, 0), 0) + COALESCE(NULLIF(tblGenXIII.CODEBTOR_SCORE_PD, 0), 0)) / 
    (CASE WHEN tblGenXIII.DEBTOR_SCORE_PD != 0 AND tblGenXIII.CODEBTOR_SCORE_PD != 0 THEN 2
          WHEN tblGenXIII.DEBTOR_SCORE_PD != 0 OR tblGenXIII.CODEBTOR_SCORE_PD != 0 THEN 1
          ELSE NULL
     END) AS GEN13_PD,
     
CASE
	WHEN tblDL.DEBTORSCORE is not NULL
		THEN 'direct lending'
	WHEN (RIGHT (TempStaticPool.ACCOUNT_NUMBER, 1) = '0' OR RIGHT (TempStaticPool.ACCOUNT_NUMBER, 1) = '5') AND TempStaticPool.APPLICATION_DATE BETWEEN '2024-01-17' AND '2024-02-07'
		THEN 'gen12'
	WHEN ((RIGHT (TempStaticPool.ACCOUNT_NUMBER, 1) = '0' OR RIGHT (TempStaticPool.ACCOUNT_NUMBER, 1) = '5') AND TempStaticPool.APPLICATION_DATE >= '2024-05-31')
		THEN 'gen12'
	WHEN TempStaticPool.APPLICATION_DATE >= '2024-08-01' 
		THEN 'gen12'
		  ELSE 'gen11'
END AS ORIGINATED_BY

FROM
TempStaticPool LEFT OUTER JOIN 
(
    select    
        *
    from TblScore
    where RowNum=1
) as tblGenXI on tblGenXI.ACCOUNTID=TempStaticPool.ACCOUNT_NUMBER
LEFT OUTER JOIN 
(
    select    
        *
    from TblScore2
    where RowNum=1
) as tblGenXII on tblGenXII.ACCOUNTID=TempStaticPool.ACCOUNT_NUMBER
LEFT OUTER JOIN 
(
    select    
        *
    from TblScore3
    where RowNum=1
) as tblDL on tblDL.ACCOUNTID=TempStaticPool.ACCOUNT_NUMBER
LEFT OUTER JOIN 
(
    select    
        *
    from TblScore4
    where RowNum=1
) as tblGenXIII on tblGenXIII.ACCOUNTID=TempStaticPool.ACCOUNT_NUMBER
LEFT OUTER JOIN
(
    select    
        *
    from TblBookValue
    where RowNum=1
) as tblbookvalue on tblbookvalue.ACCOUNT_ID=TempStaticPool.ACCOUNT_NUMBER

WHERE TempStaticPool.FUNDED_DATE between '2021-01-01' and GETDATE()
