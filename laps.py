#!/usr/bin/env python3
import ui
from ldap3 import Server, Connection, ALL, SUBTREE, ALL_ATTRIBUTES
import json

def search(sender):
    server_name = ''
    username = ''
    password = ''
    search_base = ''
    computer_name = v['computer_name'].text
    if not computer_name:
        return
    server = Server(server_name, get_info=ALL)
    conn = Connection(server,
        username,
        password,
        auto_bind=True)

    conn.search(search_base=search_base,
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

v = ui.load_view()
v.present('sheet')
