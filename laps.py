#!/usr/bin/env python3
import ui
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
import json
import keychain
import os

options_path = 'options.json'
keychain_service = 'pylaps'

def search(sender):
    options = load_options()
    # TODO: Check options to make sure they exist and exit with message if they
    #       don't.
    # TODO: Add a progress indicator and thread search so a long search doesn't
    #       appear to lock it up
    if 'username' in options:
        password = keychain.get_password(keychain_service, options['username'])
    computer_name = v['computer_name'].text
    if not computer_name:
        return
    server = Server(options['server'], get_info=ALL)
    conn = Connection(server,
        options['username'],
        password,
        auto_bind=True)

    conn.search(search_base=options['search_base'],
        search_filter='(&(cn={name}))'.format(name=computer_name),
        search_scope=SUBTREE,
        attributes=ALL_ATTRIBUTES,
        get_operational_attributes=True)

    result = json.loads(conn.response_to_json())
    
    if 'ms-Mcs-AdmPwd' in result['entries'][0]['attributes']:
        passwd = result['entries'][0]['attributes']['ms-Mcs-AdmPwd']
    else:
        passwd = 'Not set.'
    distinguished_name = result['entries'][0]['attributes']['distinguishedName']
    v['text_password'].text = passwd
    v['text_name'].text = distinguished_name
    conn.unbind()
    
def show_options(sender):
    options = load_options()
    if 'server' in options:
        options_view['server'].text = options['server']
    if 'search_base' in options:
        options_view['search_base'].text = options['search_base']
    if 'username' in options:
        options_view['username'].text = options['username']
        password = keychain.get_password(keychain_service, options['username'])
        if password:
            options_view['password'].text = password
    options_view.present('sheet')

def cancel_options(sender):
    options_view.close()

def save_options(sender):
    options = {}
    options['username'] = options_view['username'].text
    options['search_base'] = options_view['search_base'].text
    options['server'] = options_view['server'].text
    with open(options_path, 'w') as options_file:
        json.dump(options, options_file)
    keychain.set_password(keychain_service,
                          options['username'],
                          options_view['password'].text)
    options_view.close()

def load_options():
    if os.path.exists(options_path):
        with open(options_path) as options_file:
            options = json.load(options_file)
    else:
        options = {}
    return options

options_view = ui.load_view('options.pyui')
v = ui.load_view()
v.present('sheet')
