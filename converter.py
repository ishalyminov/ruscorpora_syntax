import os
import sys
import syntagrus2malt

def process_directory(in_dir_name, in_destination, in_handler):
    for (root, dirs, files) in os.walk(in_dir_name, followlinks=True):
        for filename in files:
            in_handler(open(os.path.join(root, filename)), in_destination)
        in_destination.write('\n')

def main():
    if len(sys.argv) < 2:
        print 'Usage: converter.py <sourcefile/directory>'
        exit(0)
    source = sys.argv[1]
    if os.path.isdir(source):
        process_directory(source, sys.stdout, syntagrus2malt.convert)
    else:
        syntagrus2malt.convert(source, sys.stdout)


if __name__ == '__main__':
    main()
