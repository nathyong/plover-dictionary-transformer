#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Generator, List, NamedTuple
import subprocess


def str_tails(xs: str) -> Generator[str, None, None]:
    current = ""
    for x in xs:
        current += x
        yield current


steno_order = "STKPWHRAO*EUfrpblgts"

# class Stroke(NamedTuple):
#     keys: str
#     score: int


def stressed(seq) -> List[str]:
    return ["ˈ" + s for s in seq] + ["ˌ" + s for s in seq]


# fmt: off
vowels = [ "i", "y", "ɨ", "ʉ", "ɯ", "u", "ɪ", "ʏ", "ʊ", "e", "ø", "ɘ", "ɵ", "ɤ", "o", "ø̞", "ə", "o̞", "ɛ", "œ", "ɜ", "ɞ", "ʌ", "ɔ", "æ", "ɐ", "a", "ɶ", "ä", "ɑ", "ɒ", "ɑ̃", "ɔ̃"]

consonants = [ "m̥", "m", "ɱ", "n̼", "n̥", "n", "ɳ̊", "ɳ", "ɲ̊", "ɲ", "ŋ̊", "ŋ", "ɴ", "p", "b", "p̪", "b̪", "t̼", "d̼", "t", "d", "ʈ", "ɖ", "c", "ɟ", "k", "ɡ", "q", "ɢ", "ʡ", "ʔ", "ts", "dz", "t̠ʃ", "d̠ʒ", "ʈʂ", "ɖʐ", "tɕ", "dʑ", "pɸ", "bβ", "p̪f", "b̪v", "t̪θ", "d̪ð", "tɹ̝̊", "dɹ̝", "t̠ɹ̠̊˔", "d̠ɹ̠˔", "cç", "ɟʝ", "kx", "ɡɣ", "qχ", "ɢʁ", "ʡʢ", "ʔh", "s", "z", "ʃ", "ʒ", "ʂ", "ʐ", "ɕ", "ʑ", "ɸ", "β", "f", "v", "θ̼", "ð̼", "θ", "ð", "θ̠", "ð̠", "ɹ̠̊˔", "ɹ̠˔", "ɻ˔", "ç", "ʝ", "x", "ɣ", "χ", "ʁ", "ħ", "ʕ", "h", "ʋ̥", "ʋ", "ɹ̥", "ɹ", "ɻ̊", "ɻ", "j̊", "j", "ɰ̊", "ɰ", "ⱱ̟", "ⱱ", "ɾ̼", "ɾ̥", "ɾ", "ɽ̊", "ɽ", "ɢ̆", "ʡ̆", "ʙ̥", "ʙ", "r̥", "r", "ɽ̊r̥", "ɽr", "ʀ̥", "ʀ", "ʜ", "ʢ", "tɬ", "dɮ", "ʈɭ̊˔", "cʎ̝̊", "kʟ̝̊", "ɡʟ̝", "ɬ", "ɮ", "ɭ̊˔", "ɭ˔", "ʎ̝̊", "ʎ̝", "ʟ̝̊", "ʟ̝", "l̥", "l", "ɭ̊", "ɭ", "ʎ̥", "ʎ", "ʟ̥", "ʟ", "ʟ̠", "ɺ", "ɭ̆", "ʎ̆", "ʟ̆", "w"]

# all_phonemes_merged = [
#    # ah: father, palm
#    (['ɑː'] + stressed(['ɑ', 'ä']), [
#        Stroke(keys= 'A', score= 0.9), # best keys for this sound, but not the best sound for this keys
#        Stroke(keys= 'AU', score= 0.5),
#    ]),

#    ['ɑ', 'ä',], [
#        Stroke(keys= '', score= 0.9), # best keys for this sound, but not the best sound for this keys
#    ],

#    # a: bad, cat, ran
#    ['æ', 'æː', 'ɛə', 'a', 'ă'], [
#        Stroke(keys= 'A', score= 1),
#    ],

#    # ay: day, pain, heY, weight
#    ['eɪ', 'ɛi', 'ā'], [
#        Stroke(keys= 'AEU', score= 1),
#    ],

#    # eh: bed, egg, meadow
#    ['ɛ', 'ĕ', 'eː', 'e'], [ # eː and e could use confirmation
#        Stroke(keys= 'E', score= 1),
#    ],

#    # eh?
#    ['eː', 'e'], [
#        Stroke(keys= 'E', score= 0.8),
#    ],

#    # ee: ease, see, siege, ceiling
#    ['i', 'iː', 'ɪi', 'ē'], [
#        Stroke(keys= 'AOE', score= 1),
#    ],

#    # ee eh dipthong: canadIAn
#    ['iə'] , [
#        Stroke(keys= 'KWRA', score= 0.82),
#        Stroke(keys= 'KWRE', score= 0.72),
#    ],

