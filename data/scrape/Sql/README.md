# SQL Scripts

**RxNormScripts**:
Contains Scripts to import RxNorm data as Comma delimitted files. [Full set of downloadable files can be found here]( https://www.nlm.nih.gov/research/umls/rxnorm/docs/rxnormfiles.html)

**drugsbycondition.sql**:
Collection of sql scripts (tables/views) to store drugs.com data in a mysql database. The idea is to be able to join [RxNorm](https://www.nlm.nih.gov/research/umls/rxnorm/overview.html) and [Drugs.com](https://www.drugs.com/medical_conditions.html) data to match diseases to drugs via RxNormid. Match is not perfect but should cover most cases sufficient for project.
