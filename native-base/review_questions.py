"""Apply explicit editorial reviews without altering exam excerpts or question IDs."""
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]

REVIEWS = {
    'TA1-0402': {
        'stem': 'Regarding kinetic heating during flight, which statement is correct?',
        'options': [
            'Every point on the aircraft skin reaches the ideal stagnation temperature.',
            'Skin temperature depends on heat transfer as well as the local flow conditions.',
            'Cabin pressurisation determines the stagnation temperature at the wing leading edge.',
            'At a fixed Mach number, stagnation temperature is independent of static air temperature.'
        ],
        'answer': 1,
        'explanation': 'Stagnation temperature describes an ideal adiabatic deceleration. Actual skin temperature also depends on recovery and heat transfer. For a calorically perfect gas, Tt/T = 1 + (gamma - 1) M²/2.',
        'exam_alignment': ['EX-2025-11-06-4'],
        'misconceptions': ['Confuses ideal stagnation temperature with actual wall temperature.', 'Correct: distinguishes flow energy from surface thermal equilibrium.', 'Confuses cabin conditions with the external flow.', 'Omits the static-temperature factor.'],
    },
    'TA1-0265': {
        'stem': 'An aircraft climbs to a level where air density is 20% lower. Weight and true airspeed are unchanged, and both conditions are steady level flight below stall. Which change is required?',
        'options': ['Reduce the lift coefficient by 20%.', 'Increase the lift coefficient by 25%.', 'Increase the lift coefficient by 20%.', 'Keep the lift coefficient unchanged because weight is unchanged.'],
        'answer': 1,
        'explanation': 'Level flight requires W = rho V² S CL/2. Therefore CL2/CL1 = rho1/rho2 = 1/0.80 = 1.25. Before stall, this normally requires a higher angle of attack.',
        'exam_alignment': ['EX-2023-11-06-4'],
        'misconceptions': ['Reverses the density dependence.', 'Correct: uses the reciprocal density ratio.', 'Treats a reciprocal change as the same percentage.', 'Ignores the change in dynamic pressure.'],
    },
    'TA1-0232': {
        'stem': 'In the jet Breguet equation, fuel consumption ce is measured in kg/(N s). Which prefactor gives range in metres when multiplied by L/D and ln(mi/mf)?',
        'options': ['ce/V', 'V/(g ce)', 'V/ce', 'g V/ce'],
        'answer': 1,
        'explanation': 'The mass-specific coefficient ce must be multiplied by g to obtain a weight-specific coefficient in s^-1. Thus V/(g ce) has units of length.',
        'exam_alignment': ['EX-2025-11-06-6', 'EX-2022-11-08-8'],
        'misconceptions': ['Inverts the speed and consumption dependence.', 'Correct: converts mass flow to weight flow.', 'Omits the conversion between mass and weight.', 'Places gravity in the numerator instead of the denominator.'],
        'rich_text': {'stem': [{'text': 'In the jet Breguet equation, fuel consumption '}, {'latex': r'c_e'}, {'text': ' is measured in '}, {'latex': r'\frac{\mathrm{kg}}{\mathrm{N}\,\mathrm{s}}'}, {'text': '. Which prefactor gives range in metres when multiplied by '}, {'latex': r'\frac{L}{D}'}, {'text': ' and '}, {'latex': r'\ln(m_i/m_f)'}, {'text': '?'}], 'options': [[{'latex': r'\frac{c_e}{V}'}], [{'latex': r'\frac{V}{g c_e}'}], [{'latex': r'\frac{V}{c_e}'}], [{'latex': r'\frac{gV}{c_e}'}]]},
    },
    'TA1-0753-D3': {
        'stem': 'At constant static temperature, an aircraft flies at the maximum Mach number allowed by a leading-edge heating limit. It climbs to air density 20% lower while weight and configuration remain unchanged. The same heating limit applies. What lift-coefficient ratio is required in steady level flight?',
        'options': ['CL2/CL1 = 0.80', 'CL2/CL1 = 1.25', 'CL2/CL1 = 1.20', 'CL2/CL1 = 1.00'],
        'answer': 1,
        'explanation': 'The unchanged static temperature and stagnation-temperature limit give the same limiting Mach number and true airspeed. Lift balance then requires CL2/CL1 = rho1/rho2 = 1/0.80 = 1.25. This combines the heating limit with the density effect rather than treating them independently.',
        'exam_alignment': ['EX-2025-11-06-4', 'EX-2023-11-06-4'],
        'misconceptions': ['Reverses the density ratio.', 'Correct: resolves the thermal speed constraint before applying lift balance.', 'Uses a 20% rather than reciprocal increase.', 'Assumes constant Mach also implies constant dynamic pressure.'],
        'rich_text': {'options': [[{'latex': r'\frac{C_{L,2}}{C_{L,1}}=0.80'}], [{'latex': r'\frac{C_{L,2}}{C_{L,1}}=1.25'}], [{'latex': r'\frac{C_{L,2}}{C_{L,1}}=1.20'}], [{'latex': r'\frac{C_{L,2}}{C_{L,1}}=1.00'}]]},
    },
    'TA1-0832-D3': {
        'stem': 'A jet cruises at unchanged pressure, Mach number, weight, wing area and drag polar. Static temperature rises by 10%, while mass-specific fuel consumption rises by 3%. With the same initial-to-final mass ratio, what is the approximate ratio of the new Breguet range to the original range?',
        'options': ['1.068', '1.018', '0.971', '0.925'],
        'answer': 1,
        'explanation': 'At fixed pressure and Mach, q = gamma p M²/2 is unchanged, so CL and L/D are unchanged. True airspeed scales as sqrt(T). Thus R2/R1 = sqrt(1.10)/1.03 = 1.0183. The distractors respectively use T instead of sqrt(T), ignore the speed change, or reverse the temperature effect.',
        'exam_alignment': ['EX-2023-11-06-8', 'EX-2025-01-13-6'],
        'misconceptions': ['Makes true airspeed proportional to temperature.', 'Correct: combines constant dynamic pressure with the square-root speed change.', 'Accounts for consumption but ignores temperature.', 'Reverses the speed response to temperature.'],
        'rich_text': {'explanation': [{'text': 'At fixed pressure and Mach, '}, {'latex': r'q=\frac{\gamma p M^2}{2}'}, {'text': ' is unchanged. Therefore CL and L/D stay fixed, while true airspeed scales with the square root of temperature. Hence '}, {'latex': r'\frac{R_2}{R_1}=\frac{\sqrt{1.10}}{1.03}\approx1.0183'}, {'text': '.'}]},
    },
}

def apply(bank):
    by_id = {q['id']: q for q in bank}
    for identifier, review in REVIEWS.items():
        question = by_id[identifier]
        assert question['origin']['kind'] == 'practice'
        for source in review['exam_alignment']:
            assert by_id[source]['origin']['kind'] == 'exam'
        question.update({k: v for k, v in review.items() if k != 'misconceptions'})
        question['option_explanations'] = dict(zip(question['options'], review['misconceptions']))
        question['editorial_review'] = {'basis': 'Comparison with the cited stored exam excerpts; these are new practice questions, not original exam questions.', 'version': 1}
    return bank

if __name__ == '__main__':
    for relative in ['app/assets/questions.json', 'web/bank_en_final.json']:
        path = ROOT / relative
        bank = json.loads(path.read_text(encoding='utf-8-sig'))
        path.write_text(json.dumps(apply(bank), ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Applied {len(REVIEWS)} explicit exam-aligned reviews; original exam excerpts preserved.')
