INPUT_NAME = 'synonims.txt'
OUTPUT_NAME = 'synonims.pkl'
from nltk.stem.snowball import RussianStemmer
import string
import pickle

stemmer = RussianStemmer()

def is_correct(word):
    if ' ' in word:
        return False

    for punct in string.punctuation:
        if punct in word:
            return False

    return True

def get_synonims(inp_name):    
    synonims = {}
    for line in open(inp_name):
        words = line.decode('ptcp154').rstrip().split('|')
        if len(words) != 2:
            continue
  
        if not is_correct(words[0]):
            continue

        word = stemmer.stem(words[0])
        if not synonims.has_key(word):
            synonims[word] = set()

        for s in words[1].split(','):
            if not is_correct(s):
                continue
            synonims[word].add(stemmer.stem(s))

    return synonims
         

def dump_synonims(synonims, output_name):
    output = open(output_name, 'wb')
    pickle.dump(synonims, output)
    output.close()


def make_synonims(INPUT_NAME, OUTPUT_NAME):
    synonims = get_synonims(INPUT_NAME)
    dump_synonims(synonims, OUTPUT_NAME)

if __name__ == '__main__':
    make_synonims(INPUT_NAME, OUTPUT_NAME)    
