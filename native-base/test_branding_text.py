"""Visible branding changes must never rewrite links or package identifiers."""
from branding import WORDMARKS, display_text, mascot_name, rebrand_app_display_names
from runtime_config import SMALI

assert display_text('Welcome to Duolingo! #Duolingo365') == 'Welcome to DuoAero! #DuoAero365'
assert display_text('Duolingo: https://www.duolingo.com/terms') == 'DuoAero: https://www.duolingo.com/terms'
assert display_text('com.duolingo.session.SessionActivity') == 'com.duolingo.session.SessionActivity'
assert display_text('res/drawable/duolingo_logo.xml') == 'res/drawable/duolingo_logo.xml'
assert display_text('support@duolingo.com') == 'support@duolingo.com'
for control in ('duo_radio_play','duo_radio_pause','duo_radio_check_correct','duo_radio_x_incorrect'):
    assert not mascot_name(control), control
assert mascot_name('duo_radio_host_static_bea')
assert {'intro_duo_logo_green','duo_logo_green','duo_logo_grey','duo_logo_white'} <= WORDMARKS
source=(SMALI/'smali_classes3/com/duolingo/feature/appicon/AppDisplayName.smali').read_text()
modified=rebrand_app_display_names(source)
assert modified.count('DuoAero')==22 and 'Lcom/duolingo/feature/appicon/AppDisplayName;' in modified
print('PASS: visible labels and hashtags rebranded; links and package IDs preserved.')
