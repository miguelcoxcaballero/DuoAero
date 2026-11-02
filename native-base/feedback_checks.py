# Exact positive banners observed in the original controller's Android dumps.
POSITIVE_BANNERS={'awesome!', 'good job!', 'amazing!', 'nice job!', 'great!', 'correct!',
                  'excellent!', 'great job!', 'nice!', 'nicely done!', 'wow!'}
def assert_native_correct(tree, context):
    labels={n.get('text','').strip().casefold() for n in tree.iter('node')}
    errors=('got it', 'incorrect', 'error', 'something went wrong', 'skip')
    assert not any(error in label for label in labels for error in errors), context+': incorrect, error, or skip feedback: '+repr(labels)
    assert labels.intersection(POSITIVE_BANNERS), context+': no observed native positive feedback: '+repr(labels)
    assert any(n.get('text','')=='CONTINUE' and n.get('enabled')=='true' for n in tree.iter('node')), context+': Continue is not enabled'

