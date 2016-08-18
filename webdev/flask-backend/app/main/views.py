from flask import abort, current_app, jsonify, redirect, render_template, request, session, url_for
from . import main
from aca_subsidycalc import CalcAcaSubsidy
from coordinates import get_coordinates
from database import get_db, log_query, log_click, log_ranks
from fb_handler import send_message
from forms import InputForm
from letor_get_weights import get_weights
from uuid import uuid4

@main.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm()
    if form.validate_on_submit():
        session['session_id'] = unicode(uuid4())
        session['state'] = form.state.data
        session['age'] = form.age.data
        session['zipcode'] = form.zipcode.data
        session['health'] = form.health.data
        session['income'] = form.income.data
        session['hhsize'] = form.hhsize.data
        if session['income'] and session['hhsize']:
            caps = CalcAcaSubsidy(session['income'], session['hhsize'])
            if caps:
                session['premium_cap'] = int(caps[1])
            else:
                session['premium_cap'] = 0
        else:
            session['premium_cap'] = 0
        session['query_weights'] = get_weights(session['state'], str(session['health']))
        log_query(
            session_id = session['session_id'],
            state = session['state'],
            age = session['age'],
            zipcode = session['zipcode'],
            health = session['health']
        )
        return redirect(url_for('main.results'))
    return render_template('index.html', form=form)

@main.route('/results')
def results():
    response = dict(user_state=session['state'],
                    query_weights=session['query_weights'],
                    premium_cap=session['premium_cap'],
                    health=session['health'])
    return render_template('results.html', response=response)

@main.route('/_clicks', methods=['POST'])
def _clicks():
    if ('session_id' not in session) or (not request.form) or ('plan_id' not in request.form):
        abort(400)
    plan_id = request.form['plan_id']
    log_click(session['session_id'], plan_id)
    return jsonify({'status': 'OK'}), 201

@main.route('/_ranks', methods=['POST'])
def _ranks():
    if ('session_id' not in session) or (not request.form) or ('plan_id' not in request.form):
        abort(400)
    plan_id = request.form['plan_id']
    plan_score = request.form['plan_score']
    log_ranks(session['session_id'], plan_id, plan_score)
    return jsonify({'status': 'OK'}), 201

@main.route('/providers_map')
def providers_map():
    if ('session_id' not in session):
        abort(400)
    center, provider_array = get_coordinates(plan_id=request.args.get("plan_id"), zipcode=session['zipcode'], state=session['state'])
    response= dict(center=center,
                   provider_array = provider_array)
    return render_template('providers_map.html', response=response)

@main.route('/webhook', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.verify_token") == current_app.config['FB_VERIFY_TOKEN']:
        return request.args["hub.challenge"], 200
    else:
        return "Failed validation. Make sure the validation tokens match.", 403

@main.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    if data['object'] == 'page':
        for entry in data['entry']:
            for messaging_event in entry['messaging']:
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    recipient_id = messaging_event["recipient"]["id"]
                    message_text = messaging_event["message"]["text"]
                    send_message(sender_id, message_text)
                if messaging_event.get("delivery"):
                    pass
                if messaging_event.get("optin"):
                    pass
                if messaging_event.get("postback"):
                    pass
    return "OK", 200
