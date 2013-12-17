# -*- coding: utf-8 -*-

import codecs
import xml.sax
import sys

# ruscorpora tags: http://ruscorpora.ru/corpora-morph.html
# syntagrus tags: http://ruscorpora.ru/instruction-syntax.html
SYNTAGRUS_TO_RUSCORPORA_MAPPING = {
    # gender
    'муж': 'm',
    'жен': 'f',
    'муж-жен': 'm-f',
    'сред': 'n',

    # number
    'ед': 'sg',
    'мн': 'pl',

    # case
    'им': 'nom',
    'род': 'gen',
    'дат': 'dat',
        # 'dat2',
    'вин': 'acc',
    'твор': 'ins',
    'пр': 'loc',
    'парт': 'gen2',
        # 'acc2',
    'мест': 'loc2',
    'зв': 'voc',
        # 'adnum

    # degree of comparison
    'срав': 'comp',
    'смяг': 'comp2',
    'прев': 'supr',

    # adjective form
    'кр': 'brev', # 'plen' otherwise

    # verb form
    'инф': 'inf',
    'прич': 'partcp',
    'дееприч': 'ger',

    # verb mood
    'изъяв': 'indic',
    'пов': 'imper',

    # verb aspect
    'сов': 'pf',
    'несов': 'ipf',

    # time
    'непрош': 'fut',
    'наст': 'praes',
    'прош': 'praet',

    # noun form
    '1-л': '1p',
    '2-л': '2p',
    '3-л': '3p',

    # voice
    'страд': 'pass' # otherwise 'act'
}

class SynTagRus2MaltHandler(xml.sax.handler.ContentHandler):
    def __init__(self, out_destination):
        self.__out = out_destination
        self.__in_word = False
        self.__word_features = {}

    def characters(self, content):
        if self.__in_word:
            if 'FORM' not in self.__word_features:
                self.__word_features['FORM'] = content
            else:
                self.__word_features['FORM'] += content

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, tag, in_attrs):
        if tag == 'W':
            self.__in_word = True
            self.__word_features = {attr_name: in_attrs[attr_name] for attr_name in in_attrs._attrs}
            if self.__word_features['DOM'] == '_root':
                self.__word_features['DOM'] = '0'

    def endElement(self, tag):
        if tag == 'S':
            self.__out.write('\n')
        if tag == 'W':
            self.__flush_word()
        self.__in_word = False

    def __flush_word(self):
        string_to_flush = '\t'.join([self.__word_features.get('FORM', '-'),
                                    '.'.join(self.__word_features.get('FEAT', '-').split(' ')),
                                    self.__word_features.get('DOM', '-'),
                                    self.__word_features.get('LINK', '_')])
        print >>self.__out, string_to_flush.encode('utf-8')


def convert(in_source, in_destination):
    out = in_destination
    if isinstance(in_destination, str):
        out = codecs.getwriter('utf-8')(open(in_destination, 'wb'), 'xmlcharrefreplace')
    handler = SynTagRus2MaltHandler(out)
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(in_source)

def main():
    if len(sys.argv) < 3:
        print 'Usage: syntagrus2conll.py <source> <destination>'
        exit(0)
    convert(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
