# !/usr/bin/python
from __future__ import division
import math


'''  
Household Size 	FPL 2013-2014    2014-2015 	2015-2016
1 	           $11,490 	     11,670 	11,770
2 	           $15,510 	     15,730 	15,930
3 	           $19,530 	     19,790 	20,090
4 	           $23,550 	     23,850 	24,250

Income as  	     Cap %  	   Cap % 
% of FPL        (Lower End)    (Higher End)
-----------     -----------    ------------
Up to 133%  	0.0% 	         2.0%
133% - 150% 	3.0% 	         4.0%
150% - 200% 	4.0% 	         6.3%
200% - 250% 	6.3% 	         8.05%
250% - 300% 	8.05%          9.5%
300% - 400% 	9.5% 	         9.5%
'''

# Income levels and FPL Cap Range Mappings
FPL2016   =    [0.1, 11770, 15930, 20090, 24250]
PctFplRange =  [(0.0, 1.33), (1.34,  1.5), (1.5,    2.0), (2.0,      2.5), (2.5,      3.0), (3.0,     4.0)]
PremCapRange = [(0.0, 0.02), (0.03, 0.04), (0.04, 0.063), (0.063, 0.0805), (0.0805, 0.095), (0.095, 0.095)]
   
# Calculate Subsidy based on 
# Modified Adjusted Gross Income (MAGI) and Household Size.
def CalcAcaSubsidy(magi, householdcount, debug=False):       
    IncomeAsPctOfFPL = round(magi / float(FPL2016[householdcount]),2)
    #print FPL2016[householdcount], IncomeAsPctOfFPLPct
    for (minfpl, maxfpl), (mincap, maxcap) in zip(PctFplRange,PremCapRange):
        if debug:
            print minfpl, maxfpl, mincap, maxcap
        if minfpl <= IncomeAsPctOfFPL <= maxfpl:
            # just simple split by the middle and chose one of the caps
            cap = mincap if (IncomeAsPctOfFPL < (minfpl+maxfpl)/2) else maxcap       
            yrpremcap = round(cap * magi,0)
            monthpremcap =round(yrpremcap/12,0)
            if debug:
                print 'Income = %d, ' \
                      'Number of Household = %d, ' \
                      'YearlyPremiumCap = %d, ' \
                      'MonthlyPremimCap = %d'%(magi,householdcount,yrpremcap,monthpremcap ) 
            return yrpremcap, monthpremcap

''' 
------------------------------------------------------------------------------
Test http://www.valuepenguin.com/understanding-aca-subsidies (see 2 examples)
------------------------------------------------------------------------------
''' 
# http://www.valuepenguin.com/understanding-aca-subsidies (see 2 examples)
YearlyPremiumCap, MonthlyPremimCap = CalcAcaSubsidy(28725, 1) 
YearlyPremiumCap, MonthlyPremimCap = CalcAcaSubsidy(47100, 4)   

# To Calculate Max Subsidy, use the Benchmark Plan Premium, 
# Benchmark  -> The Second Cheapest Silver Plan for that state.
# for eg. if the second cheapest plan costs 300 per month
SecondCheapestSilverPlanPremium = 300
MaxSubsidy = SecondCheapestSilverPlanPremium - MonthlyPremimCap

