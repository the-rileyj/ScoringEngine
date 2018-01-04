from forms import *
config = {}
config['teams'] = {}
config['domains'] = {}
config['services'] = {}
config['checks'] = {}
config['check_ios'] = {}

def get_forms():
    forms = {}
    forms['team'] = TeamForm()
    forms['domain'] = DomainForm()
    forms['web-user'] = WebUserForm(config['teams'])
    forms['service'] = ServiceForm()
    forms['check'] = CheckForm(config['services'])
    forms['input'] = PollInputForm()
    forms['checkio'] = CheckIoForm(config['checks'])
    forms['credential'] = CredentialForm(config['domains'], config['inputs'], config['check_ios'])
    return forms
