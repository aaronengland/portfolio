
SELECT TSP.bigAccountId, 
TSP.AmtFinanced, 
ACC.fltNetChgOff

FROM electra.riskdb.analytics.tbltempstaticpool as TSP

INNER JOIN riskdb.accountingReports.tblAccounting_LoanCOandNA_ME as ACC on TSP.bigAccountId = ACC.bigAccountId