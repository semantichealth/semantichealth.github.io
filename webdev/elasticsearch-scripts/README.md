# Elasticsearch Scripts

### Proposed Mapping for Plans
(each Document is a plan)

| Attribute | Source | Mapping | Preprocessing |
|-----------|--------|---------|---------------|
| PlanId | 1 | use as _id | none |
| Plan Name | 1 | string-analyzed | none |
| Issuer | 1 | string-analyzed, raw-string-not_analyzed | none |
| State  | 1 | string-not_analyzed | none |
| Plan Type | 1 | string-analyzed, raw-string-not_analyzed | none |
| Metal Level | 1 | string-analyzed, raw-string-not_analyzed | none |
| Plan Brochure URL  | 1 | string-no_index | none |
| Drugs Covered | 4 | string-analyzed | Array format
| Providers | 5 | nested (below) | could be an array of names to avoid nested mapping |
| Medical Conditions | 6 | string-analyzed, raw-string-not_analyzed | Array format; plan that covers 80% of drugs? |
| Logo URL  | 7 | string-no_index | none |
| Premiums_median | 8 | float | none |
| Premiums_q1 | 8 | float-no_index | none |
| Premiums_q3 | 8 | float-no_index | none |
| Plan Ranks | 9 | float | each component gets a field; use zero-indexing; Lei provide max number of components? |

#### Providers Nested Attributes
| Attribute | Source | Mapping | Preprocessing |
|-----------|--------|---------|---------------|
| Full name | 5 | string-analyzed | combine first/last name |
| Specialties | 5 | string-analyzed | array |
| NPI | 5 | string-no_index | none |

#### Sources
1. plan-attributes-puf.csv
2. benefits-and-cost-sharing-puf.csv
3. Rate_PUF.csv
4. Drugs (JSON)
5. Providers (JSON)
6. Medical condition - drugs map
7. issuers_logos.csv
8. premiums_aggregated.csv
9. letor data from Lei

#### Sample Mapping

    {
      "plans_v2" : {
        "mappings" : {
          "plan" : {
            "properties" : {
              "conditions" : {
                "type" : "string",
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed"
                  }
                }
              },
              "drugs" : {
                "type" : "string",              
                "analyzer" : "simpleAnalyzer"
              },
              "issuer" : {
                "type" : "string",
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed"
                  }
                }
              },
              "level" : {
                "type" : "string",
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed"
                  }
                }
              },
              "logo_url" : {
                "type" : "string",
                "index" : "no"
              },
              "plan_name" : {
                "type" : "string"
              },
              "plan_rank_0" : {
                "type" : "float"
              },
              "plan_rank_1" : {
                "type" : "float"
              },              
              "plan_rank_2" : {
                "type" : "float"
              },
              "plan_rank_3" : {
                "type" : "float"
              },
              "plan_rank_4" : {
                "type" : "float"
              },
              "plan_rank_5" : {
                "type" : "float"
              },
              "plan_rank_6" : {
                "type" : "float"
              },
              "plan_rank_7" : {
                "type" : "float"
              },
              "plan_rank_8" : {
                "type" : "float"
              },
              "plan_rank_9" : {
                "type" : "float"
              },
              "plan_type" : {
                "type" : "string",
                "fields" : {
                  "raw" : {
                    "type" : "string",
                    "index" : "not_analyzed"
                  }
                }
              },
              "premiums_median" : {
                "type" : "float"
              },
              "premiums_q1" : {
                "type" : "float",
                "index" : "no"
              },
              "premiums_q3" : {
                "type" : "float",
                "index" : "no"
              },
              "providers" : {
                "type" : "nested",
                "properties" : {
                  "npi" : {
                    "type" : "string",
                    "index" : "no"
                  },
                  "provider_name" : {
                    "type" : "string",
                    "analyzer" : "simpleAnalyzer"
                  },
                  "specialities" : {
                    "type" : "string",
                    "analyzer" : "simpleAnalyzer"
                  }                  
                }
              },
              "state" : {
                "type" : "string",
                "index" : "not_analyzed"
              },
              "url" : {
                "type" : "string",
                "index" : "no"
              }
            }
          }
        }
      }
    }
