"""Visible branding changes must never rewrite links or package identifiers."""
from branding import display_text, mascot_name

assert display_text('Welcome to Duolingo! #Duolingo365') == 'Welcome to DuoAero! #DuoAero365'
assert display_text('Duolingo: https://www.duolingo.com/terms') == 'DuoAero: https://www.duolingo.com/terms'
assert display_text('com.duolingo.session.SessionActivity') == 'com.duolingo.session.SessionActivity'
assert display_text('res/drawable/duolingo_logo.xml') == 'res/drawable/duolingo_logo.xml'
assert display_text('support@duolingo.com') == 'support@duolingo.com'
for control in ('duo_radio_play','duo_radio_pause','duo_radio_check_correct','duo_radio_x_incorrect'):
    assert not mascot_name(control), control
assert mascot_name('duo_radio_host_static_bea')
print('PASS: visible labels and hashtags rebranded; links and package IDs preserved.')
