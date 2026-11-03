# Exact positive banners observed in the original controller's Android dumps.
POSITIVE_BANNERS={'awesome!', 'good job!', 'amazing!', 'nice job!', 'great!', 'correct!',
                  'excellent!', 'great job!', 'nice!', 'nicely done!', 'wow!'}
ERROR_MARKERS=('got it', 'incorrect', 'error', 'something went wrong', 'skip')

def feedback_terminal(tree):
    labels={n.get('text','').strip().casefold() for n in tree.iter('node')}
    if any(error in label for label in labels for error in ERROR_MARKERS):
        return True
    return bool(labels.intersection(POSITIVE_BANNERS)) and any(
        n.get('text','')=='CONTINUE' and n.get('enabled')=='true' for n in tree.iter('node'))

def assert_native_correct(tree, context, visual_positive=False):
    labels={n.get('text','').strip().casefold() for n in tree.iter('node')}
    assert not any(error in label for label in labels for error in ERROR_MARKERS), context+': incorrect, error, or skip feedback: '+repr(labels)
    assert labels.intersection(POSITIVE_BANNERS) or visual_positive, context+': no observed native positive feedback: '+repr(labels)
    assert any(n.get('text','')=='CONTINUE' and n.get('enabled')=='true' for n in tree.iter('node')), context+': Continue is not enabled'

