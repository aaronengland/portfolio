SELECT TOP 10000 bigIncomeId, dtmStampCreation, fltGrossMonthly, strEmployerName, intMonths, intYears
FROM electra.pfsdb.dbo.tblincome
WHERE dtmStampCreation >= '2020'
ORDER BY dtmStampCreation DESC;
