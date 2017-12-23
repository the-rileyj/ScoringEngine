#!/usr/bin/python3

from dm import DataManager
from forms import *
import flask
from flask import Flask, render_template, request, redirect
from urllib.parse import urlparse, urljoin
import plot
import score
import validate
import flask_login
from flask_login import LoginManager, login_user, logout_user, login_required
from web_model import User
from decorators import *

app = Flask(__name__)
app.secret_key = 'this is a secret'

dm = DataManager()
dm.load_db()

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    if user_id not in dm.users:
        return None
    return dm.users[user_id]

def is_safe_url(target):
    ref_url = urlparse(flask.request.host_url)
    test_url = urlparse(urljoin(flask.request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc

@app.route('/')
@app.route('/status')
def status():
    teams = dm.teams
    checks = dm.checks
    results = dm.latest_results()
    teams.sort(key=lambda t: t.name)
    return render_template('status.html', teams=teams, checks=checks, results=results)

@app.route('/scores')
@login_required
@admin_required
def scores():
    teams = dm.teams
    checks = dm.checks
    team_ids = [t.id for t in teams]
    check_ids = [c.id for c in checks]
    results = score.get_results_list()
    uptime = score.uptime(results)
    return render_template('scores.html', teams=teams, checks=checks, uptime=uptime, results=results, team_ids=team_ids, check_ids=check_ids)

@app.route('/credentials', methods=['GET'])
@login_required
@admin_required
def credentials():
    dm.reload_credentials()
    team_id = int(request.args.get('tid'))
    team = next(filter(lambda t: t.id == team_id, dm.teams))
    credentials = [cred for cred in dm.credentials if cred.team.id == team_id]
    credentials.sort(key= lambda c: (c.check_io.check.name, c.username))
    return render_template('credentials.html', credentials=credentials, team=team)

@app.route('/bulk', methods=['GET', 'POST'])
@login_required
def bulk():
    form = PasswordChangeForm(dm)
    success = False
    if request.method == 'POST':
        if form.validate_on_submit():
            user = flask_login.current_user
            if user.is_admin:
                team_id = form.team.data
            else:
                team_id = user.team.id

            domain_id = form.domain.data
            service_id = form.service.data
            pwchange = form.pwchange.data

            dm.change_passwords(team_id, domain_id, service_id, pwchange)
            success = True
    return render_template('bulk.html', form=form, success=success)

@app.route('/result_log', methods=['GET'])
@login_required
@admin_required
def result_log():
    dm.reload_credentials()
    dm.load_results()

    team_id = int(request.args.get('tid'))
    check_id = int(request.args.get('cid'))
    results = sorted(dm.results[team_id][check_id], key= lambda r: r.time, reverse=True)

    fname = plot.plot_results(results) # Results plot
    return render_template('result_log.html', results=results, fname=fname)

@app.route('/competition', methods=['GET', 'POST'])
@login_required
@admin_required
def competition():
    running = dm.settings['running']
    if request.method =='POST':
        if request.form['running'] == 'Start':
            running = True
        elif request.form['running'] == 'Stop':
            running = False
        dm.update_setting('running', running)
    return render_template('competition.html', running=running)

@app.route('/config', methods=['GET', 'POST'])
@login_required
@admin_required
def config():
    teams = []
    domains = []
    services = []
    checks = []
    check_ios = []

    forms = {}
    forms['team'] = TeamForm()
    forms['domain'] = DomainForm()
    forms['web-user'] = WebUserForm(teams)
    forms['service'] = ServiceForm()
    forms['check'] = CheckForm(services)
    forms['input'] = PollInputForm()
    forms['checkio'] = CheckIoForm(checks)
    forms['credential'] = CredentialForm(domains, check_ios)
    
    success = False
    if forms['team'].validate_on_submit():
        print(forms['team'].name.data)
        print(forms['team'].subnet.data)
        print(forms['team'].netmask.data)
        success = True
    return render_template('config.html', success=success, forms=forms)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(dm)
    error = None
    if request.method == 'POST':
        if form.validate_on_submit():
            user = load_user(form.username.data.lower())
            if user is not None: # Valid user
                login_user(user)
        
                flask.flash('Logged in successfully!')
        
                next = flask.request.args.get('next')
                if not is_safe_url(next): # Open redirect protection
                    return flask.abort(400)

                return redirect(next or flask.url_for('status'))
        else:
            error = "Invalid username/password"
    return render_template('login.html', form=form, error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(flask.url_for('status'))

@app.route('/password_reset', methods=['GET', 'POST'])
@login_required
def pw_reset():
    form = PasswordResetForm(dm)
    success = False
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.user.data
            if username == 'None':
                username = flask_login.current_user.name
            username = username.lower()
            
            dm.change_user_password(username, form.new_pw.data)
            success = True
    return render_template('pw_reset.html', success=success, form=form)
