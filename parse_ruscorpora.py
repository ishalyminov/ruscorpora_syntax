import codecs
import os
import sys
import re
import shutil
import StringIO
import document_chunking
import malt_wrapper
from ruscorpora_tagging import tokenizer
from disamb import ruscorpora2plaintext, hunpos_wrapper
from ruscorpora_tagging.modules import task_list, config

''' Parsing Ruscorpora-formatted text '''

TRAINED_MODELS = { }

TEMP_FILES_DIR = './tmp_files'

def filter_punctuation(in_file_name):
    in_file = open(in_file_name)
    original_lines = codecs.getreader('utf-8')(in_file).readlines()
    in_file.close()
    filtered_lines = []
    for line in original_lines:
        tokens = line.split('\t')
        if line == '\n' or len(re.findall('\w+', tokens[0], re.UNICODE)):
            filtered_lines.append(line.strip())
    in_file = open(in_file_name, 'w')
    writer = codecs.getwriter('utf-8')(in_file)
    for line in filtered_lines:
        print >>writer, line
    in_file.close()


def plainify_file(in_filenames):
    (in_file_name, out_file_name) = in_filenames
    # tokenizing the input text
    tokenized_temp_buffer = StringIO.StringIO()
    tokenizer.convert((in_file_name, codecs.getwriter('utf-8')(tokenized_temp_buffer)))
    tokenized_temp_buffer.seek(0)

    # converting xml to hunpos-plaintext
    plain_file = open(out_file_name, 'w')
    ruscorpora2plaintext.convert(tokenized_temp_buffer, 'hunpos', plain_file)
    plain_file.close()

def analyze_file(in_filenames):
    print 'Analyzing %s' % in_filenames[0]
    (in_file_name, out_file_name) = in_filenames
    src_local_name = os.path.basename(in_file_name)

    # disambiguating plaintext with hunpos
    DISAMB_TEMP_FILENAME = os.path.join(TEMP_FILES_DIR,  src_local_name + '.disamb.temp')
    hunpos_wrapper.tag_file(in_file_name, TRAINED_MODELS['tagger'], DISAMB_TEMP_FILENAME)
    filter_punctuation(DISAMB_TEMP_FILENAME)

    # parsing syntactic dependencies in the disambed text
    parser_wrapper = malt_wrapper.MaltWrapper()
    malt_model = TRAINED_MODELS['parser']
    parser_wrapper.parse(DISAMB_TEMP_FILENAME, malt_model, out_file_name)

    os.remove(DISAMB_TEMP_FILENAME)

def process_file(in_filenames):
    (in_file_name, out_file_name) = in_filenames

    src_local_name = os.path.basename(in_file_name)
    # converting xml to hunpos-plaintext
    PLAINTEXT_TEMP_FILENAME = os.path.join(TEMP_FILES_DIR,  src_local_name + '.plaintext.temp')
    plainify_file((in_file_name, PLAINTEXT_TEMP_FILENAME))
    analyze_file((PLAINTEXT_TEMP_FILENAME, out_file_name))

    os.remove(PLAINTEXT_TEMP_FILENAME)

def process_directory(in_src_root, in_dst_root, in_handler):
    if not os.path.isdir(in_dst_root):
        os.makedirs(in_dst_root)
    for root, dirs, files in os.walk(in_src_root, followlinks=True):
        local_root = root[len(in_src_root) + 1:]
        result_root = os.path.join(in_dst_root, local_root)
        if not os.path.isdir(result_root):
            os.makedirs(result_root)
        for filename in files:
            src_filename = os.path.join(root, filename)
            dst_filename = os.path.join(result_root, filename)
            task_list.add_task(src_filename, dst_filename)
    task_list.execute_tasks(in_handler)
    task_list.clear_task_list()

def perform_parsing(in_src, out_dst):
    if os.path.isdir(TEMP_FILES_DIR):
        shutil.rmtree(TEMP_FILES_DIR)
    os.makedirs(TEMP_FILES_DIR)

    if os.path.isfile(in_src):
        process_file((in_src, out_dst))
    else:
        print 'Step 1 of 4: making plaintext files'
        PLAINTEXT_DIRECTORY = 'temp_plaintexts'
        documents_for_chunking_directory = PLAINTEXT_DIRECTORY
        if config.CONFIG['convert_to_plaintext']:
            process_directory(in_src, PLAINTEXT_DIRECTORY, plainify_file)
        else:
            documents_for_chunking_directory = in_src

        print 'Step 2 of 4: grouping texts in chunks for more effective analyzers invocation'
        CHUNKS_DIRECTORY = 'temp_filechunks'
        document_chunking.chunk_documents(documents_for_chunking_directory, CHUNKS_DIRECTORY)

        print 'Step 3 of 4: analyzing document chunks'
        ANALYZED_CHUNKS_DIRECTORY = 'temp_analyzed_chunks'
        process_directory(CHUNKS_DIRECTORY, ANALYZED_CHUNKS_DIRECTORY, analyze_file)

        print 'Step 4 of 4: splitting analyzed chunks into the initial document hierarchy'
        document_chunking.unchunk_documents(ANALYZED_CHUNKS_DIRECTORY, out_dst)

        for directory in [PLAINTEXT_DIRECTORY,
                          CHUNKS_DIRECTORY,
                          ANALYZED_CHUNKS_DIRECTORY,
                          TEMP_FILES_DIR]:
            if os.path.isdir(directory):
                shutil.rmtree(directory)

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print 'Usage: parse_ruscorpora.py <input file|root folder> <tagger model> <parser model> <output file|folder> [--convert_to_plaintext]'
        exit(0)

    config.CONFIG['convert_to_plaintext'] = \
        (len(sys.argv) == 6 and sys.argv[5] == '--convert_to_plaintext')

    TRAINED_MODELS['tagger'] = sys.argv[2]
    TRAINED_MODELS['parser'] = sys.argv[3]

    # setting config parameters for ruscorpora_tagging
    config.CONFIG['jobs_number'] = 8
    config.CONFIG['out_encoding'] = 'utf-8'
    perform_parsing(sys.argv[1], sys.argv[4])