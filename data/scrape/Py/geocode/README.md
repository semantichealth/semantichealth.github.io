## Scripts to pull Geo Locations

Pulling Geocodes for over a Million providers proved a significant challenge. Most data sources and APIs out there had daily limitation on the number of free Geo pulls and additional pulls were prohibitively expensive at least for the purposes of this project. In the end we were very excited that SmartyStreets (Thank you Jefferson!) offered to support our project by providing an unlimited pull license which we eventually used to pull Geo Locations for over a million plus providers.

The main script attempts to use three APIs to pull Geo Locations in a waterfall like method. Try the first, if not try second and if not then the last one. Eventually those that are return empty are saved separately to re-try at a later time.
* The three Sources we used for Geo Locations are:
 * [SmartyStreets](https://smartystreets.com/docs/us-street-api#http-request-url)
 * [geocder.google](http://geocoder.readthedocs.io/)
 * [geopy Nominatim](https://github.com/geopy/geopy)  

Additional scripts were required to push scraped geocodes to the Provider Collection in MongoDB. To accomplish this we had to match each of the address element for the update query and then insert the geo field.

```json

"addresses" : [
        {
            "city" : "FLEMINGTON",
            "zip" : "08822",
            "phone" : "9087886464",
            "state" : "NJ",
            "address_2" : "SUITE 302",
            "address" : "1100 WESCOTT DRIVE",
            "geo" : [
                40.53208,
                -74.86025
            ]
        }
      ]
```
Given a Plans ID, the associated Provider Name and address geo codes can be easily queried from the Provider Collection in MongoDb and used to show markers in a Map window as nearby provider locations.


**Note**: Summary descriptions are provided as comments inside each script and contains additional details.
