select
    ACCOUNTID as bigAccountId,
    ORIGINALSCORE as fltDebtorScore,
    SCORECARDVERSION
from RAW.SOURCE_MONGO.SCORE_SCORERESULT
where STAMPCREATION >= '2024-03-14'
and SCORECARDVERSION in ('genxi_v2_3','genxii_v2')
order by stampcreation desc