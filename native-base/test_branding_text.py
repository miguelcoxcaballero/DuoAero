"""Visible branding changes must never rewrite links or package identifiers."""
from branding import WORDMARKS, display_text, mascot_name, rebrand_app_display_names, rebrand_visible_literal
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
for name,method,instruction in [
    ('smali_classes4/wxp.smali','.method public static final j(Ljava/lang/String;Ljava/lang/String;Lz5q;Ljava/lang/String;ZLkotlin/jvm/functions/Function0;Lo18;I)V','    const-string v8, "Duolingo"'),
    ('smali_classes3/fes.smali','.method public final i(Landroid/content/Context;Ljava/lang/String;Ljava/lang/String;Lc6s;Landroid/graphics/Bitmap;Landroid/os/Bundle;)V','    const-string p5, "Duolingo"')]:
    original=(SMALI/name).read_text()
    branded=rebrand_visible_literal(original,method,instruction)
    assert branded.count('"DuoAero"') == original.count('"DuoAero"')+1
    assert branded.replace('"DuoAero"','"Duolingo"',1)==original
print('PASS: visible labels and hashtags rebranded; links and package IDs preserved.')
