# -*- coding: utf-8 -*-

import re

# ruscorpora tags: http://ruscorpora.ru/corpora-morph.html
# syntagrus tags: http://ruscorpora.ru/instruction-syntax.html
import sys

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
    u'страд': 'pass' # otherwise 'act'
}

def convert_grammar(in_grammar_string):
    ruscorpora_grammar_tags = []
    syntagrus_grammar_tags = [tag.lower() for tag in in_grammar_string.split(' ')]
    for grammar_tag in syntagrus_grammar_tags:
        grammar_tag = grammar_tag.strip()
        if not grammar_tag:
            continue
        if grammar_tag in SYNTAGRUS_TO_RUSCORPORA_MAPPING:
            ruscorpora_grammar_tags.append(SYNTAGRUS_TO_RUSCORPORA_MAPPING[grammar_tag])
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

def convert(in_file, out_file):
    gramm_re = re.compile('FEAT="(.+?)"')
    for line in in_file:
        line = line.strip()
        for grammar in gramm_re.findall(line):
            ruscorpora_grammar = convert_grammar(grammar)
            line = line.replace('FEAT="%s"' % grammar, 'FEAT="%s"' % ruscorpora_grammar)
        print >>out_file, line
