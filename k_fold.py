import os
import random
import sys
from sklearn import cross_validation
import converter
from disamb import create_datasets
import malt_wrapper
import syntagrus2malt
import syntagrus2ruscorpora

FOLDS_NUMBER = 6
DATASETS_FOLDER = 'datasets'

def perform_kfold_cross_validation(in_texts_root):
    if not os.path.isdir(DATASETS_FOLDER):
        os.makedirs(DATASETS_FOLDER)
    corpus_converted_path = os.path.join(DATASETS_FOLDER, 'corpus_converted')
    if not os.path.isdir(corpus_converted_path):
        os.makedirs(corpus_converted_path)
    syntagrus2ruscorpora.convert_directory(in_texts_root, corpus_converted_path)
    sentences_number = create_datasets.get_sentences_number_in_corpus(corpus_converted_path)
    sentences = range(sentences_number)
    print 'Sentences in the corpus: %d' % sentences_number
    random.seed(271)
    random.shuffle(sentences)
    kfold = cross_validation.KFold(len(sentences), n_folds=FOLDS_NUMBER)
    fold_accuracies = []
    for (train_index, test_index) in kfold:
        (train_filename, test_filename) = (os.path.join(DATASETS_FOLDER, 'train.xml'),
                                           os.path.join(DATASETS_FOLDER, 'test.xml'))
        (train_file, test_file) = (open(train_filename, 'w'),
                                   open(test_filename, 'w'))
        create_datasets.perform_splitting(corpus_converted_path,
                                          train_index,
                                          test_index,
                                          train_file,
                                          test_file)
        train_file.close()
        test_file.close()
        (train_tab, test_tab) = (open('datasets/train.tab', 'w'), open('datasets/test.tab', 'w'))
        syntagrus2malt.convert(os.path.join(DATASETS_FOLDER, 'train.xml'), train_tab)
        syntagrus2malt.convert(os.path.join(DATASETS_FOLDER, 'test.xml'), test_tab)
        train_tab.close()
        test_tab.close()
        fold_accuracy = malt_wrapper.train_and_calculate_accuracy('datasets/train.tab',
                                                                  'datasets/test.tab',
                                                                  'malt_model')
        fold_accuracies.append(fold_accuracy)
    mean_accuracy = sum(fold_accuracies) / len(fold_accuracies)
    print 'Mean accuracy across %d folds = %.3f' % (FOLDS_NUMBER, mean_accuracy)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'Usage: k_fold.py <source texts root folder>'
        exit(0)
    perform_kfold_cross_validation(sys.argv[1])
