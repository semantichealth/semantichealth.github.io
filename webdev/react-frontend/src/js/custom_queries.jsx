import $ from "jquery";

export const inputQuery = (query, options) => {
	let input_query = {
		"nested": {
	      "path": options.path,
	      "query": {
	        "match": {}
	      },
	      "inner_hits": {
					"name": options.subfield,
          "from": 0,
          "size": 5
	      }
		}
	}
	input_query["nested"]["query"]["match"][options.path + "." + options.subfield] = query
	return input_query
}

export const generateRescore = (query_weights) => {
	const rescore_function_array = $.map(query_weights,
		function(weight, i) {
			return {
				"field_value_factor": {
					"field": "plan_rank_" + (i).toString(),
					"factor": weight,
					"missing": 0
				}
			}
		}
	)
	const rescore_query = {
		 "window_size" : 1000,
		 "query" : {
			"score_mode": "total",
			"rescore_query" : {
				"function_score": {
					 "score_mode": "sum",
					 "functions": rescore_function_array
				}
			}
		}
	}
	return rescore_query
}
