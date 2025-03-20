with tblBase as
(
select
    tblAccount.bigAccountId,
    tblAccount.bigDebtorId,
    1 as bitDebtor
from tblAccount
where dtmStampCreation >= '01/01/2021'

union
select
    tblAccount.bigAccountId,
    tblCosigner.bigDebtorId_cosigner as bigDebtorId,
    0 as bitDebtor
from tblAccount
left outer join tblCosigner on tblCosigner.bigAccountId=tblAccount.bigAccountId
where dtmStampCreation >= '01/01/2021'
and tblCosigner.bigDebtorId_cosigner is not null
)

select 
    tblBase.*,
    tblDebtor.strNameFirst,
    tblDebtor.strNameLast,
    tblDebtor.dtmBirthday,
    tblAddress.strZipCode,
    tblDebtor.dtmStampCreation
from tblBase
left outer join 
(
    select
        bigDebtorId,
        min(bigAddressId) as bigAddressId
    from tblAddress
    group by bigDebtorId
)tblMin on tblMin.bigDebtorId=tblBase.bigDebtorId
left join tblAddress on tblAddress.bigAddressId = tblMin.bigAddressId
left outer join tblDebtor on tblDebtor.bigDebtorId=tblBase.bigDebtorId