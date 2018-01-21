from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
import bcrypt
import flask_login
import module
import polling, checker

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])

    def __init__(self, dm):
        super(LoginForm, self).__init__()
        self.dm = dm

    def validate(self):
        if not super(LoginForm, self).validate():
            return False

        pwhash = self.dm.get_hash(self.username.data)
        pwhash = pwhash.encode('utf-8')
        passwd = self.password.data.encode('utf-8')

        return bcrypt.checkpw(passwd, pwhash)


class PasswordChangeForm(FlaskForm):
    team = SelectField('Team', coerce=int)
    ctype = SelectField('Credential Type')
    domain = SelectField('Domain', coerce=int)
    service = SelectField('Service', coerce=int)
    pwchange = TextAreaField('Password Changes')

    def __init__(self, dm):
        super(PasswordChangeForm, self).__init__()
        self.dm = dm

        self.team.choices=[(t.id, t.name) for t in dm.teams]
        self.team.validators=[Optional()]

        self.ctype.choices=[('Local', 'Local'), ('Domain', 'Domain')]
        self.ctype.validators=[InputRequired()]
        
        self.domain.choices=[(d.id, d.fqdn) for d in dm.domains]
        self.domain.validators=[Optional()]

        self.service.choices=[(s.id, 'Host: %d, Port: %d' % (s.host, s.port)) for s in dm.services]
        self.service.validators=[Optional()]

        self.pwchange.validators=[InputRequired(),
                Regexp('^(.*[^\s]+:[^\s]+.*(\r\n)*)+$',
                    message='Invalid format: Use user:password, one per line')]

class PasswordResetForm(FlaskForm):
    user = SelectField('User', validators=[Optional()])
    current_pw = PasswordField('Current Password', validators=[Optional()])
    new_pw = PasswordField('New Password', validators=[InputRequired()])
    confirm_new_pw = PasswordField('Confirm New Password', validators=[InputRequired()])

    def __init__(self, dm):
        super(PasswordResetForm, self).__init__()
        self.dm = dm
        self.user.choices=[(username, username) for username in dm.users.keys()]

    def validate(self):
        if not super(PasswordResetForm, self).validate():
            return False

        if self.new_pw.data != self.confirm_new_pw.data:
            self.errors['samepw'] = 'Passwords don\'t match'
            return False

        if not flask_login.current_user.is_admin:
            username = self.user.data
            print('formdata', username)
            if username == 'None':
                username = flask_login.current_user.name
            print(username)
            username = username.lower()
    
            pwhash = self.dm.get_hash(username)
            pwhash = pwhash.encode('utf-8')
            passwd = self.current_pw.data.encode('utf-8')
    
            if not bcrypt.checkpw(passwd, pwhash):
                self.errors['validpw'] = 'Invalid Password'
                return False
        return True

class TeamForm(FlaskForm):
    name = TextField('Name', validators=[InputRequired()])
    subnet = TextField('Subnet', validators=[InputRequired(), IPAddress()])
    netmask = TextField('Netmask', validators=[InputRequired(), IPAddress()])

class DomainForm(FlaskForm):
    fqdn = TextField('FQDN', validators=[InputRequired()])

class WebUserForm(FlaskForm):
    username = TextField('Username', validators=[InputRequired()])
    password = TextField('Password', validators=[InputRequired()])
    team = SelectField('Team', validators=[InputRequired()])
    is_admin = BooleanField('Is Admin', validators=[InputRequired()])

    def __init__(self, teams):
        super(WebUserForm, self).__init__()
        teams = [(id, t['name']) for id, t in teams.items()]
        self.team.choices = [(0, 'None')] + teams

class ServiceForm(FlaskForm):
    host = IntegerField('Host', validators=[InputRequired(), NumberRange(1, 4294967294)])
    port = IntegerField('Port', validators=[InputRequired(), NumberRange(1, 65535)])

class CheckForm(FlaskForm):
    name = TextField('Name', validators=[InputRequired()])
    check_function = SelectField('Check Function', validators=[InputRequired()])
    poller = SelectField('Poller', validators=[InputRequired()])
    service = SelectField('Service', validators=[InputRequired()])

    def __init__(self, services):
        super(CheckForm, self).__init__()
        check_funcs = module.get_functions_below(checker)
        self.check_function.choices = [(c, c) for c in check_funcs]
        pollers = module.get_classes_below_matching(polling, '.+Poller')
        self.poller.choices = [(p, p) for p in pollers]
        self.service.choices = [(id, 'Host: %s, Port: %s' % (s['host'], s['port'])) for id, s in services.items()]

class PollInputForm(FlaskForm):
    input_type = SelectField('Input Type', validators=[InputRequired()])
    # TODO Inputs?

    def __init__(self):
        super(PollInputForm, self).__init__()
        types = module.get_classes_below_matching(polling, '.+PollInput')
        self.input_type.choices = [(t, t) for t in types]
class CheckIoForm(FlaskForm):
    check = SelectField('Check', validators=[InputRequired()])
    input = SelectField('Input', validators=[InputRequired()])
    # TODO expecteds?

    def __init__(self, checks, inputs):
        super(CheckIoForm, self).__init__()
        self.check.choices = [(id, c['name']) for id, c in checks.items()]
        self.input.choices = [(id, '%s:%s' % (i['input_type'], i['input'])) for id, i in inputs.items()]

class CredentialForm(FlaskForm):
    domain = SelectField('Domain', validators=[InputRequired()])
    username = TextField('Username', validators=[InputRequired()])
    password = TextField('Password', validators=[InputRequired()])
    check_ios = SelectMultipleField('Check IOs', validators=[InputRequired()])

    def __init__(self, domains, inputs, check_ios):
        super(CredentialForm, self).__init__()
        self.domain.choices = [(0, 'None')] + [(id, d['fqdn']) for id, d in domains.items()]
        self.check_ios.choices = [(id, '%s:%s->%s' % (inputs[c['input']]['input_type'], inputs[c['input']]['input'], c['expected'])) for id, c in check_ios.items()] # TODO
