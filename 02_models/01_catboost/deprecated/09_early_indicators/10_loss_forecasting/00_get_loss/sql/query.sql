SELECT
bigAccountId,
dtmBooking,
BookingQuarter,
fltNetChgOff,
MonthEndDate
FROM medusa.riskdb.accountingReports.tblAccounting_LoanCOandNA_ME
WHERE 
MonthEndDate = 'STR_MONTH_END' 
-- AND dtmBooking >= '2013-01-01' 
-- AND dtmBooking < '2020-01-01'