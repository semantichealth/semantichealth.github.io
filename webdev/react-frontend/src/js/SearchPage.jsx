import * as React from "react";
import * as _ from "lodash";
import $ from "jquery";

import {
	SearchkitManager, SearchkitProvider,
	SearchBox, RefinementListFilter, MenuFilter, InputFilter, RangeFilter,
	Hits, HitsStats, NoHits, Pagination, SortingSelector,
	SelectedFilters, ResetFilters, ItemHistogramList,
	Layout, LayoutBody, LayoutResults, TopBar,
	SideBar, ActionBar, ActionBarRow, TermQuery
} from "searchkit";

import { PlanHitsListItem, PlanHitsGridItem } from "./components";
import { inputQuery, generateRescore } from "./custom_queries";
require("./index.scss");

const host = "http://169.45.104.77:80/plans/plan"
const searchkit = new SearchkitManager(host)

try {
	var { user_state, query_weights, premium_cap, health } = window.user_input

	searchkit.addDefaultQuery( (query) => {
		 return query.addFilter("state",
			 TermQuery("state", user_state)
		 )
	})

	if ( query_weights != 0) {
		const rescore_query = generateRescore(query_weights)
		searchkit.setQueryProcessor( (plainQueryObject) => {
				plainQueryObject["rescore"] = rescore_query
				return plainQueryObject
		})
	}

	var display_cap_yes = "none"
	var display_cap_no = "none"
	if (premium_cap == 0) {
		display_cap_no = "inline"
	} else {
		display_cap_yes = "inline"
	}

} //end try

catch(error) {
	console.log("Frontend Mode Only");
}

export class SearchPage extends React.Component {
	render(){


		return (
			<SearchkitProvider searchkit={searchkit}>
		    <Layout>
		      <TopBar>
						<div>
							<a href={"/"}>
								<img src={"/static/img/semantic-health-logo-small-white.png"}/>
							</a>
						</div>
		        <SearchBox
		          autofocus={true}
							placeholder="Search plan name, issuer, type, metal level..."
		          queryFields={["plan_name^5", "level^2", "plan_type^2", "issuer^5"]}/>
		      </TopBar>
		      <LayoutBody>
		        <SideBar>
							<InputFilter
								id="providers"
								title="Search Providers"
								placeholder="Search providers..."
								queryOptions={ {path: "providers", subfield: "provider_name"} }
								queryBuilder={ inputQuery }
							/>
							<InputFilter
								id="specialties"
								title="Search Specialties"
								placeholder="Search specialties..."
								queryOptions={ {path: "providers", subfield: "speciality"} }
								queryBuilder={ inputQuery }
							/>
							<InputFilter
								id="drugs"
								title="Search Drugs"
								placeholder="Search drugs..."
								queryFields={["drugs"]}
							/>
							<RangeFilter
								id="premiums_median"
								title="Average Premiums ($)"
								field="premiums_median"
								min={0}
								max={800}
								showHistogram={true}
							/>
							<MenuFilter
								id="level"
								title="Metal Level"
								field="level.raw"
								orderKey="_term"
								listComponent={ItemHistogramList}
							/>
							<MenuFilter
								id="plan_type"
								title="Plan Type"
								field="plan_type.raw"
								orderKey="_term"
								listComponent={ItemHistogramList}
							/>
							<RefinementListFilter
					            id="issuer"
					            title="Issuer"
					            field="issuer.raw"
					            operator="OR"
								exclude=""
		            			size={10}
							/>
		        </SideBar>
		        <LayoutResults>
		          <ActionBar>
								<ActionBarRow>
									<div className = {'hits-details show-query'}>
										Showing Plans for {user_state}, tailored to {health}.&nbsp;
										<span style={ {display: display_cap_yes} }>Your monthly insurance cost is capped at ${premium_cap}. </span>
										<span style={ {display: display_cap_no} }>You do not qualify for a subsidy, or you did not enter your income. </span>
									</div>
								</ActionBarRow>
		            <ActionBarRow>
		              <HitsStats/>
									<SortingSelector options={[
										{label:"Relevance", field:"_score", order:"desc", defaultOption:true},
										{label:"Premium", field:"premiums_median", order:"asc", defaultOption:true}
									]}/>
		            </ActionBarRow>
		            <ActionBarRow>
		              <SelectedFilters/>
		              <ResetFilters/>
		            </ActionBarRow>
		          </ActionBar>
		          <Hits
								mod="sk-hits-grid"
								hitsPerPage={20}
								itemComponent={PlanHitsGridItem}
								sourceFilter={["plan_name", "issuer", "state", "plan_type", "level", "url", "logo_url",
									"premiums_q1", "premiums_median", "premiums_q3", "plan_rank_*"]}
							/>
		          <NoHits/>
							<Pagination showNumbers={true}/>
		        </LayoutResults>
		      </LayoutBody>
		    </Layout>
		  </SearchkitProvider>
		)
	}
}
