library(tidyverse)
library(RODBC)


odbcChannel=odbcConnect("electra pfsdb")

data=sqlQuery(odbcChannel, paste(
  "
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
	tbltempstaticpool.DefaultDate,
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
	tblDealer.dtmStampCreation as DealerStampCreation
from riskdb.analytics.tbltempstaticpool
left outer join tblMax on tblMax.bigAccountid=tbltempstaticpool.bigAccountId
left outer join tblReportCOStaticPools_StaticPoolNew on tblReportCOStaticPools_StaticPoolNew.uniqueC=tblMax.MaxUnique
left outer join tblAccount on tblAccount.bigAccountId=tbltempstaticpool.bigAccountId
left outer join tblDealer on tblDealer.bigDealerId=tbltempstaticpool.bigDealerId
where tblAccount.dtmStampCreation>='10/01/2013'

union

select 
	CONCAT(tblAccount.bigAccountId, tblAccount.bigDebtorId, 1) as UniqueID,
	tbltempstaticpool.bigAccountId,
	tblCosigner.bigDebtorId_cosigner as bigDebtorId,
	0 as bitDebtor,
	tblAccount.dtmStampCreation,
	tbltempstaticpool.dtmFunded,
	case when tbltempstaticpool.LoanStatusCNCombined='Default' then 1 else 0 end as bitDefault,
	tbltempstaticpool.DefaultDate,
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
	tblDealer.dtmStampCreation as DealerStampCreation
from riskdb.analytics.tbltempstaticpool
left outer join tblMax on tblMax.bigAccountid=tbltempstaticpool.bigAccountId
left outer join tblReportCOStaticPools_StaticPoolNew on tblReportCOStaticPools_StaticPoolNew.uniqueC=tblMax.MaxUnique
left outer join tblAccount on tblAccount.bigAccountId=tbltempstaticpool.bigAccountId
left outer join tblDealer on tblDealer.bigDealerId=tbltempstaticpool.bigDealerId
left outer join tblCosigner on tblCosigner.bigAccountId=tbltempstaticpool.bigAccountId
where tblAccount.dtmStampCreation>='10/01/2013'
and tblCosigner.bigDebtorId_cosigner is not null    
              
              ", sep="")
)

odbcClose(odbcChannel)



odbcChannel=odbcConnect("electra dw")

daysLate=sqlQuery(odbcChannel, paste(
  "
select
	bigAccountId,
	DATEDIFF(Month, BKKDate, RunDate) as MOB,
	max(DaysLate) as MaxDaysLate		
from dw.dbo.fact
--where DATEDIFF(Month, BKKDate, RunDate) < 1
group by bigAccountId, DATEDIFF(Month, BKKDate, RunDate)
order by bigAccountId, DATEDIFF(Month, BKKDate, RunDate) 
              
              ", sep="")
)

odbcClose(odbcChannel)


odbcChannel=odbcConnect("electra pfsdb")

default=sqlQuery(odbcChannel, paste(
  "
select 
	tbltempstaticpool.bigAccountId,
	tbltempstaticpool.dtmFunded,
	tbltempstaticpool.DefaultDate,
	DATEDIFF(Month, tbltempstaticpool.dtmFunded, tbltempstaticpool.DefaultDate) as TimeToDefault,
	DATEDIFF(Month, tbltempstaticpool.dtmFunded, Getdate()) as TimeToToday
from riskdb.analytics.tbltempstaticpool
left outer join tblAccount on tblAccount.bigAccountId=tbltempstaticpool.bigAccountId
where tblAccount.dtmStampCreation>='10/01/2013'
              
              ", sep="")
)

odbcClose(odbcChannel)


daysLate <- subset(daysLate, daysLate$bigAccountId>=1337511)

daysLate1 <- daysLate %>%
  group_by(bigAccountId) %>%
  arrange(MOB, .by_group = TRUE) %>%
  mutate(CumMaxDaysLate = cummax(MaxDaysLate))

# targets: 1+, 15+, 30+, 60+, default

daysLate1$DQ1 <- ifelse(daysLate1$CumMaxDaysLate>0, 1, 0)
daysLate1$DQ15 <- ifelse(daysLate1$CumMaxDaysLate>15, 1, 0)
daysLate1$DQ30 <- ifelse(daysLate1$CumMaxDaysLate>30, 1, 0)
daysLate1$DQ60 <- ifelse(daysLate1$CumMaxDaysLate>60, 1, 0)
daysLate1$DQ90 <- ifelse(daysLate1$CumMaxDaysLate>90, 1, 0)

daysLate1 <- daysLate1 %>%
  select(-MaxDaysLate, -CumMaxDaysLate)
daysLate1 <- subset(daysLate1, daysLate1$MOB<=72)


library(reshape2)

daysLate2 <-dcast(data = daysLate1,formula = bigAccountId~MOB,fun.aggregate = sum,value.var = "DQ1")
daysLate15 <-dcast(data = daysLate1,formula = bigAccountId~MOB,fun.aggregate = sum,value.var = "DQ15")
daysLate30 <-dcast(data = daysLate1,formula = bigAccountId~MOB,fun.aggregate = sum,value.var = "DQ30")
daysLate60 <-dcast(data = daysLate1,formula = bigAccountId~MOB,fun.aggregate = sum,value.var = "DQ60")
daysLate90 <-dcast(data = daysLate1,formula = bigAccountId~MOB,fun.aggregate = sum,value.var = "DQ90")


daysLate2 <- melt(daysLate2, id="bigAccountId")
daysLate2 <- daysLate2 %>%
  group_by(bigAccountId) %>%
  arrange(variable, .by_group = TRUE) %>%
  mutate(MaxValue = cummax(value))
daysLate2 <-dcast(data = daysLate2,formula = bigAccountId~variable,fun.aggregate = sum,value.var = "MaxValue")
colnames(daysLate2)[2:ncol(daysLate2)] <- paste("DQ1_", colnames(daysLate2)[2:ncol(daysLate2)], sep="")

daysLate15 <- melt(daysLate15, id="bigAccountId")
daysLate15 <- daysLate15 %>%
  group_by(bigAccountId) %>%
  arrange(variable, .by_group = TRUE) %>%
  mutate(MaxValue = cummax(value))
daysLate15 <-dcast(data = daysLate15,formula = bigAccountId~variable,fun.aggregate = sum,value.var = "MaxValue")
colnames(daysLate15)[2:ncol(daysLate15)] <- paste("DQ15_", colnames(daysLate15)[2:ncol(daysLate15)], sep="")

daysLate30 <- melt(daysLate30, id="bigAccountId")
daysLate30 <- daysLate30 %>%
  group_by(bigAccountId) %>%
  arrange(variable, .by_group = TRUE) %>%
  mutate(MaxValue = cummax(value))
daysLate30 <-dcast(data = daysLate30,formula = bigAccountId~variable,fun.aggregate = sum,value.var = "MaxValue")
colnames(daysLate30)[2:ncol(daysLate30)] <- paste("DQ30_", colnames(daysLate30)[2:ncol(daysLate30)], sep="")

daysLate60 <- melt(daysLate60, id="bigAccountId")
daysLate60 <- daysLate60 %>%
  group_by(bigAccountId) %>%
  arrange(variable, .by_group = TRUE) %>%
  mutate(MaxValue = cummax(value))
daysLate60 <-dcast(data = daysLate60,formula = bigAccountId~variable,fun.aggregate = sum,value.var = "MaxValue")
colnames(daysLate60)[2:ncol(daysLate60)] <- paste("DQ60_", colnames(daysLate60)[2:ncol(daysLate60)], sep="")

daysLate90 <- melt(daysLate90, id="bigAccountId")
daysLate90 <- daysLate90 %>%
  group_by(bigAccountId) %>%
  arrange(variable, .by_group = TRUE) %>%
  mutate(MaxValue = cummax(value))
daysLate90 <-dcast(data = daysLate90,formula = bigAccountId~variable,fun.aggregate = sum,value.var = "MaxValue")
colnames(daysLate90)[2:ncol(daysLate90)] <- paste("DQ90_", colnames(daysLate90)[2:ncol(daysLate90)], sep="")


daysLate2 %>%
  select(-bigAccountId) %>%
  summarise_all(mean) %>%
  t() %>%
  plot(type="b")

daysLate2 <- daysLate2 %>%
  left_join(daysLate15, by="bigAccountId") %>%
  left_join(daysLate30, by="bigAccountId") %>%
  left_join(daysLate60, by="bigAccountId") %>%
  left_join(daysLate90, by="bigAccountId")

rm(daysLate15, daysLate30, daysLate60, daysLate90); gc()

id <- rep(default$bigAccountId, 72)
id <- id[order(id)]
defaults <- data.frame(bigAccountId = id, MOB = 1:72)
default1 <- default %>%
  select(bigAccountId, TimeToDefault)
default2 <- default %>%
  select(bigAccountId, TimeToToday)

defaults <- defaults %>%
  left_join(default1, by="bigAccountId") %>%
  left_join(default2, by="bigAccountId")

defaults$bitDefault <- ifelse(defaults$MOB>=defaults$TimeToToday, NA, ifelse(is.na(defaults$TimeToDefault), 0, 
                                                                             ifelse(defaults$MOB>=defaults$TimeToDefault, 1, 0) ))

defaults <- defaults %>%
  select(bigAccountId, MOB, bitDefault)

defaults <-dcast(data = defaults,formula = bigAccountId~MOB,fun.aggregate = sum,value.var = "bitDefault")

colnames(defaults)[2:ncol(defaults)] <- paste("Default_", colnames(defaults)[2:ncol(defaults)], sep="")

targ <- defaults %>%
  left_join(daysLate2, by="bigAccountId")


#write_csv(targ, "GenXIIPerformanceMonitoringTarget.csv")


dataOut <- data %>%
  select(UniqueID, bigAccountId, bigDebtorId, bitDebtor) %>%
  left_join(targ, by="bigAccountId")

write_csv(dataOut, "GenXIIPerformanceMonitoringTarget.csv")


dataOut <- data %>%
  select(UniqueID, bigAccountId, bigDebtorId, bitDebtor, dtmFunded) %>%
  left_join(targ, by="bigAccountId")

library(zoo)

dataOut$YearMon <- as.yearmon(dataOut$dtmFunded)

dataOut1 <- dataOut %>%
  group_by(YearMon) %>%
  summarise(Default_72 = mean(Default_72, na.rm=T),
            DQ1_0 = mean(DQ1_0, na.rm=T),
            DQ1_1 = mean(DQ1_1, na.rm=T),
            DQ1_2 = mean(DQ1_2, na.rm=T),
            DQ1_3 = mean(DQ1_3, na.rm=T),
            DQ1_6 = mean(DQ1_6, na.rm=T),
            DQ1_9 = mean(DQ1_9, na.rm=T),
            DQ1_12 = mean(DQ1_12, na.rm=T),
            DQ1_18 = mean(DQ1_18, na.rm=T),
            DQ1_24 = mean(DQ1_24, na.rm=T),
            DQ1_36 = mean(DQ1_36, na.rm=T),
            DQ1_48 = mean(DQ1_48, na.rm=T),
            
            DQ15_1 = mean(DQ15_1, na.rm=T),
            DQ15_2 = mean(DQ15_2, na.rm=T),
            DQ15_3 = mean(DQ15_3, na.rm=T),
            DQ15_4 = mean(DQ15_4, na.rm=T),
            
            DQ30_0 = mean(DQ30_0, na.rm=T),
            DQ30_3 = mean(DQ30_3, na.rm=T),
            DQ30_6 = mean(DQ30_6, na.rm=T),
            DQ30_9 = mean(DQ30_9, na.rm=T),
            DQ30_12 = mean(DQ30_12, na.rm=T),
            DQ30_18 = mean(DQ30_18, na.rm=T),
            DQ30_24 = mean(DQ30_24, na.rm=T),
            DQ30_36 = mean(DQ30_36, na.rm=T),
            DQ30_48 = mean(DQ30_48, na.rm=T),
            
            DQ60_0 = mean(DQ60_0, na.rm=T),
            DQ60_3 = mean(DQ60_3, na.rm=T),
            DQ60_6 = mean(DQ60_6, na.rm=T),
            DQ60_9 = mean(DQ60_9, na.rm=T),
            DQ60_12 = mean(DQ60_12, na.rm=T),
            DQ60_18 = mean(DQ60_18, na.rm=T),
            DQ60_24 = mean(DQ60_24, na.rm=T),
            DQ60_36 = mean(DQ60_36, na.rm=T),
            DQ60_48 = mean(DQ60_48, na.rm=T),
            
            DQ90_0 = mean(DQ90_0, na.rm=T),
            DQ90_3 = mean(DQ90_3, na.rm=T),
            DQ90_6 = mean(DQ90_6, na.rm=T),
            DQ90_9 = mean(DQ90_9, na.rm=T),
            DQ90_12 = mean(DQ90_12, na.rm=T),
            DQ90_18 = mean(DQ90_18, na.rm=T),
            DQ90_24 = mean(DQ90_24, na.rm=T),
            DQ90_36 = mean(DQ90_36, na.rm=T),
            DQ90_48 = mean(DQ90_48, na.rm=T),
            
            Default_3 = mean(Default_3, na.rm=T),
            Default_6 = mean(Default_6, na.rm=T),
            Default_9 = mean(Default_9, na.rm=T),
            Default_12 = mean(Default_12, na.rm=T),
            Default_18 = mean(Default_18, na.rm=T),
            Default_24 = mean(Default_24, na.rm=T),
            Default_36 = mean(Default_36, na.rm=T))
  
dataOut1 <- subset(dataOut1, !is.na(dataOut1$Default_72))


plot(dataOut1$DQ1_0, dataOut1$Default_72)
plot(dataOut1$DQ1_3, dataOut1$Default_72)
plot(dataOut1$DQ1_6, dataOut1$Default_72)
plot(dataOut1$DQ1_9, dataOut1$Default_72)
plot(dataOut1$DQ1_12, dataOut1$Default_72)
plot(dataOut1$DQ1_18, dataOut1$Default_72)
plot(dataOut1$DQ1_24, dataOut1$Default_72)
plot(dataOut1$DQ1_36, dataOut1$Default_72)

plot(dataOut1$DQ30_0, dataOut1$Default_72)
plot(dataOut1$DQ30_3, dataOut1$Default_72); cor(dataOut1$DQ30_3, dataOut1$Default_72)
plot(dataOut1$DQ30_6, dataOut1$Default_72)
plot(dataOut1$DQ30_9, dataOut1$Default_72)
plot(dataOut1$DQ30_12, dataOut1$Default_72)
plot(dataOut1$DQ30_18, dataOut1$Default_72)
plot(dataOut1$DQ30_24, dataOut1$Default_72)
plot(dataOut1$DQ30_36, dataOut1$Default_72)

plot(dataOut1$DQ60_0, dataOut1$Default_72)
plot(dataOut1$DQ60_3, dataOut1$Default_72)
plot(dataOut1$DQ60_6, dataOut1$Default_72)
plot(dataOut1$DQ60_9, dataOut1$Default_72)
plot(dataOut1$DQ60_12, dataOut1$Default_72)
plot(dataOut1$DQ60_18, dataOut1$Default_72)
plot(dataOut1$DQ60_24, dataOut1$Default_72)
plot(dataOut1$DQ60_36, dataOut1$Default_72)

plot(dataOut1$DQ90_0, dataOut1$Default_72)
plot(dataOut1$DQ90_3, dataOut1$Default_72)
plot(dataOut1$DQ90_6, dataOut1$Default_72)
plot(dataOut1$DQ90_9, dataOut1$Default_72)
plot(dataOut1$DQ90_12, dataOut1$Default_72)
plot(dataOut1$DQ90_18, dataOut1$Default_72)
plot(dataOut1$DQ90_24, dataOut1$Default_72)
plot(dataOut1$DQ90_36, dataOut1$Default_72)


plot(dataOut1$Default_3, dataOut1$Default_72)
plot(dataOut1$Default_6, dataOut1$Default_72)
plot(dataOut1$Default_9, dataOut1$Default_72)
plot(dataOut1$Default_12, dataOut1$Default_72)
plot(dataOut1$Default_18, dataOut1$Default_72)
plot(dataOut1$Default_24, dataOut1$Default_72)
plot(dataOut1$Default_36, dataOut1$Default_72)






cor(dataOut1$DQ1_0, dataOut1$Default_72)
cor(dataOut1$DQ1_3, dataOut1$Default_72)
cor(dataOut1$DQ1_6, dataOut1$Default_72)
cor(dataOut1$DQ1_9, dataOut1$Default_72)
cor(dataOut1$DQ1_12, dataOut1$Default_72)
cor(dataOut1$DQ1_18, dataOut1$Default_72)
cor(dataOut1$DQ1_24, dataOut1$Default_72)
cor(dataOut1$DQ1_36, dataOut1$Default_72)

cor(dataOut1$DQ30_0, dataOut1$Default_72)
cor(dataOut1$DQ30_3, dataOut1$Default_72)
cor(dataOut1$DQ30_6, dataOut1$Default_72)
cor(dataOut1$DQ30_9, dataOut1$Default_72)
cor(dataOut1$DQ30_12, dataOut1$Default_72)
cor(dataOut1$DQ30_18, dataOut1$Default_72)
cor(dataOut1$DQ30_24, dataOut1$Default_72)
cor(dataOut1$DQ30_36, dataOut1$Default_72)

cor(dataOut1$DQ60_0, dataOut1$Default_72)
cor(dataOut1$DQ60_3, dataOut1$Default_72)
cor(dataOut1$DQ60_6, dataOut1$Default_72)
cor(dataOut1$DQ60_9, dataOut1$Default_72)
cor(dataOut1$DQ60_12, dataOut1$Default_72)
cor(dataOut1$DQ60_18, dataOut1$Default_72)
cor(dataOut1$DQ60_24, dataOut1$Default_72)
cor(dataOut1$DQ60_36, dataOut1$Default_72)

cor(dataOut1$DQ90_0, dataOut1$Default_72)
cor(dataOut1$DQ90_3, dataOut1$Default_72)
cor(dataOut1$DQ90_6, dataOut1$Default_72)
cor(dataOut1$DQ90_9, dataOut1$Default_72)
cor(dataOut1$DQ90_12, dataOut1$Default_72)
cor(dataOut1$DQ90_18, dataOut1$Default_72)
cor(dataOut1$DQ90_24, dataOut1$Default_72)
cor(dataOut1$DQ90_36, dataOut1$Default_72)

cor(dataOut1$Default_3, dataOut1$Default_72)
cor(dataOut1$Default_6, dataOut1$Default_72)
cor(dataOut1$Default_9, dataOut1$Default_72)
cor(dataOut1$Default_12, dataOut1$Default_72)
cor(dataOut1$Default_18, dataOut1$Default_72)
cor(dataOut1$Default_24, dataOut1$Default_72)
cor(dataOut1$Default_36, dataOut1$Default_72)




plot(dataOut1$DQ15_1, dataOut1$Default_72); cor(dataOut1$DQ15_1, dataOut1$Default_72)
plot(dataOut1$DQ15_2, dataOut1$Default_72); cor(dataOut1$DQ15_2, dataOut1$Default_72)
plot(dataOut1$DQ15_3, dataOut1$Default_72); cor(dataOut1$DQ15_3, dataOut1$Default_72)
plot(dataOut1$DQ15_4, dataOut1$Default_72); cor(dataOut1$DQ15_4, dataOut1$Default_72)


# test <- read_csv("df_prod_pre_targets.csv")
# 
# 
# test <- test %>%
#   select(bigaccountid__app, bigdebtorid__app, DQ15_1, DQ15_2, DQ15_3, DQ15_4)
# 
# test <- test %>%
#   group_by(bigaccountid__app) %>%
#   summarise(DQ15_1 = mean(DQ15_1),
#             DQ15_2 = mean(DQ15_2),
#             DQ15_3 = mean(DQ15_3),
#             DQ15_4 = mean(DQ15_4))
# 
# write_csv(test, "dqPredsMM.csv")
# 

base::list.files(pattern = '*.csv') |>
  base::file.remove()

daysLate2 |> 
  dplyr::select(bigAccountId, DQ15_2) |>
  readr::write_csv(file = 'daysLate2.csv')
