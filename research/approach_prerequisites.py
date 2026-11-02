"""Partial isolated prerequisites for the measured-condition approach draft.

The stall formula is deliberately absent pending a native radical containing
all interactive named quantities. This is not a complete lesson.
"""
from speed_limits_lesson import introduce
from approach_speed_steps import DENSITY, APPROACH, CONVERT


def prerequisites():
    return sum([
      introduce('APPROACH-DENSITY','Air density equals pressure divided by gas constant times absolute ___.',
        'temperature',['mass','wing area','force'],DENSITY,
        ['air density','pressure','gas constant','absolute temperature'],['mass','area','force'],
        ['___','=','___',r'\div','(','___',r'\times','___',')'],
        ['ρ','p','R','T'],['___','=','___',r'\div','(','___',r'\times','___',')'],r'=\frac{p}{RT}'),
      introduce('APPROACH-FACTOR','Approach speed equals stall speed multiplied by ___.',
        '1.3',['2','3.6','0.5'],APPROACH,
        ['approach speed','stall speed'],['mass','area','temperature'],
        ['___','=','1.3',r'\times','___'],['V_app','V_s'],['___','=','1.3',r'\times','___'],r'=1.3V_s'),
      introduce('APPROACH-CONVERT','Speed in kilometers per hour is speed in meters per second times ___.',
        '3.6',['1.3','0.5','9.81'],CONVERT,
        ['speed in km/h','speed in m/s'],['mass','area','temperature'],
        ['___','=','3.6',r'\times','___'],['V_kmh','V_ms'],['___','=','3.6',r'\times','___'],r'=3.6V_{\mathrm{m/s}}')
    ],[])
