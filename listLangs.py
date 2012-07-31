import os
import glob

def file_len(fname):
    with open(fname, 'r') as f:
        for i, l in enumerate(f):
            pass
    return i + 1

link='https://github.com/downloads/djstrong/PL-Wiktionary-To-Dictionary/'
for fp in glob.glob('*polish.txt'):
    i = fp.find('_polish.txt')
    lang = ' '.join([x.capitalize() for x in fp[:i].split('_')])
    print '* '+lang+' to Polish dictionary ('+ str(file_len(fp)/1000)+'k) - '+link+fp
    
    