import codecs
import xml.sax
import sys
import syntagrus2ruscorpora

MAX_SENTS = 1000000000

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
                                    syntagrus2ruscorpora.convert_grammar(self.__word_features.get('FEAT', '-')),
                                    self.__word_features.get('DOM', '-'),
                                    self.__word_features.get('LINK', '_')])
        print >>self.__out, string_to_flush.encode('utf-8')

class RuscorporaSynTagRus2MaltHandler(xml.sax.handler.ContentHandler):
    def __init__(self, out_destination):
        self.__out = out_destination
        self.__in_word = False
        self.__word_features = {}
        self.sentences_number = 0

    def characters(self, content):
        if self.__in_word:
            if 'form' not in self.__word_features:
                self.__word_features['form'] = content
            else:
                self.__word_features['form'] += content

    def startDocument(self):
        pass

    def endDocument(self):
        pass

    def startElement(self, tag, in_attrs):
        if tag == 'w':
            self.__in_word = True
        if tag == 'ana':
            self.__word_features = {attr_name: in_attrs[attr_name] for attr_name in in_attrs._attrs}
            if self.__word_features['dom'] == '_root':
                self.__word_features['dom'] = '0'

    def endElement(self, tag):
        if tag == 'se':
            self.__out.write('\n')
            self.sentences_number += 1
        if tag == 'w':
            self.__flush_word()
            self.__in_word = False

    def __flush_word(self):
        if self.sentences_number > MAX_SENTS:
            return
        string_to_flush = '\t'.join([self.__word_features.get('form', '-'),
                                    self.__word_features.get('gr', '-'),
                                    self.__word_features.get('dom', '-'),
                                    self.__word_features.get('link', '_')])
        print >>self.__out, string_to_flush.encode('utf-8')

def convert(in_source, in_destination):
    out = in_destination
    if isinstance(in_destination, str):
        out = codecs.getwriter('utf-8')(open(in_destination, 'wb'))
    handler = RuscorporaSynTagRus2MaltHandler(out)
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(in_source)

def main():
    if len(sys.argv) < 3:
        print 'Usage: syntagrus2malt.py <source> <destination>'
        exit(0)
    convert(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
