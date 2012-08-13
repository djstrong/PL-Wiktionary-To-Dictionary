import os
import glob

def file_len(fname):
    with open(fname, 'r') as f:
        for i, l in enumerate(f):
            pass
    return i + 1

link='https://github.com/downloads/djstrong/PL-Wiktionary-To-Dictionary/'
link='https://raw.github.com/djstrong/PL-Wiktionary-To-Dictionary/master/dictionaries/'
for fp in glob.glob('*polish.txt'):
    i = fp.find('_polish.txt')
    lang = ' '.join([x.capitalize() for x in fp[:i].split('_')])
    print '* '+lang+' to Polish dictionary ('+ str(file_len(fp)/1000)+'k) - '+link+fp
    
for fp in glob.glob('polish_*.txt'):
    i = fp.find('.txt')
    lang = ' '.join([x.capitalize() for x in fp[7:i].split('_')])
    print '* Polish to '+lang+' dictionary ('+ str(file_len(fp)/1000)+'k) - '+link+fp