#    # ee?: citY, everYday, manIa, gEography
#    # FIXME espeak doesn't produce: ['ɪː'], what soeund does it make?

#    # ih: sit, city, bit, will
#    ['ɪ', 'ĭ'], [
#        Stroke(keys= 'EU', score= 1),
#    ],
#    # TODO ['ɨ', 'ih'], # quicker, but still "ih" like rosEs # maybe make optional leave it out?

#    # my, rice, pie, hi, Mayan
#    ['aɪ', 'ɑi', 'ī'], [
#        Stroke(keys= 'AOEU', score= 1),
#    ],

#    # awe: maw baught caught
#    ['ɔ'], [
#        Stroke(keys= 'AU', score= 1),
#        Stroke(keys= 'O', score= 0.8),
#    ],

#    # About, brAzil  "uh" sound (but slightly "ah"-like) usually spelled with an A
#    ['ɐ'], [
#        Stroke(keys= 'U', score= 0.9), # best for sound, not best sound for keys
#        Stroke(keys= 'A', score= 0.8),
#        Stroke(keys= 'AU', score= 0.5),
#    ],

#    # TODO ['ɒ', ''] espeak doesn't produce this for en-us maybe it's found in wiktionary, figure out what it sounds like

#    # TODO ['ŏ', 'ah'], # TODO what sound is this?

#    # no, go, hope, know, toe
#    ['əʊ', 'oʊ', 'ō'], [
#        Stroke(keys= 'OE', score= 1),
#        Stroke(keys= 'O', score= 0.3),
#    ],

#    # o: hoarse, force # espeak only has this before "ɹ"
#    # TODO wiktionary might use "oː" for "awe"
#    ['oː', 'ō'], [
#        Stroke(keys= 'O', score= 1),
#        Stroke(keys= 'AU', score= 0.7),
#    ],

#    # espeak uses this for both "awe" as in "draw" and "o" as in "north"
#    # TODO see how wiktionary uses it
#    ['ɔː'], [
#        Stroke(keys= 'AU', score= 0.8),
#        Stroke(keys= 'O', score= 0.8),
#    ],

#    #law, caught
#    # ɔː, oː	ɔ, ɒ	ɒ	oː	ô
#    # TODO is ô "awe" or "o as in Or"?
#    # (ɔə) ɔː, oː	ɔɹ	oː	ôr	horse, north[5]

#    # oi: boy, noise
#    ['ɔɪ', 'oi', 'ɔɪ'], [
#        Stroke(keys= 'OEU', score= 1),
#    ],

#    # u: put, foot, wolf
#    ['ʊ', 'o͝o', 'ŏŏ'], [
#        # this sound doesn't map well...
#        Stroke(keys= 'AO', score= 0.7),
#        Stroke(keys= 'O', score= 0.6),
#        Stroke(keys= 'U', score= 0.5),
#    ],

#    # TODO figure out 'ɵː' sound if wiktionary uses it

#    # oo: lose, soon, through
#    ['uː', 'ʉː', 'u', 'o͞o', 'ōō'], [
#        Stroke(keys= 'AO', score= 1),
#    ],

#    # ow: house, now, tower
#    ['aʊ', 'ʌʊ', 'ou'], [
#        Stroke(keys= 'OU', score= 1),
#    ],

#    # uh: run, enough, up, other
#    ['ʌ', 'ŭ'], [
#        Stroke(keys= 'U', score= 1),
#    ],

#    # r: fur, blurry, bird, swerve[11][12]
#    ['ɜː', 'ɝ', 'ûr'], [
#        Stroke(keys= 'r', score= 0.9),
#        Stroke(keys= 'R', score= 0.8),
#        Stroke(keys= 'Ur', score= 0.7),
#    ],

#    # uh/ah: rosA's, About, Oppose
#    ['ə'], [
#        Stroke(keys= 'U', score= 0.85),
#        Stroke(keys= 'AU', score= 0.66),
#        Stroke(keys= 'O', score= 0.57),
#        Stroke(keys= 'A', score= 0.51),
#    ],

#    # r: winnER, entER, errOR, doctOR
#    ['ɚ', 'ər'], [
#        Stroke(keys= 'R', score= 0.9),
#        Stroke(keys= 'r', score= 0.91),
#        Stroke(keys= 'Ur', score= 0.7),
#    ],


#    # schwa: dEcember
#    ['ᵻ'], [
#        Stroke(keys= 'U', score= 0.63),
#        Stroke(keys= '', score= 0.88),
#        Stroke(keys= 'E', score= 0.33),
#        Stroke(keys= 'EU', score= 0.32),
#        Stroke(keys= 'A', score= 0.31),
#    ],

#    # croissant (french vowel at the end)
#    ['ɑ̃', 'ɔ̃'], [
#        Stroke(keys= 'OE', score= 0.76),
#        Stroke(keys= 'AU', score= 0.66),
#    ],

