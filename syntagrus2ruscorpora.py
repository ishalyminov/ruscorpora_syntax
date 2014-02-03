# -*- coding: utf-8 -*-

import re
import sys
import os
import StringIO
import codecs

# ruscorpora tags: http://ruscorpora.ru/corpora-morph.html
# syntagrus tags: http://ruscorpora.ru/instruction-syntax.html

SYNTAGRUS_TO_RUSCORPORA_MAPPING = {
    # parts of speech
    's': 's',
    'a': 'a',
    'v': 'v',
    'adv': 'adv',
    'num': 'num',
    'pr': 'pr',
    'com': 'com',
    'conj': 'conj',
    'part': 'part',
    'p': 'p',
    'intj': 'intj',
    'nid': 'nid',

    # animality
    u'од': 'anim',
    u'неод': 'inan',

    # gender
    u'муж': 'm',
    u'жен': 'f',
    u'муж-жен': 'm-f',
    u'сред': 'n',

    # number
    u'ед': 'sg',
    u'мн': 'pl',

    # case
    u'им': 'nom',
    u'род': 'gen',
    u'дат': 'dat', # 'dat2',
    u'вин': 'acc',
    u'твор': 'ins',
    u'пр': 'loc',
    u'парт': 'gen2', # 'acc2',
    u'местн': 'loc2',
    u'зв': 'voc', # 'adnum'

    # degree of comparison
    u'срав': 'comp',
    u'смяг': 'comp2',
    u'прев': 'supr',

    # adjective form
    u'кр': 'brev', # 'plen' otherwise

    # verb form
    u'инф': 'inf',
    u'прич': 'partcp',
    u'деепр': 'ger',

    # verb mood
    u'изъяв': 'indic',
    u'пов': 'imper',

    # verb aspect
    u'сов': 'pf',
    u'несов': 'ipf',

    # time
    u'непрош': 'fut',
    u'наст': 'praes',
    u'прош': 'praet',

    # noun form
    u'1-л': '1p',
    u'2-л': '2p',
    u'3-л': '3p',

    # voice
    u'страд': 'pass', # otherwise 'act'

    # special
    u'неправ': 'distort',
    u'NID': 'NONLEX',
    u'нестанд': '',
    u'сл': ''
}

def convert_grammar(in_grammar_string):
    ruscorpora_grammar_tags = []
    syntagrus_grammar_tags = [tag.lower() for tag in in_grammar_string.split(' ')]
    for grammar_tag in syntagrus_grammar_tags:
        grammar_tag = grammar_tag.strip()
        if not grammar_tag:
            continue
        if grammar_tag in SYNTAGRUS_TO_RUSCORPORA_MAPPING:
            syntagrus_tag = SYNTAGRUS_TO_RUSCORPORA_MAPPING[grammar_tag]
            if syntagrus_tag:
                ruscorpora_grammar_tags.append(syntagrus_tag)
        else:
            print >>sys.stderr, grammar_tag.encode('utf-8')
            ruscorpora_grammar_tags.append(grammar_tag)
    # processing mutually exclusive tags
    if 'a' in ruscorpora_grammar_tags and 'brev' not in ruscorpora_grammar_tags:
        ruscorpora_grammar_tags.append('plen')
    if 'v' in ruscorpora_grammar_tags and 'pass' not in ruscorpora_grammar_tags:
        ruscorpora_grammar_tags.append('act')
    pos_tag = ruscorpora_grammar_tags[0].upper()
    return ','.join([pos_tag] + sorted(ruscorpora_grammar_tags[1:]))

def build_word_tag(in_word_attrs, in_word_form):
    attribute_mapping = {'FEAT': 'gr', 'LEMMA': 'lex'}
    result_tag = '<w><ana'
    for attribute_name, attribute_value in re.findall('(.+?)="(.+?)"', in_word_attrs):
        attribute_name = attribute_name.strip()
        mapped_attribute = attribute_name.lower()
        if attribute_name in attribute_mapping:
            mapped_attribute = attribute_mapping[attribute_name]
        result_tag += ' %s="%s"' % (mapped_attribute, attribute_value)
    result_tag += '/>%s</w>' % in_word_form
    return result_tag

def convert(in_file, out_file):
    gramm_re = re.compile('FEAT="(.+?)"')
    for line in in_file:
        line = line.strip()
        for grammar in gramm_re.findall(line):
            ruscorpora_grammar = convert_grammar(grammar)
            line = line.replace('FEAT="%s"' % grammar, 'FEAT="%s"' % ruscorpora_grammar)
        print >>out_file, line

def convert_directory(in_texts_root, in_result_root):
    if not os.path.isdir(in_result_root):
        os.makedirs(in_result_root)
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        local_root = root[len(in_texts_root) + 1:]
        result_root = os.path.join(in_result_root, local_root)
        if not os.path.isdir(result_root):
            os.makedirs(result_root)
        for filename in files:
            if os.path.splitext(filename)[1] == '.tgt':
                text_buffer = StringIO.StringIO()
                tgt_file_name = os.path.join(root, filename)
                convert(codecs.getreader('cp1251')(open(tgt_file_name)), text_buffer)
                text_buffer.seek(0)
                out_file_name = os.path.join(result_root, filename)
                out_stream = codecs.getwriter('utf-8')(open(out_file_name, 'w'))
                for line in text_buffer:
                    line = line.strip()
                    line = line.replace('encoding="windows-1251"', 'encoding="utf-8"')
                    line = line.replace('</S>', '</se>')
                    line = line.replace('<S', '<se')
                    # fantom words
                    for (tag_region, word_attrs) in re.findall('(<W(.*?)/>)', line):
                        line = line.replace(tag_region, build_word_tag(word_attrs, '-'))
                    for (tag_region, word_attrs, word_form) in re.findall('(<W(.*?)>(.*?)</W>)', line):
                        line = line.replace(tag_region, build_word_tag(word_attrs, word_form))
                    print >>out_stream, line
                out_stream.close()

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage: syntagrus2ruscorpora.py <source texts root> <result root>'
        exit(0)
    convert_directory(os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]))
