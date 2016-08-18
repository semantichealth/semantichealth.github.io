import * as React from "react";
import { logClick, logRanks, display_inner_hits, load_backup_logo } from "./helper";

export const PlanHitsGridItem = (props)=> {
  const { bemBlocks, result } = props
  const { plan_name, issuer, state, plan_type, level, premiums_q1, premiums_median, premiums_q3 } = result._source

  let logo_url = result._source.logo_url
  if (logo_url == "") {
    logo_url = "/static/img/semantic-health-logo-small.png"
  }
  let url = result._source.url
  if (url == "") {
    url = encodeURI("http://www.google.com/#q=" + issuer + " " + plan_name)
  }

  let providers = ''
  let display_providers = 'none'
  try {
    const [inner_providers, inner_display_providers] = display_inner_hits(result.inner_hits, "provider_name")
    providers = inner_providers
    display_providers = inner_display_providers
  }
  catch (error) {}

  let specialists = ''
  let display_specialists = 'none'
  try {
    const [inner_specialists, inner_display_specialists] = display_inner_hits(result.inner_hits, "speciality")
    specialists = inner_specialists
    display_specialists = inner_display_specialists
  }
  catch (error) {}

  console.log(result)
  logRanks({
      "plan_id": result._id,
      "plan_score": result._score
  })

  return (
    <div className={bemBlocks.item().mix(bemBlocks.container("item"))} data-qa="hit">

      <a href={url} target="_blank">
        <div className="div-img-logo">
          <img data-qa="poster" className={bemBlocks.item("poster")}
            src={logo_url}
            onMouseDown={logClick}
            data-plan-id={result._id}
            onError={load_backup_logo}
          />
        </div>
        <div data-qa="title" className={bemBlocks.item("title")}
          onMouseDown={logClick}
          data-plan-id={result._id}>{plan_name}</div>
      </a>

      <ul style={{marginTop: 8, marginBottom: 8, marginLeft: 0, paddingLeft: 0, listStyle: 'none' }}>
        <li>Plan: <span className={'hits-details'}> { plan_name } </span></li>
        <li>Issuer: <span className={'hits-details'}> { issuer } </span></li>
        <li>Type: <span className={'hits-details'}> { plan_type } </span></li>
        <li>Score: <span className={'hits-details'}> { result._score } </span></li>
        <li>Level: <span className={'hits-details'}> { level } </span></li>
        <li><a href={ "providers_map?plan_id=" + encodeURIComponent(result._id) } target="_blank" className={ "link" }>
          Providers Nearby
        </a></li>
        <li style={ {display: display_providers} }>Matched Providers: <span className={'hits-details'}> { providers } </span></li>
        <li style={ {display: display_specialists} }>Matched Specialists: <span className={'hits-details'}> { specialists } </span></li>
        <li><br></br></li>
        <li className={'premiums'}> ${ parseInt(premiums_median) } /mo</li>
        <li className={'hits-details'}> (estimated ${ parseInt(premiums_q1) } &mdash; ${ parseInt(premiums_q3) }) </li>
      </ul>

    </div>
  )
}