#    # consonants
#    # b: but, web, rubble
#    ['b'], [
#        Stroke(keys= 'PW', score= 1),
#        Stroke(keys= 'b', score= 1),
#    ],

#    # ch: chat, teach, nature
#    # FIXME why doesn't "premature" match this?
#    ['t͡ʃ', 'ch'], [
#        Stroke(keys= 'KH', score= 1),
#        Stroke(keys= 'fp', score= 0.9),
#    ],

#    # d: dot, idea, nod
#    ['d'], [
#        Stroke(keys= 'TK', score= 1),
#        Stroke(keys= 'd', score= 1),
#    ],

#    # f: fan, left, enough, photo
#    ['f'], [
#        Stroke(keys= 'TP', score= 1),
#        Stroke(keys= 'f', score= 1),
#    ],

#    # g: get, bag
#    ['ɡ', 'g'], [
#        Stroke(keys= 'TKPW', score= 1),
#        Stroke(keys= 'g', score= 1),
#    ],

#    # h: ham
#    ['h'], [
#        Stroke(keys= 'H', score= 1),
#    ],

#    # wh: which
#    ['ʍ', 'hw'], [
#        Stroke(keys= 'WH', score= 1),
#    ],

#    # j: joy, agile, age
#    ['d͡ʒ', 'dʒ'], [
#        Stroke(keys= 'SKWR', score= 1),
#        Stroke(keys= 'KWR', score= 0.2),
#    ],

#    # k: cat, tack
#    ['k'], [
#        Stroke(keys= 'K', score= 1),
#        Stroke(keys= 'bg', score= 1),
#    ],

#    # kh: loCH (in Scottish English)
#    ['x', 'ᴋʜ'], [
#        Stroke(keys= 'K', score= 0.69),
#        Stroke(keys= 'KH', score= 0.65),
#        Stroke(keys= 'bg', score= 0.79),
#        Stroke(keys= 'fp', score= 0.72),
#    ],

#    # l: left
#    ['l', 'ɫ'], [
#        Stroke(keys= 'HR', score= 1),
#        Stroke(keys= 'l', score= 1),
#    ],

#    # little
#    ['l̩', 'əl'], [
#        Stroke(keys= 'HR', score= 1),
#        Stroke(keys= 'l', score= 1),
#        Stroke(keys= 'El', score= 0.58),
#    ],

#    # m: man, animal, him
#    ['m'], [
#        Stroke(keys= 'PH', score= 1),
#        Stroke(keys= 'pl', score= 0.95),
#    ],

#    # m: spasm, prism
#    ['m̩', 'əm'], [
#        Stroke(keys= 'PH', score= 1),
#        Stroke(keys= 'pl', score= 0.95),
#        Stroke(keys= 'Epl', score= 0.55),
#    ],

#    # n: note, ant, pan
#    ['n'], [
#        Stroke(keys= 'TPH', score= 1),
#        Stroke(keys= 'pb', score= 1),
#    ],

#    # n: hidden
#    ['n̩', 'ən'], [
#        Stroke(keys= 'TPH', score= 1),
#        Stroke(keys= 'pb', score= 1),
#        Stroke(keys= 'Epb', score= 0.56),
#    ],

#    # ng: singer, ring
#    ['ŋ', 'ng'], [
#        Stroke(keys= 'pbg', score= 1),
#    ],

#    # p: pen, spin, top, apple
#    ['p'], [
#        Stroke(keys= 'P', score= 1),
#        Stroke(keys= 'p', score= 1),
#    ],

#    # r: run, very
#    ['ɹ', 'r'], [
#        Stroke(keys= 'R', score= 1),
#        Stroke(keys= 'r', score= 1),
#    ],

#    # s: set, list, ice
#    ['s'], [
#        Stroke(keys= 'S', score= 1),
#        Stroke(keys= 'f', score= 0.7),
#        Stroke(keys= 's', score= 1),
#        Stroke(keys= 'z', score= 0.81),
#    ],

#    # sh: ash, sure, ration
#    ['ʃ', 'sh'], [
#        Stroke(keys= 'SH', score= 1),
#        Stroke(keys= 'rb', score= 1),
#    ],

#    # t: ton, butt
#    ['t', 'ɾ', 'ʔ'], [
#        Stroke(keys= 'T', score= 1),
#        Stroke(keys= 't', score= 1),
#    ],

#    # th: thin, nothing, moth
#    ['θ', 'th'], [
#        Stroke(keys= 'TH', score= 1),
#        Stroke(keys= '*t', score= 0.9),
#    ],

#    # voiced th: this, father, clothe
#    ['ð', 'th'], [
#        Stroke(keys= 'TH', score= 0.99),
#        Stroke(keys= '*t', score= 0.89),
#    ],

