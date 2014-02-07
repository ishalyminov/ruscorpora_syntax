import subprocess
import re


class MaltEvalWrapper(object):
    def __init__(self):
        self.malt_eval_lib = 'dist-20120206/lib/MaltEval.jar'

    def calculate_accuracy(self, in_auto_result, in_gold_result):
        subprocess_cmd = 'java -jar %s  -s %s -g %s' % \
            (self.malt_eval_lib, in_auto_result, in_gold_result)
        malt_eval = subprocess.Popen(subprocess_cmd.split(), stdout=subprocess.PIPE)
        eval_output = malt_eval.communicate()[0]
        accuracy_patterns = re.findall('(\-|\d+\.\d+?)\s+Row mean', eval_output)
        if not len(accuracy_patterns):
            raise RuntimeError('Invalid MaltEval output: %s' % eval_output)
        value = accuracy_patterns[0]
        return float(value) if value != '-' else 0.0
