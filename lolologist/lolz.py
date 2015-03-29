#!/usr/bin/env python
#
# LOLspeak translator library
# Created by Stephen Newey
# Modified w/JSON & Python 3 support by Aru Sahni <arusahni@gmail.com>
#
# Python stuff, copyright (c)2008 Stephen Newey
# Inspired by Dave Dribin's Ruby library lolspeak (http://www.dribin.org/dave/lolspeak/)
# tranzlator.yml dictionary by Dave Dribin
#
# python code licensed under the Mozilla Public License v1.1.
# http://www.mozilla.org/MPL/MPL-1.1.html
#
#
from __future__ import print_function

import json, sys, os.path, re

DEFAULT_LOLZ_DB = os.path.join(os.path.split(__file__)[0], 'tranzlator.json') # Change in setup.py, too

class Tranzlator(object):
    """
    LOLz Translator Class
    Uses a YAML DB of translations
    Falls back to some heuristic analysis
    Provides word lookup with caching
    Provides sentence lookup.

    >>> t = Tranzlator()
    >>> t.translate_sentence("Hello. My English is perfect and produces a lot of statisfaction with intentional misspellings.")
    'y halo thar. mah english iz perfik an producez lot ov statisfacshun wif intentional misspellingz.'
    >>> t.cached
    {'': '', 'statisfaction': 'statisfacshun', 'lot': 'lot', 'english': 'english', 'intentional': 'intentional', 'misspellings': 'misspellingz'}

    """

    # simple search/replace of word endings
    easy_regex = [
            (re.compile("(.*)ed$"), 'd'),
            (re.compile("(.*)ing$"), 'in'),
            (re.compile("(.*)ss$"), 's'),
            (re.compile("(.*)er$"), 'r'),
            ]

    # more complicated search/replace operations
    regex = {
            'apostrophy' : re.compile('(?P<prefix>.*)(?P<suffix>[\']\w*)'),
            'tion' : re.compile("(.*)tion(s?)$"),
            'stoz' : re.compile("^([\w]+)s$"),
            'ous' : re.compile("ous$"),
            }

    def __init__(self, db=DEFAULT_LOLZ_DB, heuristics=True):
        super(Tranzlator, self).__init__()
        self.heuristics = heuristics
        self.cached = {}
        try:
            f = open(db, 'r')
        except:
            raise IOError("Unable to open lolz database: %s" % db)
        try:
            self.db = json.load(f)
        except:
            raise IOError("Specified lolz database unreadable.")
        f.close()

    def translate_word(self, word):
        # lower case lolz pleaz, ph is pronounces f!
        word = word.lower()
        word = word.replace('ph', 'f')

        # fastest, check the cache...
        if word in self.cached:
            return self.cached[word]

        # easiest first, look in dictionary
        if word in self.db:
            return self.db[word]

        # not found, perhaps a possesive apostrophy or the like?
        if self.regex['apostrophy'].search(word):
            result = self.regex['apostrophy'].search(word).groupdict()
            if result['prefix'] in self.db:
                self.cached[word] = '%s%s' % (self.db[result['prefix']], result['suffix'])
                return self.cached[word]

        # no matches? try heuristics unless we've been told otherwise
        if self.heuristics is True:
            for regex, replace in self.easy_regex:
                match = regex.search(word)
                if match:
                    self.cached[word] = match.group(1)+replace
                    return self.cached[word]
            tion = self.regex['tion'].search(word)
            if tion:
                self.cached[word] = tion.group(1)+'shun'+tion.group(2)
                return self.cached[word]
            stoz = self.regex['stoz'].search(word)
            if stoz and not self.regex['ous'].search(word):
                self.cached[word] = stoz.group(1)+'z'
                return self.cached[word]

        # no matches, leave it alone!
        self.cached[word] = word
        return word

    def translate_sentence(self, sentence):
        new_sentence = ''
        # reminder to self...
        # ([\w]*) - match 0 or more a-zA-Z0-9_ group
        # ([\W]*) - match 0 or more non-(see above) group
        for word, space in re.findall("([\w]*)([\W]*)", sentence):
            word = self.translate_word(word)
            if word != '':
                new_sentence += word + space
        return new_sentence

def _test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == '-test':
            _test()
        else:
            tranz = Tranzlator()
            print(tranz.translate_sentence(' '.join(sys.argv[1:])))
    else:
        print("Usage: %s text to tranzlate" % sys.argv[0])