#    # v: voice, navel
#    ['v'], [
#        Stroke(keys= 'SR', score= 1),
#        Stroke(keys= 'f', score= 0.6),
#    ],

#    # w: wet
#    ['w'], [
#        Stroke(keys= 'W', score= 1),
#    ],

#    # y: yes
#    ['j', 'ʲ', 'y'], [
#        Stroke(keys= 'KWR', score= 1),
#    ],

#    # zoo, quiz, rose
#    ['z', 'z'], [
#        Stroke(keys= 'z', score= 1),
#        Stroke(keys= 'STKPW', score= 0.84),
#        Stroke(keys= 'S', score= 0.64),
#        Stroke(keys= 's', score= 0.68),
#    ],

#    # voiced sh (zh): vision, treasure
#    ['ʒ', 'zh'], [
#        Stroke(keys= 'rb', score= 0.9),
#    ],

#    # french ê: crêpe
#    ['ɛː'], [
#        Stroke(keys= 'E', score= 0.87),
#        Stroke(keys= 'AEU', score= 0.74),
#    ],

#    # spanish ñ: piñata
#    ['ɲ'], [
#        Stroke(keys= 'pb/KWR', score= 1),
#        Stroke(keys= 'pb', score= 0.8),
#        Stroke(keys= 'TPH', score= 0.8),
#    ],


#    # space (word separator)
#    [' '], [
#        Stroke(keys= '/', score= 1), # idealy a stroke doesn't span multiple words
#        Stroke(keys= '', score= 0.4), # it's allowed to though
#    ],
# ]
# fmt: on

stressor = ["ˈ", "ˌ"]

extensor = "ː"
palatal = "ʲ"

all_symbols = vowels + consonants

schwa_like = ["ə", "ɚ", "ɛ", "ĕ", "e", "ɪ", "ĭ", "ɐ", "u"]


def is_ipa_token(tok: str) -> bool:
    """
    >>> is_ipa_token("d")
    True
    >>> is_ipa_token("ʈʂ")
    True
    >>> is_ipa_token("ɔː")
    True
    >>> is_ipa_token("ˈɔ")
    True
    >>> is_ipa_token("ː")
    False
    >>> is_ipa_token("dˈɪkʃənəɹɪ")
    False
    >>> is_ipa_token("nʲ")
    True
    """
    if any(tok == s for s in stressor):
        # just the stressor, short circuit
        return True

    if any(tok.startswith(s) for s in stressor):
        tok = tok[1:]

    if tok.endswith(extensor) or tok.endswith(palatal):
        tok = tok[:-1]

    return tok in all_symbols


def is_short_unstressed_syllable(sound: str) -> bool:
    """
    >>> is_short_unstressed_syllable("nɪd")  # arachNID
    True

    >>> is_short_unstressed_syllable("nɔɪd")  # arachNOID
    False

    >>> is_short_unstressed_syllable("lˈɪt")  # lit
    False

    >>> is_short_unstressed_syllable("ɹuːm")  # room
    True

    >>> is_short_unstressed_syllable("əɹənt")  # accelERANT
    True

    >>> is_short_unstressed_syllable("tʃuːəl")  # evenTUAL
    True
    """
    vowels_in_sound = filter(lambda c: c in vowels, sound)

    return (
        all(v in schwa_like for v in vowels_in_sound)
        and not any(x in sound for x in stressor)
    )


def tokenize(pronunciation: str) -> List[str]:
    """Accumulate with state machine

    >>> tokenize("dˈɪkʃənəɹɪ")
    ['d', 'ˈɪ', 'k', 'ʃ', 'ə', 'n', 'ə', 'ɹ', 'ɪ']
    >>> tokenize("bˈɑːɡɪn")
    ['b', 'ˈɑː', 'ɡ', 'ɪ', 'n']
    >>> tokenize("kwˈɑːsɑ̃")
    ['k', 'w', 'ˈɑː', 's', 'ɑ̃']
    """
    tokens: List[str] = []

    index = 0

    while index < len(pronunciation):
        token = None

        for cand in str_tails(pronunciation[index:]):
            if is_ipa_token(cand) or cand == " ":
                token = cand
            else:
                break

        assert token is not None, f"Encountered {cand} in {pronunciation}"

        tokens.append(token)
        index += len(token)

    return tokens


def word_to_ipa(word: str, *, voice: str = "en-gb-x-rp", cache=None) -> str:
    """
    >>> word_to_ipa("sacrifice")
    'sˈækɹɪfˌaɪs'
    """
    if cache is not None:
        try:
            return cache[word].decode("utf-8")
        except:
            pass

    ipa_str = (
        subprocess.check_output(["espeak", "-v", voice, "-qx", "-b1", "--ipa", word])
        .decode("utf-8")
        .strip()
    )

    if cache is not None:
        cache[word] = ipa_str

    return ipa_str
