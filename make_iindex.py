"""
    Generate pickle file with inverted index
    INPUT_NAME  - name of Anna Karenina html file
    OUTPUT_NAME - name of pickle file with inverted index dictionary
"""
INPUT_NAME  = "karenina.htm"
IINDEX_OUTPUT = "iindex.pkl"
PARAGRAPHS_OUTPUT = "paragraphs.pkl"


from nltk import WordPunctTokenizer
from nltk.stem.snowball import RussianStemmer
import pickle
from HTMLParser import HTMLParser
import string
import sys, codecs


class KareninaParser(HTMLParser):

    def __init__(self):
        HTMLParser.__init__(self)
        self.inside_dd = False
        self.doc_id = 0
        self.token_count = 0
        self.token_sum_len = 0      
        self.iindex = {}
        self.paragraphs = []
        self.tokenizer = WordPunctTokenizer()
        self.stemmer = RussianStemmer()


    def handle_starttag(self, tag, attrs):
        if tag == "dd":
            self.inside_dd = True
            self.doc_id += 1
        else:
           self.inside_dd = False


    def handle_data(self, data):
        if self.inside_dd:
            self.paragraphs.append(data)
            terms = set()
            for token in self.tokenizer.tokenize(unicode(data.lower(), 'utf-8')):
                if token[0] in string.punctuation:
                    continue

                self.token_count += 1
                self.token_sum_len += len(token)                   

                term = self.stemmer.stem(token)                  

                if not term in terms:
                    terms.add(term)
                    if self.iindex.has_key(term):
                        self.iindex[term].append(self.doc_id)
                    else:
                        self.iindex[term] = [ self.doc_id ]


    def dump_iindex(self, output_name):
        output = open(output_name, 'wb')
        pickle.dump(self.iindex, output)
        output.close()


    def dump_paragraphs(self, output_name):
        output = open(output_name, 'wb')
        pickle.dump(self.paragraphs, output)
        output.close()


    def get_stat(self):
        term_sum_len = 0
        for term in self.iindex.keys():
            term_sum_len += len(term)

        term_count = len(self.iindex.keys())
        
        if not (term_count and self.token_count):
            self.stat = {}

        else:
            self.stat = {
                'token_count': self.token_count,
                'token_avg_len': self.token_sum_len/float(self.token_count),
                'term_count': term_count,
                'term_avg_len': term_sum_len/float(term_count)
            }

        return self.stat


    def print_iindex(self):
        for term in sorted(self.iindex.keys()):
            posting_list = self.iindex[term]
            print term
            print len(posting_list)
            print posting_list
            print '---------------------'


def make_iindex(INPUT_NAME, IINDEX_OUTPUT, PARAGRAPHS_OUTPUT):
    print "Making inverted index..."
    if not sys.stdout.isatty():
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    parser = KareninaParser()
    karenina = open(INPUT_NAME).read()
    parser.feed(karenina)
    parser.dump_iindex(IINDEX_OUTPUT)
    parser.dump_paragraphs(PARAGRAPHS_OUTPUT)

    print "Inverted index saved in " + IINDEX_OUTPUT
    print "Paragraphs saved in " + PARAGRAPHS_OUTPUT
    print 'statistics:'
    print parser.get_stat()   

if __name__ == '__main__':
    make_iindex(INPUT_NAME, IINDEX_OUTPUT, PARAGRAPHS_OUTPUT)

