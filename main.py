import sys
import json
from nltk.corpus import wordnet as wn
import pattern.en as en

def make_morph_set(lemma, pos):
    if pos == 'n':
      return set([lemma, en.pluralize(lemma)])
    elif pos == 'v':
      m = set(en.lexeme(lemma))
      m.add(lemma)
      return m
    elif pos == 'a':
      m = set([lemma])

      c = en.comparative(lemma)

      if c and not c.startswith('more '):
          m.add(c)

      s = en.superlative(lemma)

      if s and not s.startswith('most '):
          m.add(s)

      return m
    else:
      return set([lemma])


# {pos => {word => Set(lemma)}}
pos_to_word_to_lemmas = {}

# {pos => {lemma => Set(morph)}}
pos_to_lemma_to_morphs = {}

for synset in wn.all_synsets():
    pos = synset.pos()

    if (pos != 'n') and (pos != 'v') and (pos != 'a'):
        continue

    word_to_lemmas = pos_to_word_to_lemmas.get(pos)

    if not word_to_lemmas:
        word_to_lemmas = {}
        pos_to_word_to_lemmas[pos] = word_to_lemmas

    lemma_to_morphs = pos_to_lemma_to_morphs.get(pos)

    if not lemma_to_morphs:
        lemma_to_morphs = {}
        pos_to_lemma_to_morphs[pos] = lemma_to_morphs

    for lemma in synset.lemma_names():
        morphs = make_morph_set(lemma, pos)

        for morph in morphs:
            lemmas_for_morph = word_to_lemmas.get(morph)
            if not lemmas_for_morph:
                lemmas_for_morph = set()
                word_to_lemmas[morph] = lemmas_for_morph
            lemmas_for_morph.add(lemma)

        lemma_to_morphs[lemma] = morphs

pos_to_word_to_morphs = {}

for pos, word_to_lemmas in pos_to_word_to_lemmas.viewitems():
    word_to_morphs = {}
    pos_to_word_to_morphs[pos] = word_to_morphs

    lemma_to_morphs = pos_to_lemma_to_morphs[pos]

    for word, lemmas in word_to_lemmas.viewitems():
        morphs = word_to_morphs.get(word)
        if not morphs:
            morphs = set()
            word_to_morphs[word] = morphs

        for lemma in lemmas:
            morphs_for_lemma = lemma_to_morphs.get(lemma)
            if morphs_for_lemma:
                morphs |= morphs_for_lemma

        for morph in morphs:
            existing_morphs = word_to_morphs.get(morph)
            if existing_morphs:
                existing_morphs |= morphs
            else:
                word_to_morphs[morph] = morphs.copy()

    for word in word_to_morphs.keys():
        morphs = word_to_morphs[word]
        morphs.discard(word)

        if len(morphs) == 0:
            del word_to_morphs[word]
        else:
            word_to_morphs[word] = list(morphs)

out_file = open('morphs.json', 'w')
json.dump(pos_to_word_to_morphs, out_file)
out_file.close()