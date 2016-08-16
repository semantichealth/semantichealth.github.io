# PostgreSQL

The files in this directory are DDL extractions or SQL code used to test queries.

| File | Description
| ---- | -----------
| plan_rate_aggregation.sql | loads the contents of the premiums_aggregated.csv file into the database
| populate_logo_url_col.sql | updates the `plan_attributes` table from the `HIOS_ISSUER and` `logos` tables
| issuers_logos.csv | CSV file of insurer logos by state and insurer HIOS identity
| public_schema.sql | extracted DDL of the `public` schema of the PostgreSQL database
| https://s3-us-west-1.amazonaws.com/w210/pg_dump.dmp | Backup of PostgreSQL database

