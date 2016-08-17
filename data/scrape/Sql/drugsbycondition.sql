
--@author:  Tigi Thomas
--@project: MIDS W210 Capstone - ACA Semantic Search
--@module:  drugsbycondition.sql
--@desc :   collection of sql scripts to store drugs.com data in 
--          mysql database and to jon with Rxnorm data to 
--			match diseases to drugs and rxNormid. 
--			match is not perfect but should cover most cases sufficient for project



-- Create Mysql database to host drugs.com dat

# database
use prescribe

#create table drugsbycondition
drop table drugsbycondition
create table drugsbycondition 
(
	Id int not null AUTO_INCREMENT, 
	condition_name varchar(128),
	drug_name varchar(128),
	brand_name varchar(512),
	alcohol  varchar(5),
	pregnancy varchar(5),
	csasched varchar(5),
	rating int,
	rxtype varchar(10),
	popularityscore int,
	drug_generalinfo varchar(2000),
	primary key (Id)
);

# create all indexes.
create unique index uci_drugsbycondition_Id_drugname on drugsbycondition( Id, drug_name);
create index uci_drugsbycondition_drugname on drugsbycondition( drug_name);
create index uci_drugsbycondition_condition on drugsbycondition(condition_name);
create index ui_drugsbycondition_brandname on drugsbycondition(brand_name);
create index ui_drugsbycondition_drg2 on drugsbycondition(drug_name2_like);

truncate table drugsbycondition
GRANT ALL PRIVILEGES ON prescribe.drugsbycondition TO 'user'@'localhost' 



-- create indexes on the RXNORM databases. 
-- See sql scripts for RXNCONSO

create index idx_RXNCONSO_RXCUI on RXNCONSO( RXCUI);
create index idx_RXNCONSO_STR on RXNCONSO( STR);
create index idx_RXNCONSO_drug_name on RXNCONSO( drug_name);



select count(*) from prescribe.drugsbycondition;
select count(*) from prescribe.RXNCONSO where SAB = 'RXNORM'; --132,223
select count(*) from prescribe.RXNCONSO where SAB = 'RXNORM' and TTY = 'PSN'; 
select count(distinct(RXCUI)) from prescribe.RXNCONSO where SAB = 'RXNORM'; --132,223


-- creating different version of the drug names to improve join...
alter table drugsbycondition add column drug_name1 varchar(100)

update prescribe.drugsbycondition
	set drug_name1 = SUBSTRING_INDEX(TRIM(drug_name),' ', 1)

alter table drugsbycondition add column drug_name1_like varchar(120)

update prescribe.drugsbycondition
	set drug_name1_like =  CONCAT("%", drug_name1, "%")
	
alter table drugsbycondition add column drug_name2_like varchar(256)
alter table drugsbycondition drop column drug_name2_like
update prescribe.drugsbycondition
	set drug_name2_like =  CONCAT(lower(trim(drug_name)), "%")

	
alter table RXNCONSO add column drug_name varchar(128)
update RXNCONSO
set drug_name = substring(lower(TRIM(STR)), 1, 128)
	
	
# create some views.. 

alter view prescribe.export_drugsbycondition
as
select 
	condition_name, 
	drug_name, 
	brand_name
from prescribe.drugsbycondition;

select * from  export_drugsbycondition;

alter view prescribe.export_rxnconso
as 
select 
	RxNormId = convert(RXCUI, bigint),
	RxNormId2 = convert(RXAUI, bigint),
	drug_name = STR
from prescribe.RXNCONSO
where SAB = 'RXNORM';

alter view prescribe.rxnormbycondition
as 
select distinct 
	condition_name as disease, 
	c.RXCUI as RxNormId
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where dc.drug_name like c.STR
order by condition_name asc, c.RXCUI

CREATE TABLE prescribe.rxnorm_bycondition SELECT * FROM prescribe.rxnormbycondition;

