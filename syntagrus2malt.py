import codecs
import os
import xml.sax
import sys
import syntagrus2ruscorpora

MAX_SENTS = 1000000000
WRITE_GRAMMAR_TAGS = False
LOWERCASE = True


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
        self.__word_features['FEAT'] = syntagrus2ruscorpora.convert_grammar(self.__word_features.get('FEAT', '-'))
        for key in self.__word_features:
            if LOWERCASE:
                self.__word_features[key] = self.__word_features[key].lower()
            if key == 'FEAT' and not WRITE_GRAMMAR_TAGS:
                self.__word_features[key] = self.__word_features[key].split(',')[0]

        string_to_flush = '\t'.join([self.__word_features.get('FORM', '-'),
                                     self.__word_features.get('FEAT', '-'),
                                     self.__word_features.get('DOM', '-'),
                                     self.__word_features.get('LINK', '_')])
        print >>self.__out, string_to_flush


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
        for key in self.__word_features:
            if LOWERCASE:
                self.__word_features[key] = self.__word_features[key].lower()
            if key == 'gr' and not WRITE_GRAMMAR_TAGS:
                self.__word_features[key] = self.__word_features[key].split(',')[0]

        string_to_flush = '\t'.join([self.__word_features.get('form', '-'),
                                    self.__word_features.get('gr', '-'),
                                    self.__word_features.get('dom', '-'),
                                    self.__word_features.get('link', '_')])
        print >>self.__out, string_to_flush


def convert(in_source, out_destination, in_format):
    out = out_destination
    if isinstance(out_destination, str):
        out = codecs.getwriter('utf-8')(open(out_destination, 'wb'))
    handler = SynTagRus2MaltHandler(out) if in_format == 'syntagrus' else RuscorporaSynTagRus2MaltHandler(out)
    parser = xml.sax.make_parser()
    parser.setContentHandler(handler)
    parser.parse(in_source)


def convert_directory(in_texts_root, in_result_root, in_format):
    if not os.path.isdir(in_result_root):
        os.makedirs(in_result_root)
    for root, dirs, files in os.walk(in_texts_root, followlinks=True):
        local_root = root[len(in_texts_root) + 1:]
        result_root = os.path.join(in_result_root, local_root)
        if not os.path.isdir(result_root):
            os.makedirs(result_root)
        for filename in files:
            if os.path.splitext(filename)[1] == '.tgt':
                tgt_file_name = os.path.join(root, filename)
                out_file_name = os.path.join(result_root, filename)
                print '%s -> %s' % (tgt_file_name, out_file_name)
                out_stream = codecs.getwriter('utf-8')(open(out_file_name, 'w'))
                convert(tgt_file_name, out_stream, in_format)
                out_stream.close()


def main():
    if len(sys.argv) < 4:
        print 'Usage: syntagrus2malt.py <source> <destination> syntagrus/ruscorpora_syntagrus'
        exit()
    source, destination, format = sys.argv[1:4]
    if os.path.isdir(source):
        convert_directory(source, destination, format)
    else:
        convert(source, destination, format)

if __name__ == '__main__':
    main()
