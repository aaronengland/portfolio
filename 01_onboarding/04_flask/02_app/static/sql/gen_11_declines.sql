with accountsTbl as
(
	SELECT
		account.bigAccountId,
		account.dtmStampCreation,
		account.dtmApproved,
		account.dtmDeclined,
		account.dtmFunded,
		ISNULL(account.bitSystemDecline, 0) AS SystemDecline
	FROM tblAccount account
	WHERE account.dtmStampCreation >= '2024-05-10'
),
gen11scoreCardTbl as
(
	SELECT
			scoreCard.intAccountKey,
			scoreCard.strScoreCardVersion,
			scoreCard.dtmStampCreation,
			scoreCard.fltDebtorScore,
			scoreCard.fltCoDebtorScore,
			scoreCard.fltDebtor_Score_lgd,
			scoreCard.fltCoDebtor_Score_lgd,
			scoreCard.fltDebtor_Score_pd,
			scoreCard.fltCoDebtor_Score_pd,
			scoreCard.strTier AS strTier_gen_11
		FROM edw.pfsedw.dbo.DimScoreCard scoreCard
		INNER JOIN (
			SELECT
				intAccountKey,
				MAX(dtmStampCreation) AS dtmStampCreation
			FROM edw.pfsedw.dbo.DimScoreCard
			WHERE strScoreCardVersion IN ('genxi_v2_3')
				or strScoreCardVersion is null
				--and strScoreCardVersion not in ('genxii_v1')
				--and strScoreCardVersion not in ('genxii_v1_1')
				--and strScoreCardVersion not in ('genxii')
				--and strScoreCardVersion not in ('dlv1')
				--and strScoreCardVersion not in ('dlv1_1')
				and dtmStampCreation >= '2024-05-10'
			GROUP BY intAccountKey
		) latest ON scoreCard.intAccountKey = latest.intAccountKey AND scoreCard.dtmStampCreation = latest.dtmStampCreation
),
gen12scoreCardTbl as
(
	SELECT
			scoreCard.intAccountKey,
			scoreCard.strScoreCardVersion,
			scoreCard.dtmStampCreation,
			scoreCard.fltDebtorScore,
			scoreCard.fltCoDebtorScore,
			scoreCard.fltDebtor_Score_lgd,
			scoreCard.fltCoDebtor_Score_lgd,
			scoreCard.fltDebtor_Score_pd,
			scoreCard.fltCoDebtor_Score_pd,
			scoreCard.strTier AS strTier_gen_11
		FROM edw.pfsedw.dbo.DimScoreCard scoreCard
		INNER JOIN (
			SELECT
				intAccountKey,
				MAX(dtmStampCreation) AS dtmStampCreation
			FROM edw.pfsedw.dbo.DimScoreCard
			WHERE strScoreCardVersion IN ('genxii_v2')
				or strScoreCardVersion is null
				--and strScoreCardVersion not in ('genxii_v1')
				--and strScoreCardVersion not in ('genxii_v1_1')
				--and strScoreCardVersion not in ('genxii')
				--and strScoreCardVersion not in ('dlv1')
				--and strScoreCardVersion not in ('dlv1_1')
				and dtmStampCreation >= '2024-05-10'
			GROUP BY intAccountKey
		) latest ON scoreCard.intAccountKey = latest.intAccountKey AND scoreCard.dtmStampCreation = latest.dtmStampCreation
),
gen11declinesTbl as
(
	SELECT
		accountsTbl.bigAccountId,
		accountsTbl.dtmStampCreation,
		accountsTbl.dtmApproved,
		accountsTbl.dtmDeclined,
		accountsTbl.dtmFunded,
		accountsTbl.SystemDecline,
		scoreCardTbl.strScoreCardVersion,
		scoreCardTbl.fltDebtorScore,
		scoreCardTbl.fltCoDebtorScore,
		scoreCardTbl.strTier_gen_11
	from accountsTbl left join gen12scoreCardTbl on accountsTbl.bigAccountId = gen12scoreCardTbl.intAccountKey
)
