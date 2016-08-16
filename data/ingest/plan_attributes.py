
import csv
import psycopg2

"""

    This Python program uses the Plan Attributes.csv file from the CMS.gov site to extract the insurance
    plan coverage details for each plan. The code reads the CSV file and uploads it to a PostgreSQL
    database table with the same structure.

"""


# get a connection to the database
def connect_db():
    conn = psycopg2.connect(user="acaproject",
                            database="acaproject",
                            password="test1234",
                            host="w210.cxihwctrc5di.us-west-1.rds.amazonaws.com",
                            port="5432")
    return conn

db_conn = connect_db()
cur = db_conn.cursor()


rates = []
count = 0
with open("plan-attributes-puf.csv", "r") as puf:
    attr_gen = csv.DictReader(puf)
    line = 0
    for attr in attr_gen:

        cur.execute("INSERT INTO plan_attributes ("
                    "BusinessYear, StateCode, IssuerId, SourceName, VersionNum, ImportDate,"
                    "BenefitPackageId, IssuerId2, StateCode2, MarketCoverage, DentalOnlyPlan,"
                    "TIN, StandardComponentId, PlanMarketingName, HIOSProductId, HPID,"
                    "NetworkId, ServiceAreaId, FormularyId, IsNewPlan, PlanType, MetalLevel,"
                    "UniquePlanDesign, QHPNonQHPTypeId, IsNoticeRequiredForPregnancy,"
                    "IsReferralRequiredForSpecialist, SpecialistRequiringReferral,"
                    "PlanLevelExclusions, IndianPlanVariationEstimatedAdvancedPaymentAmountPerEnrollee,"
                    "CompositeRatingOffered, ChildOnlyOffering, ChildOnlyPlanId,"
                    "WellnessProgramOffered, DiseaseManagementProgramsOffered,"
                    "EHBPercentTotalPremium, EHBPediatricDentalApportionmentQuantity,"
                    "IsGuaranteedRate, SpecialtyDrugMaximumCoinsurance,"
                    "InpatientCopaymentMaximumDays, BeginPrimaryCareCostSharingAfterNumberOfVisits,"
                    "BeginPrimaryCareDeductibleCoinsuranceAfterNumberOfCopays, PlanEffictiveDate,"
                    "PlanExpirationDate, OutOfCountryCoverage, OutOfCountryCoverageDescription,"
                    "OutOfServiceAreaCoverage, OutOfServiceAreaCoverageDescription,"
                    "NationalNetwork, URLForEnrollmentPayment, FormularyURL, PlanId,"
                    "CSRVariationType, IssuerActuarialValue, AVCalculatorOutputNumber,"
                    "MedicalDrugDeductiblesIntegrated, MedicalDrugMaximumOutofPocketIntegrated,"
                    "MultipleInNetworkTiers, FirstTierUtilization, SecondTierUtilization,"
                    "SBCHavingaBabyDeductible, SBCHavingaBabyCopayment, SBCHavingaBabyCoinsurance,"
                    "SBCHavingaBabyLimit, SBCHavingDiabetesDeductible, SBCHavingDiabetesCopayment,"
                    "SBCHavingDiabetesCoinsurance, SBCHavingDiabetesLimit, MEHBInnTier1IndividualMOOP,"
                    "MEHBInnTier1FamilyPerPersonMOOP, MEHBInnTier1FamilyPerGroupMOOP,"
                    "MEHBInnTier2IndividualMOOP, MEHBInnTier2FamilyPerPersonMOOP,"
                    "MEHBInnTier2FamilyPerGroupMOOP, MEHBOutOfNetIndividualMOOP,"
                    "MEHBOutOfNetFamilyPerPersonMOOP, MEHBOutOfNetFamilyPerGroupMOOP,"
                    "MEHBCombInnOonIndividualMOOP, MEHBCombInnOonFamilyPerPersonMOOP,"
                    "MEHBCombInnOonFamilyPerGroupMOOP, DEHBInnTier1IndividualMOOP,"
                    "DEHBInnTier1FamilyPerPersonMOOP, DEHBInnTier1FamilyPerGroupMOOP,"
                    "DEHBInnTier2IndividualMOOP, DEHBInnTier2FamilyPerPersonMOOP,"
                    "DEHBInnTier2FamilyPerGroupMOOP, DEHBOutOfNetIndividualMOOP,"
                    "DEHBOutOfNetFamilyPerPersonMOOP, DEHBOutOfNetFamilyPerGroupMOOP,"
                    "DEHBCombInnOonIndividualMOOP, DEHBCombInnOonFamilyPerPersonMOOP,"
                    "DEHBCombInnOonFamilyPerGroupMOOP, TEHBInnTier1IndividualMOOP,"
                    "TEHBInnTier1FamilyPerPersonMOOP, TEHBInnTier1FamilyPerGroupMOOP,"
                    "TEHBInnTier2IndividualMOOP, TEHBInnTier2FamilyPerPersonMOOP,"
                    "TEHBInnTier2FamilyPerGroupMOOP, TEHBOutOfNetIndividualMOOP,"
                    "TEHBOutOfNetFamilyPerPersonMOOP, TEHBOutOfNetFamilyPerGroupMOOP,"
                    "TEHBCombInnOonIndividualMOOP, TEHBCombInnOonFamilyPerPersonMOOP,"
                    "TEHBCombInnOonFamilyPerGroupMOOP, MEHBDedInnTier1Individual,"
                    "MEHBDedInnTier1FamilyPerPerson, MEHBDedInnTier1FamilyPerGroup,"
                    "MEHBDedInnTier1Coinsurance, MEHBDedInnTier2Individual,"
                    "MEHBDedInnTier2FamilyPerPerson, MEHBDedInnTier2FamilyPerGroup,"
                    "MEHBDedInnTier2Coinsurance, MEHBDedOutOfNetIndividual,"
                    "MEHBDedOutOfNetFamilyPerPerson, MEHBDedOutOfNetFamilyPerGroup,"
                    "MEHBDedCombInnOonIndividual, MEHBDedCombInnOonFamilyPerPerson,"
                    "MEHBDedCombInnOonFamilyPerGroup, DEHBDedInnTier1Individual,"
                    "DEHBDedInnTier1FamilyPerPerson, DEHBDedInnTier1FamilyPerGroup,"
                    "DEHBDedInnTier1Coinsurance, DEHBDedInnTier2Individual,"
                    "DEHBDedInnTier2FamilyPerPerson, DEHBDedInnTier2FamilyPerGroup,"
                    "DEHBDedInnTier2Coinsurance, DEHBDedOutOfNetIndividual,"
                    "DEHBDedOutOfNetFamilyPerPerson, DEHBDedOutOfNetFamilyPerGroup,"
                    "DEHBDedCombInnOonIndividual, DEHBDedCombInnOonFamilyPerPerson,"
                    "DEHBDedCombInnOonFamilyPerGroup, TEHBDedInnTier1Individual,"
                    "TEHBDedInnTier1FamilyPerPerson, TEHBDedInnTier1FamilyPerGroup,"
                    "TEHBDedInnTier1Coinsurance, TEHBDedInnTier2Individual,"
                    "TEHBDedInnTier2FamilyPerPerson, TEHBDedInnTier2FamilyPerGroup,"
                    "TEHBDedInnTier2Coinsurance, TEHBDedOutOfNetIndividual,"
                    "TEHBDedOutOfNetFamilyPerPerson, TEHBDedOutOfNetFamilyPerGroup,"
                    "TEHBDedCombInnOonIndividual, TEHBDedCombInnOonFamilyPerPerson,"
                    "TEHBDedCombInnOonFamilyPerGroup, IsHSAEligible, HSAOrHRAEmployerContribution,"
                    "HSAOrHRAEmployerContributionAmount, URLForSummaryofBenefitsCoverage,"
                    "PlanBrochure, RowNumber) "
                    "VALUES ( "
                    "%(BusinessYear)s, %(StateCode)s, %(IssuerId)s, %(SourceName)s, %(VersionNum)s, %(ImportDate)s,"
                    "%(BenefitPackageId)s, %(IssuerId2)s, %(StateCode2)s, %(MarketCoverage)s, %(DentalOnlyPlan)s,"
                    "%(TIN)s, %(StandardComponentId)s, %(PlanMarketingName)s, %(HIOSProductId)s, %(HPID)s,"
                    "%(NetworkId)s, %(ServiceAreaId)s, %(FormularyId)s, %(IsNewPlan)s, %(PlanType)s, %(MetalLevel)s,"
                    "%(UniquePlanDesign)s, %(QHPNonQHPTypeId)s, %(IsNoticeRequiredForPregnancy)s,"
                    "%(IsReferralRequiredForSpecialist)s, %(SpecialistRequiringReferral)s,"
                    "%(PlanLevelExclusions)s, %(IndianPlanVariationEstimatedAdvancedPaymentAmountPerEnrollee)s,"
                    "%(CompositeRatingOffered)s, %(ChildOnlyOffering)s, %(ChildOnlyPlanId)s,"
                    "%(WellnessProgramOffered)s, %(DiseaseManagementProgramsOffered)s,"
                    "%(EHBPercentTotalPremium)s, %(EHBPediatricDentalApportionmentQuantity)s,"
                    "%(IsGuaranteedRate)s, %(SpecialtyDrugMaximumCoinsurance)s,"
                    "%(InpatientCopaymentMaximumDays)s, %(BeginPrimaryCareCostSharingAfterNumberOfVisits)s,"
                    "%(BeginPrimaryCareDeductibleCoinsuranceAfterNumberOfCopays)s, %(PlanEffictiveDate)s,"
                    "%(PlanExpirationDate)s, %(OutOfCountryCoverage)s, %(OutOfCountryCoverageDescription)s,"
                    "%(OutOfServiceAreaCoverage)s, %(OutOfServiceAreaCoverageDescription)s,"
                    "%(NationalNetwork)s, %(URLForEnrollmentPayment)s, %(FormularyURL)s, %(PlanId)s,"
                    "%(CSRVariationType)s, %(IssuerActuarialValue)s, %(AVCalculatorOutputNumber)s,"
                    "%(MedicalDrugDeductiblesIntegrated)s, %(MedicalDrugMaximumOutofPocketIntegrated)s,"
                    "%(MultipleInNetworkTiers)s, %(FirstTierUtilization)s, %(SecondTierUtilization)s,"
                    "%(SBCHavingaBabyDeductible)s, %(SBCHavingaBabyCopayment)s, %(SBCHavingaBabyCoinsurance)s,"
                    "%(SBCHavingaBabyLimit)s, %(SBCHavingDiabetesDeductible)s, %(SBCHavingDiabetesCopayment)s,"
                    "%(SBCHavingDiabetesCoinsurance)s, %(SBCHavingDiabetesLimit)s, %(MEHBInnTier1IndividualMOOP)s,"
                    "%(MEHBInnTier1FamilyPerPersonMOOP)s, %(MEHBInnTier1FamilyPerGroupMOOP)s,"
                    "%(MEHBInnTier2IndividualMOOP)s, %(MEHBInnTier2FamilyPerPersonMOOP)s,"
                    "%(MEHBInnTier2FamilyPerGroupMOOP)s, %(MEHBOutOfNetIndividualMOOP)s,"
                    "%(MEHBOutOfNetFamilyPerPersonMOOP)s, %(MEHBOutOfNetFamilyPerGroupMOOP)s,"
                    "%(MEHBCombInnOonIndividualMOOP)s, %(MEHBCombInnOonFamilyPerPersonMOOP)s,"
                    "%(MEHBCombInnOonFamilyPerGroupMOOP)s, %(DEHBInnTier1IndividualMOOP)s,"
                    "%(DEHBInnTier1FamilyPerPersonMOOP)s, %(DEHBInnTier1FamilyPerGroupMOOP)s,"
                    "%(DEHBInnTier2IndividualMOOP)s, %(DEHBInnTier2FamilyPerPersonMOOP)s,"
                    "%(DEHBInnTier2FamilyPerGroupMOOP)s, %(DEHBOutOfNetIndividualMOOP)s,"
                    "%(DEHBOutOfNetFamilyPerPersonMOOP)s, %(DEHBOutOfNetFamilyPerGroupMOOP)s,"
                    "%(DEHBCombInnOonIndividualMOOP)s, %(DEHBCombInnOonFamilyPerPersonMOOP)s,"
                    "%(DEHBCombInnOonFamilyPerGroupMOOP)s, %(TEHBInnTier1IndividualMOOP)s,"
                    "%(TEHBInnTier1FamilyPerPersonMOOP)s, %(TEHBInnTier1FamilyPerGroupMOOP)s,"
                    "%(TEHBInnTier2IndividualMOOP)s, %(TEHBInnTier2FamilyPerPersonMOOP)s,"
                    "%(TEHBInnTier2FamilyPerGroupMOOP)s, %(TEHBOutOfNetIndividualMOOP)s,"
                    "%(TEHBOutOfNetFamilyPerPersonMOOP)s, %(TEHBOutOfNetFamilyPerGroupMOOP)s,"
                    "%(TEHBCombInnOonIndividualMOOP)s, %(TEHBCombInnOonFamilyPerPersonMOOP)s,"
                    "%(TEHBCombInnOonFamilyPerGroupMOOP)s, %(MEHBDedInnTier1Individual)s,"
                    "%(MEHBDedInnTier1FamilyPerPerson)s, %(MEHBDedInnTier1FamilyPerGroup)s,"
                    "%(MEHBDedInnTier1Coinsurance)s, %(MEHBDedInnTier2Individual)s,"
                    "%(MEHBDedInnTier2FamilyPerPerson)s, %(MEHBDedInnTier2FamilyPerGroup)s,"
                    "%(MEHBDedInnTier2Coinsurance)s, %(MEHBDedOutOfNetIndividual)s,"
                    "%(MEHBDedOutOfNetFamilyPerPerson)s, %(MEHBDedOutOfNetFamilyPerGroup)s,"
                    "%(MEHBDedCombInnOonIndividual)s, %(MEHBDedCombInnOonFamilyPerPerson)s,"
                    "%(MEHBDedCombInnOonFamilyPerGroup)s, %(DEHBDedInnTier1Individual)s,"
                    "%(DEHBDedInnTier1FamilyPerPerson)s, %(DEHBDedInnTier1FamilyPerGroup)s,"
                    "%(DEHBDedInnTier1Coinsurance)s, %(DEHBDedInnTier2Individual)s,"
                    "%(DEHBDedInnTier2FamilyPerPerson)s, %(DEHBDedInnTier2FamilyPerGroup)s,"
                    "%(DEHBDedInnTier2Coinsurance)s, %(DEHBDedOutOfNetIndividual)s,"
                    "%(DEHBDedOutOfNetFamilyPerPerson)s, %(DEHBDedOutOfNetFamilyPerGroup)s,"
                    "%(DEHBDedCombInnOonIndividual)s, %(DEHBDedCombInnOonFamilyPerPerson)s,"
                    "%(DEHBDedCombInnOonFamilyPerGroup)s, %(TEHBDedInnTier1Individual)s,"
                    "%(TEHBDedInnTier1FamilyPerPerson)s, %(TEHBDedInnTier1FamilyPerGroup)s,"
                    "%(TEHBDedInnTier1Coinsurance)s, %(TEHBDedInnTier2Individual)s,"
                    "%(TEHBDedInnTier2FamilyPerPerson)s, %(TEHBDedInnTier2FamilyPerGroup)s,"
                    "%(TEHBDedInnTier2Coinsurance)s, %(TEHBDedOutOfNetIndividual)s,"
                    "%(TEHBDedOutOfNetFamilyPerPerson)s, %(TEHBDedOutOfNetFamilyPerGroup)s,"
                    "%(TEHBDedCombInnOonIndividual)s, %(TEHBDedCombInnOonFamilyPerPerson)s,"
                    "%(TEHBDedCombInnOonFamilyPerGroup)s, %(IsHSAEligible)s, %(HSAOrHRAEmployerContribution)s,"
                    "%(HSAOrHRAEmployerContributionAmount)s, %(URLForSummaryofBenefitsCoverage)s,"
                    "%(PlanBrochure)s, %(RowNumber)s)",
                    attr)
        line += 1
        db_conn.commit()
    print "{0} entries processed...".format(line)
    cur.close()
    db_conn.close()
