import subprocess
import malt_eval_wrapper


class MaltWrapper(object):
    def __init__(self):
        self.malt_lib = 'lib/malt.jar'

    def train(self, in_train_file, out_model_file_name):
        subprocess_cmd = 'java -Xmx8G -jar %s -c %s -i %s -if malttab -m learn' % \
            (self.malt_lib, out_model_file_name, in_train_file)
        malt = subprocess.Popen(subprocess_cmd.split())
        malt.communicate()

    def parse(self, in_test_file, in_model_file_name, out_result_file):
        subprocess_cmd = 'java -jar %s -c %s -i %s -o %s -m parse' % \
            (self.malt_lib, in_model_file_name, in_test_file, out_result_file)
        malt = subprocess.Popen(subprocess_cmd.split())
        return malt.communicate()[0]

def train_and_calculate_accuracy(in_train_filename, in_test_filename, out_model_name):
    wrapper = MaltWrapper()
    wrapper.train(in_train_filename, out_model_name)
    wrapper.parse(in_test_filename, out_model_name + '.mco', 'malt_result.tab')
    malt_eval = malt_eval_wrapper.MaltEvalWrapper()
    accuracy_value = malt_eval.calculate_accuracy(in_test_filename, 'malt_result.tab')
    return accuracy_value