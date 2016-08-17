# SQL Scripts

**RxNormScripts**: 
Contains Scripts to import RxNorm data as Comma delimitted files. [Full set of downloadable files can be found here]( https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html)

**drugsbycondition.sql**:
Collection of sql scripts (tables/views) to store drugs.com data in a mysql database. The idea is to be able to join Rxnorm and Drugs.com data to match diseases to drugs via rxNormid. Match is not perfect but should cover most cases sufficient for project.