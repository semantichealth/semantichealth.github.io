import $ from "jquery";

export const logClick = (event)=> {
  const payload = {
    "plan_id": event.target.getAttribute("data-plan-id")
  };
  const success = (response)=> {
    console.log(response);
  };
  $.post($SCRIPT_ROOT + '/_clicks', payload, success);
};

export const logRanks = (payload)=> {
  const success = (response)=> {
    console.log(response);
  };
  if (payload.plan_score == null) {
    payload.plan_score = 1
  }
  $.post($SCRIPT_ROOT + '/_ranks', payload, success);
};

export const display_inner_hits = (inner_hits, subfield) => {
  const hits = inner_hits[subfield]["hits"]["hits"]
  const provider_array = $.map(hits,
    function(value, index) {
      return value["_source"]["provider_name"]
    }
  )
  const inner_providers = provider_array.join(', ')
  const display = 'block'
  return [inner_providers, display]
};

export const load_backup_logo = (event) => {
  event.target.setAttribute("src", "/static/img/semantic-health-logo-backup.png")
}
