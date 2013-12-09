import os
import sys
from ruscorpora_tagging.modules.fs_walk import process_directory
import syntagrus2malt

def process_directory(in_dir_name):
    for (root, dirs, files) in os.walk(in_dir_name, followlinks=True):
        for filename in

def main():
    if len(sys.argv) < 3:
        print 'Usage: converter.py <sourcefile/directory> <destination file>'
        exit(0)
    (source, destination) = sys.argv[1:3]
    if os.path.isdir(source):
        process_directory(source, destination, syntagrus2malt.convert)
    else:
        syntagrus2malt.convert(source, destination)


if __name__ == '__main__':
    main()
