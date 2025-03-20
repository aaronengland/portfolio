with tbl_base as (
    select
		bigAccountId,
		FundingMonth,
		intOpenBKType,
		AmtFinanced,
		BookValue,
		MonthsOnBooks,
		DealerType,
        ROW_NUMBER() OVER (PARTITION BY bigAccountId ORDER BY FundingMonth) AS row_num
    FROM riskdb.analytics.tbltempstaticpool
)
select *
from tbl_base
where row_num = 1;