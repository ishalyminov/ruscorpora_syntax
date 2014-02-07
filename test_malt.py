import os
import sys
import converter
import malt_eval_wrapper
import malt_wrapper


def test_malt(in_model_name, in_test_dataset):
    if not os.path.isdir('datasets'):
        os.makedirs('datasets')
    converter.process_directory(in_test_dataset, open('datasets/test.tab'))
    wrapper = malt_wrapper.MaltWrapper()
    wrapper.parse('datasets/test.tab', in_model_name, 'malt_result.tab')
    accuracyEval = malt_eval_wrapper.MaltEvalWrapper()
    print accuracyEval.calculate_accuracy('malt_result.tab', 'datasets/test.tab')

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: test_malt.py <model name> <input dataset>'
        exit(0)
    test_malt(sys.argv[1], sys.argv[2])
