# Feature Extraction

## Feature Description
### Coverage flag:
- Plan: formulary tier type
- Drug: 0/1 indicator for all drugs
- Provider: 0/1 indicator for all providers

### Summary statistics:
- Plan: average of copay and coinsurance
- Drug: count of coverage type
- Provider: count of coverage type

## File Description
Name|Function
---|---
**main.py** | main procedure to execute feature Extraction
**get_state_feature.py** | extract and assemble feature vectors for plans in one state
**query_plan_feature.py** | MongoDB pipeline to process plan collection
**query_drug_feature.py** | MongoDB pipeline to process formulary collection
**query_provider_feature.py** | MongoDB pipeline to process provider collection
**extract_plan_feature.py** | assemble features for plan data
**extract_drug_feature.py** | assemble features for formulary data
**extract_provider_feature.py** | assemble features for provider data
**logger.py** | record steps and states during the process
**s3_helpers.py** | upload feature pickle file to AWS S3
**dev.ipynb** | unit test

## Deployment
- specify the S3 folder name to store the feature pickle in _main.py_
- execute main on background: `python main.py &`
