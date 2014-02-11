import os

class DocumentChunker(object):
    def __init__(self):
        self.__chunk_capacity = 100
        self.__chunks_number = 0
        self.__chunk_size = 0
        self.__chunk_stream = None
        self.__dst_root = None

    def chunk_documents(self, in_src_root, in_dst_root, in_chunk_capacity=500):
        self.__dst_root = in_dst_root
        self.__chunk_capacity = in_chunk_capacity
        if not os.path.isdir(in_dst_root):
            os.makedirs(in_dst_root)
        for root, dirs, files in os.walk(in_src_root, followlinks=True):
            local_root = root[len(in_src_root) + 1:]
            for filename in files:
                local_filename = os.path.join(local_root, filename)
                global_filename = os.path.join(root, filename)
                self.__flush_file(local_filename, global_filename)
        self.__close_chunk()

    def unchunk_documents(self, in_src_root, in_dst_root):
        for root, dirs, files in os.walk(in_src_root, followlinks=True):
            for filename in files:
                global_filename = os.path.join(root, filename)
                self.__unchunk_document(global_filename, in_dst_root)

    def __unchunk_document(self, in_filename, in_dst_root):
        self.__read_open_new_chunk(in_filename)
        for chunked_document in self.__read_chunk_documents():
            document_file = os.path.join(in_dst_root, chunked_document['name'])
            dst_dir = os.path.dirname(document_file)
            if not os.path.isdir(dst_dir):
                os.makedirs(dst_dir)
            dst_file = open(document_file, 'w')
            dst_file.writelines(chunked_document['lines'])
            dst_file.close()

    def __read_chunk_documents(self):
        current_chunk = {}
        for line in self.__chunk_stream:
            if line.startswith('FILENAME:'):
                if len(current_chunk):
                    yield current_chunk
                current_chunk = {}
                current_chunk['name'] = line.strip().split('\t')[0].replace('FILENAME:', '')
                current_chunk['lines'] = []
            else:
                if line == '\n':
                    if not len(current_chunk['lines']) or current_chunk['lines'][-1] == '\n':
                        continue
                current_chunk['lines'].append(line)
        if len(current_chunk):
            yield(current_chunk)


    def __flush_file(self, in_local_filename, in_global_filename):
        if not self.__chunk_stream:
            self.__write_open_new_chunk()
        print >>self.__chunk_stream, 'FILENAME:' + in_local_filename
        print >>self.__chunk_stream, '\n'
        print >>self.__chunk_stream, ''.join(open(in_global_filename).readlines())
        print '\n\n\n\n'

        self.__chunk_size += 1
        if self.__chunk_size == self.__chunk_capacity:
            self.__close_chunk()

    def __write_open_new_chunk(self):
        chunk_filename = os.path.join(self.__dst_root, 'chunk_%d.tab' % self.__chunks_number)
        self.__chunk_stream = open(chunk_filename, 'w')
        self.__chunk_size = 0

    def __read_open_new_chunk(self, in_filename):
        self.__chunk_stream = open(in_filename)

    def __close_chunk(self):
        if self.__chunk_stream:
            self.__chunk_stream.close()
            self.__chunk_stream = None
            self.__chunks_number += 1


def chunk_documents(in_src_dir, in_dst_dir):
    if not os.path.isdir(in_dst_dir):
        os.makedirs(in_dst_dir)
    chunker = DocumentChunker()
    chunker.chunk_documents(in_src_dir, in_dst_dir)

def unchunk_documents(in_src_dir, in_dst_dir):
    if not os.path.isdir(in_dst_dir):
        os.makedirs(in_dst_dir)
    chunker = DocumentChunker()
    chunker.unchunk_documents(in_src_dir, in_dst_dir)