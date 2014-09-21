# coding: utf-8
from pyparsing import infixNotation, opAssoc, Keyword, Word, alphas
import pickle
from nltk.stem.snowball import RussianStemmer
from make_iindex import make_iindex
import os, sys

KARENINA_NAME = 'karenina.htm'
IINDEX_NAME = 'iindex.pkl'
PARAGRAPHS_NAME = 'paragraphs.pkl'

class BoolOperand(object):    
    def __init__(self,t):
        global STEMMER, IINDEX
        term = STEMMER.stem(t[0])    
        self.value = IINDEX.get(term, [])

    def calcop(self):
        return self.value
   

class BoolBinOp(object):
    def __init__(self,t): 
        self.larg, self.rarg = tuple(t[0][0::2])

    def calcop(self):
        return self.calc(self.larg.calcop(), self.rarg.calcop())
    

class BoolAnd(BoolBinOp):
    def calc(self, docs1, docs2):
	res = []
	i = 0
	j = 0
	n = len(docs1)
	m = len(docs2)

	while i<n and j<m:
	    if docs1[i] == docs2[j]:
	        res.append(docs1[i])
	        i += 1
	        j += 1
	    elif docs1[i] < docs2[j]:
	        i += 1
	    else:
	        j += 1
	    	
	return res


class BoolOr(BoolBinOp):
    def calc(self, docs1, docs2):
	res = []
	i = 0
	j = 0
	n = len(docs1)
	m = len(docs2)
	while i<n and j<m:
	    if docs1[i] < docs2[j]:
	        res.append(docs1[i])
	        i += 1
	    elif docs1[i] > docs2[j]:
	        res.append(docs2[j])
	        j += 1
	    else:
	        i += 1

	while i<n:
	    res.append(docs1[i])
	    i += 1

	while j<m:
	    res.append(docs2[j])
	    j += 1
	    	
	return res


class BoolNot(object):
    def __init__(self,t):
        self.arg = t[0][1]

    def calcop(self):
        global ALL_DOC_IDS
        docs = self.arg.calcop()
        res = []
        for d in ALL_DOC_IDS:
            if not (d in docs):
                res.append(d)

        return res


def eval_query(query_str):
    global WORD_CHARS
    boolOperand = Word(WORD_CHARS)
    boolOperand.setParseAction(BoolOperand)

    boolExpr = infixNotation( boolOperand,
        [
             ("not", 1, opAssoc.RIGHT, BoolNot),
             ("and", 2, opAssoc.LEFT,  BoolAnd),
             ("or",  2, opAssoc.LEFT,  BoolOr),
        ]
    )

    return boolExpr.parseString(query_str.lower())[0].calcop()


def init():
    global IINDEX, WORD_CHARS, ALL_DOC_IDS, STEMMER
    inp = open(IINDEX_NAME, 'rb')
    IINDEX = pickle.load(inp)
    m = 0
    for term, posting_list in IINDEX.items():
        curr_m = max(posting_list)
        if curr_m > m:
     	    m = curr_m
    inp.close()

    ALL_DOC_IDS = [ i for i in xrange(1,m+1) ]
    STEMMER = RussianStemmer()
    WORD_CHARS = u'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщьыъэюя'


def read_paragraphs():
    inp = open(PARAGRAPHS_NAME, 'rb')
    paragraphs = pickle.load(inp)
    inp.close()
    return paragraphs


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "usage: ./search.py 'семья AND друг'"
        exit()

    query = sys.argv[1].decode('utf-8')
    filenames = os.listdir('.')
    if not (PARAGRAPHS_NAME in filenames and IINDEX_NAME in filenames):
        make_iindex(KARENINA_NAME, IINDEX_NAME, PARAGRAPHS_NAME)

    init()
    paragraphs = read_paragraphs()
    paragraph_nums = eval_query(query)    
    for num in paragraph_nums:
        print num, paragraphs[num-1]