drop table prescribe.rxnorm_bycondition
CREATE TABLE prescribe.rxnorm_bycondition
select distinct 
	dc.condition_name as disease, 
	dc.drug_name as ddc_drug_name,
	c.STR as rxn_drug_name,
	c.RXCUI as RxNormId
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where c.STR like dc.drug_name1_like 
order by condition_name asc, c.RXCUI

drop table prescribe.rxnorm_bycondition2
CREATE TABLE prescribe.rxnorm_bycondition2
select distinct 
	dc.condition_name as disease, 
	dc.drug_name as ddc_drug_name,
	c.STR as rxn_drug_name,
	c.RXCUI,
	c.SCUI
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where dc.drug_name like concat("%", c.STR, "%") 
order by condition_name asc, c.RXCUI


-- ****************************************************************
-- Finally use this table to extract data and create json file..
-- ****************************************************************
drop table prescribe.rxnorm_bycondition3;
CREATE TABLE prescribe.rxnorm_bycondition3
select distinct 
	dc.condition_name as disease, 
	dc.drug_name as ddc_drug_name,
	c.drug_name as rxn_drug_name,
	c.RXCUI as RxNormId
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where c.drug_name like dc.drug_name2_like
order by condition_name asc, c.RXCUI;

drop table prescribe.rxnorm_condition_vector;
create table prescribe.rxnorm_condition_vector
select 
	RxNormId as rxnormid, 
	disease, 
	count(*) as diseasecount
from prescribe.rxnorm_bycondition3
group by RxNormId, disease
order by 1;

# Sample data checks....... 

SELECT SUBSTRING_INDEX(TRIM(drug_name),' ', 1), drug_name from prescribe.drugsbycondition;


select * from prescribe.RXNCONSO where SAB = 'RXNORM' ;
select * from prescribe.RXNCONSO where SAB = 'RXNORM' and TTY = 'PSN';

select distinct dc.*, c.RXCUI, c.STR
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where dc.drug_name like c.STR;

select distinct 
condition_name as disease, 
c.RXCUI as RxNormId
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where dc.drug_name like c.STR
order by 1,2

select count(*)
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where dc.drug_name like c.STR;

1648780 Juxtapid 60 mg capsule
1648776 Juxtapid 40 mg capsule
1648772 Juxtapid 30 mg capsule

select * from prescribe.RXNCONSO 
where SAB = 'RXNORM'
and TTY = 'PSN'
and STR like '%Juxtapid%'
-- -------------------------------------------------------------
-- use RXCUI



select count(*) from prescribe.rxnorm_bycondition
select * from  prescribe.rxnorm_bycondition where rxn_drug_name = 'imipramine'
select * from  prescribe.rxnorm_bycondition2 where rxn_drug_name = 'imipramine'
select * from  prescribe.rxnorm_bycondition3 where rxn_drug_name like 'imipramine%'

select * from  prescribe.rxnorm_bycondition3 where rxn_drug_name like 'chromium picolinate%'

update prescribe.rxnorm_bycondition3
 set disease = replace(disease, '\n', ' ')


select count(*) from prescribe.rxnorm_bycondition3 where rxn_drug_name like 'imipramine%'


select * from prescribe.drugsbycondition where drug_name = 'imipramine'

select * from prescribe.drugsbycondition where drug_name = 'OFLOXACIN'
select * from prescribe.RXNCONSO where STR like '%Otic%'
OFLOXACIN 3 mg in 1 mL AURICULAR (OTIC) SOLUTION

select * from  prescribe.RXNCONSO where lower(STR) like 'imipramine%'
select * from  prescribe.RXNCONSO where RXCUI = 835564

select count(distinct(disease)) from  prescribe.rxnorm_bycondition

select distinct dc.*, c.RXCUI, c.STR
from prescribe.drugsbycondition dc, prescribe.RXNCONSO c
where dc.drug_name like c.STR;
