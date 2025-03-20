SELECT strName as [Dealer], YTDApplicationcount as [Applications], YTDApprovedCount as [Approved], YTDFundedCount as [Funded]
FROM riskdb.dbo.tbldealerstats
ORDER BY YTDApplicationcount DESC
OFFSET 2 ROWS
FETCH NEXT 10 ROWS ONLY;
