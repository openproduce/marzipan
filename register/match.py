#!/usr/bin/env/python
# match a search string against an index
# check for exact matches, substring matches, word matches, phonetic word
# matches, and low edit-distance word matches on words with correct first
# character; assume index size is small (say O(1000) entries ~ 3-4 words, less
# than 10k total words) so performance is not a big deal.

# This file is part of Marzipan, an open source point-of-sale system.
# Copyright (C) 2015 Open Produce LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import metaphone

edit_threshold = 2


def damerau_levenshtein(seq1, seq2):
    """Calculate Damerau-Levenshtein distance between sequences.

    This distance is the number of additions, deletions, substitutions,
    and transpositions needed to transform the first sequence into the
    second. Although generally used with strings, any sequences of
    comparable objects will work.

    Transpositions are exchanges of *consecutive* characters; all other
    operations are self-explanatory.

    This implementation is O(N*M) time and O(M) space, for N and M the
    lengths of the two sequences.
    """
    # codesnippet:D0DE4716-B6E6-4161-9219-2903BF8F547F
    # Conceptually, this is based on a len(seq1) + 1 * len(seq2) + 1 matrix.
    # However, only the current and two previous rows are needed at once,
    # so we only store those.
    oneago = None
    thisrow = list(range(1, len(seq2) + 1)) + [0]
    for x in range(len(seq1)):
        # Python lists wrap around for negative indices, so put the
        # leftmost column at the *end* of the list. This matches with
        # the zero-indexed strings and saves extra calculation.
        twoago, oneago, thisrow = oneago, thisrow, [0] * len(seq2) + [x + 1]
        for y in range(len(seq2)):
            delcost = oneago[y] + 1
            addcost = thisrow[y - 1] + 1
            subcost = oneago[y - 1] + (seq1[x] != seq2[y])
            thisrow[y] = min(delcost, addcost, subcost)
            # This block deals with transpositions
            if (x > 0 and y > 0 and seq1[x] == seq2[y-1]
                    and seq1[x-1] == seq2[y] and seq1[x] != seq2[y]):
                thisrow[y] = min(thisrow[y], twoago[y-2] + 1)
    return thisrow[len(seq2) - 1]


class Index:
    def __init__(self):
        self.literal = {}
        self.words = {}
        self.alpha_words = {}
        self.phonetic_words = {}

    def normalize_word(self, word):
        return word.lower()

    def is_stop_word(self, word):
        return False

    def normalize_key(self, key):
        words = [self.normalize_word(w) for w in key.split()]
        result = list([w for w in words[0:-1] if not self.is_stop_word(w)]) 
        if words:
            result.append(words[-1])
        return ' '.join(result)

    def add_item(self, key, value):
        "add a key and associated value(s) to index."
        canon_key = self.normalize_key(key)
        self.literal.setdefault(canon_key, []).append(value)

        for word in canon_key.split():
            self.words.setdefault(word, []).append(canon_key)
            self.alpha_words.setdefault(word[0], []).append(word)
            ph = metaphone.dm(word)
            self.phonetic_words.setdefault(ph[0], []).append(canon_key)
            if ph[1]:
                self.phonetic_words.setdefault(ph[1], []).append(canon_key)

    def match(self, search_string):
        "get set of matches sorted by plausibility"
        s = self.normalize_key(search_string)
        if not s:
            return []  # empty string doesn't match

        rk = {}
        if s in self.literal:  # exact literal match
            rk.setdefault(s, 0)

        for k in list(self.literal.keys()):  # exact literal substring match
            if k.find(s) != -1:
                rk.setdefault(k, 1)

#        words = s.split()
#        for w in words: # literal word matches
#            for k in self.words.get(w, []):
#                rk.setdefault(k, 2)
#
#        for w in words: # phonetic word matches
#            ph = metaphone.dm(w)
#            if ph[0]:
#                pk = self.phonetic_words.get(ph[0], [])
#                pk.extend(self.phonetic_words.get(ph[1], []))
#                for k in pk:
#                    rk.setdefault(k, 2)
#
#        for w in words: # low edit-distance word matches
#            for kw in self.alpha_words.get(w[0], []): # assume first character correct
#                if damerau_levenshtein(w, kw) < edit_threshold:
#                    for k in self.words.get(kw, []):
#                        rk.setdefault(k, 3)

        results = []
        for k, v in sorted(list(rk.items()), key=lambda k_v: (k_v[0], k_v[1])):
            results.extend(self.literal.get(k, []))
        return results


if __name__ == "__main__":
    index = Index()
    haystack = [
        "apple", "apple fuji", "apple gala", "apple organic",
        "banana", "odwalla", "naan", "basmati rice", "falafel", "alfafa",
        "uncle ben's wild rice", "brown rice", "persimmon", "pineapple",
        "daiquiri", "cpoy"
    ]
    for k in haystack:
        index.add_item(k, k)
    needles = [
        'ap', 'apple', 'fuji', 'fuji apple', 'foojey', 'bannana',
        'banana', 'rice', 'odwalal', 'flafel', 'falafel', 'felaful',
        'alf', 'lfafel', 'odwala', 'nan', 'persimon', 'pear', 'riec',
        'falofel', 'dakuri', 'daiuqiri', 'copy'
    ]
    for n in needles:
        print((n, index.match(n)));

