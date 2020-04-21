#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Any, Deque, Generator, List, NamedTuple, Set, Tuple
import collections
import copy
import heapq
import itertools
import logging
import re

import ipa

steno_order = "1S2TK3PW4HR5A0O*EU-6fr7pb7lg8ts9dz"


_LOG = logging.getLogger(__name__)


class S:
    def __init__(self, stroke: str):
        """
        >>> S("TKPW-PB")
        'TKPW-PB'
        >>> S("-PB")
        '-PB'
        >>> S("TKPWEUPB")
        'TKPWEUPB'
        >>> S("TKPW-")
        'TKPW'
        >>> S("TKPW*PB")
        'TKPW*PB'
        >>> S("AOE")
        'AOE'
        """
        self.keys: Set[str] = set(normalise_stroke(stroke))

    def __repr__(self):
        return f"'{str(self)}'"

    def __str__(self):
        keys = list(self.keys)
        if not any(implicit_dash in keys for implicit_dash in "AO*EU"):
            keys.append("-")
        text = "".join(sorted(keys, key=lambda k: steno_order.index(k))).upper()
        if text.endswith("-"):
            text = text[:-1]
        return text

    def __len__(self):
        return len(self.keys)

    def __contains__(self, item):
        """
        >>> "S*" in S("SAO*PL")
        True
        >>> "*PL" in S("SAO*PL")
        True
        """
        if isinstance(item, str):
            item = S(item)
        return self.keys >= item.keys

    def __sub__(self, item):
        """
        >>> S("SAO*PL") - S("S")
        'AO*PL'

        >>> s = S("WAO")
        >>> s -= S("AO")
        >>> s
        'W'
        """
        assert (
            self.keys >= item.keys
        ), f"S.__sub__: Not all keys in {item} are present in {self}"
        new_stroke = copy.deepcopy(self)
        new_stroke.keys -= item.keys
        return new_stroke

    def __add__(self, item):
        """
        >>> S("SAOPL") + S("*")
        'SAO*PL'
        """
        assert not self.keys & item.keys, f"S.__add__: {self} and {item} overlap"
        new_stroke = copy.deepcopy(self)
        new_stroke.keys |= item.keys
        return new_stroke

    def __lt__(self, other) -> bool:
        """True if all keys (apart from star) in ``self`` are left of ``other``.
        >>> S("TW-") < S("AR")
        True
        >>> S("S*") < S("T-")
        True
        """
        if self.empty():
            return not other.empty()

        rightmost_1 = max(steno_order.index(k) for k in self.keys if k not in "-*")
        leftmost_2 = min(steno_order.index(k) for k in other.keys if k not in "-*")
        return not (self.keys & other.keys) and rightmost_1 < leftmost_2

    def __eq__(self, other) -> bool:
        """
        >>> S("") == S("")
        True
        """
        return self.keys == other.keys

    def empty(self) -> bool:
        """
        >>> S("").empty()
        True
        >>> S("*").empty()
        True
        >>> S("S-").empty()
        False
        """
        return self.keys <= {"*"}

    @staticmethod
    def from_brief(brief: str):
        """
        >>> S.from_brief("PHAPBLG/-BG")
        ['PHAPBLG', '-BG']
        """
        return [S(stroke) for stroke in brief.split("/")]


def normalise_stroke(stroke: str) -> str:
    """Doesn't handle

    >>> normalise_stroke("TKPW-PB")
    'TKPWpb'
    >>> normalise_stroke("-PB")
    'pb'
    >>> normalise_stroke("TKPWEUPB")
    'TKPWEUpb'
    >>> normalise_stroke("TKPW-")
    'TKPW'
    >>> normalise_stroke("TKPW*PB")
    'TKPW*pb'
    >>> normalise_stroke("S*")
    'S*'
    """
    pattern = re.compile(r"(S?T?K?P?W?H?R?)(-?A?O?\*?E?U?)(F?R?P?B?L?G?T?S?D?Z?)")

    match = pattern.fullmatch(stroke)
    assert match is not None, f"S is not in steno order: {stroke}"

    return "".join(
        (match.group(1), match.group(2).replace("-", ""), match.group(3).lower())
    )


known_phonemes_plover = [
    (["b"], ["PW", "-B"]),
    (["n"], ["TPH", "-PB"]),
    (["ɑː"], ["AR"]),
    (["ɡ", "g"], ["TKPW", "-G"]),
    (["t͡ʃ", "tʃ", "ch"], ["KH", "-FP"]),
    (["d"], ["TK", "-D"]),
    (["f"], ["TP", "-F"]),
    (["h"], ["H"]),
    (["ʍ", "hw"], ["WH"]),
    (["d͡ʒ", "dʒ"], ["SKWR", "-PBLG"]),
    (["k"], ["K", "-BG"]),
    #    # kh: loCH (in Scottish English)
    #    ['x', 'ᴋʜ'], [
    #        Stroke(keys= 'K', score= 0.69),
    #        Stroke(keys= 'KH', score= 0.65),
    #        Stroke(keys= 'bg', score= 0.79),
    #        Stroke(keys= 'fp', score= 0.72),
    #    ],
    (["l", "ɫ"], ["HR", "-L"]),
    (["m", "m̩"], ["PH", "-PL"]),
    (["n", "n̩"], ["TPH", "-PB"]),
    #    # ng: singer, ring
    #    ['ŋ', 'ng'], [
    #        Stroke(keys= 'pbg', score= 1),
    #    ],
    (["p"], ["P", "-P"]),
    (["ɹ", "r"], ["R", "-R"]),
    (["s"], ["S", "-S", "-F", "-Z"]),
    (["ʃ", "sh"], ["SH", "-RB"]),
    (["t", "ɾ", "ʔ"], ["T", "-T"]),
    (["θ", "th", "ð"], ["TH", "*T"]),
    (["v"], ["SR", "-F", "*F"]),
    (["w"], ["W"]),
    (["ɐ"], ["-ER", "-UR"]),
    (["j", "ʲ", "y"], ["KWR"]),
    (["z", "z"], ["S*", "-Z"]),
    (["lədʒɪ"], ["-LG"]),
    (["st"], ["*S"]),
    (["ɑ̃"], ["APBT"]),  # croissant
    (["mɔ̃"], ["-PLT"]),
]
known_phonemes_phoenix = [
    # vowels
    (["ɪ"], ["EU", "E"]),
    # consonants
    (["b"], ["PW", "-B"]),
    (["n"], ["TPH", "-PB"]),
    (["ɑː"], ["AR"]),
    (["ɡ", "g"], ["TKPW", "-G"]),
    (["t͡ʃ", "tʃ", "ch"], ["KH", "-FP"]),
    (["d"], ["TK", "-D"]),
    (["f"], ["TP", "-F"]),
    (["h"], ["H"]),
    (["ʍ", "hw"], ["WH"]),
    (["d͡ʒ", "dʒ"], ["SKWR", "-PBLG"]),
    (["k"], ["K", "-BG"]),
    (["l", "ɫ"], ["HR", "-L"]),
    (["m", "m̩"], ["PH", "-PL"]),
    (["n", "n̩"], ["TPH", "-PB"]),
    (["p"], ["P", "-P"]),
    (["ɹ", "r"], ["R", "-R"]),
    (["s"], ["S", "-S", "-SZ", "-Z"]),
    (["ʃ", "sh"], ["SH", "-GS"]),
    (["t", "ɾ", "ʔ"], ["T", "-T"]),
    (["θ", "th", "ð"], ["TH", "-GT"]),
    (["v"], ["SR", "-FB"]),
    (["w"], ["W"]),
    (["ɐ"], ["-ER", "-UR", "-R"]),
    (["j", "ʲ", "y"], ["KWR"]),
    (ipa.stressor, ["KWR"]),  # dangerous
    (["z", "z"], ["S*", "-Z"]),
    (["ɪŋ"], ["-G"]),
    (["ŋ"], ["-PBG"]),
    (["ŋk"], ["*PBG"]),
    (["ɡ"], ["-PBLG"]),  # dangerous
    (["st"], ["*S"]),
    (["ʃən"], ["-GZ"]),
    (["ʃəl"], ["-LGS"]),
    (["ˈiə"], ["-AOER"]),  # austere
    (["lədʒɪ"],  ["-LG"]),
]

phoneme_to_key = [
    (phoneme, S(key))
    for phonemes, keys in known_phonemes_plover
    for phoneme in phonemes
    for key in keys
]

phoneme_to_key_stars = [
    (phoneme, S(key))
    for phonemes, keys in known_phonemes_plover
    for phoneme in phonemes
    for key in keys
    if "*" in key
]

class T(NamedTuple):
    keys: S
    phonemes: str

    def __repr__(self) -> str:
        if self.keys or self.phonemes:
            return f"('{str(self.keys)}'=>'{self.phonemes}')"
        else:
            return "(/)"

    def __eq__(self, other) -> bool:
        """
        >>> S("") == S("")
        True
        >>> T(S(""), "") == T(S(""), "")
        True
        """
        return self.keys == other.keys and self.phonemes == other.phonemes



class N(NamedTuple):
    tokens: List[T]
    remaining_strokes: List[S]
    remaining_phonemes: str

    def metric(self) -> int:
        """Counts the number of unmatched keys (keys without a sound).

        >>> short = N([T("A", "a"), T("/", ""), T("S", "s")], [], "sisisss")
        >>> short.metric()
        5

        >>> long = N([T("S", "bdbdbdsus"), T("T", "t")], [], "ss")
        >>> long.metric()
        8
        """
        # treat each token as matching only one consonant (the others are trailing)
        consonant_tokens = [
            tok for tok in self.tokens if any(p in tok.phonemes for p in ipa.consonants)
        ]
        full_sound = (
            "".join(tok.phonemes for tok in self.tokens) + self.remaining_phonemes
        )
        all_consonants = [x for x in ipa.tokenize(full_sound) if x in ipa.consonants]
        return len(all_consonants) - len(consonant_tokens)

    def __lt__(self, other) -> bool:
        """Compare by unmatched consonant metric.
        """
        return self.metric() < other.metric()


def parse_phoneme_tokens(tokens: List[T]) -> List[str]:
    """
    >>> parse_phoneme_tokens(
    ...     [
    ...         T(S("PH"), "m"),
    ...         T(S("AOEU"),  "ˈaɪ"),
    ...         T(S(""), ""),
    ...         T(S("TPH"), "n"),
    ...         T(S("U"), "ə"),
    ...         T(S("-S"), "s"),
    ...         T(S(""), ""),
    ...     ]
    ... )
    ['mˈaɪ', 'nəs']
    """
    sounds = list()
    current_sound = ""

    for t in tokens:
        if not t.keys and not t.phonemes:
            # new stroke -- clear the accumulating current sound
            sounds.append(current_sound)
            current_sound = ""

        current_sound += t.phonemes

    return sounds


def compact_tokens(tokens: List[T]) -> List[T]:
    """Propagate sounds to the earliest stroke (fixing up stroke boundary
    issues).

    >>> compact_tokens([
    ...     T(S('PH'), 'm'),
    ...     T(S('AOEU'), ''),
    ...     T(S(''), ''),
    ...     T(S(''), 'ˈaɪ'),
    ...     T(S('TPH'), 'n'),
    ...     T(S('U'), 'ə'),
    ...     T(S('-S'), 's'),
    ...     T(S(''), '')
    ... ])
    [('PH'=>'m'), ('AOEU'=>'ˈaɪ'), (/), ('TPH'=>'n'), ('U'=>'ə'), ('-S'=>'s'), (/)]
    """
    _LOG.debug("compact_tokens: %s", tokens)

    new_tokens = list()

    acc_keys = S("")
    acc_phonemes = ""
    acc_blank = None

    phonemes_only = lambda t: t.phonemes and not t.keys
    keys_only = lambda t: t.keys and not t.phonemes
    empty_token = lambda t: not t.keys and not t.phonemes
    full_token = lambda t: t.keys and t.phonemes

    while tokens:
        current = tokens.pop(0)

        if not tokens:
            # current is last token
            new_tokens.append(current)

        elif full_token(current) or empty_token(current):
            new_tokens.append(current)

        elif keys_only(current):
            new_phonemes = ""

            # search ahead for a stroke with phonemes only
            for i in range(len(tokens)):
                if tokens[i].keys:
                    # reached another stroke
                    break
                if phonemes_only(tokens[i]):
                    new_phonemes = tokens[i].phonemes
                    del tokens[i]
                    break

            new_tokens.append(T(current.keys, new_phonemes))

        else:
            new_tokens.append(current)

    _LOG.debug("compact_tokens done: %s", new_tokens)

    return new_tokens


def tokenize_phonemes(pronunciation: str, strokes: str) -> List[T]:
    """
    >>> tokenize_phonemes("b", "PW-")
    [('PW'=>'b'), (/)]

    >>> tokenize_phonemes("ɪn", "EUPB")
    [('EU'=>'ɪ'), ('-PB'=>'n'), (/)]

    >>> tokenize_phonemes("ɪn", "-PB")
    [(''=>'ɪ'), ('-PB'=>'n'), (/)]

    >>> tokenize_phonemes("bˈɑːɡɪn", "PWAR/TKPW-PB")
    [('PW'=>'b'), (''=>'ˈ'), ('AR'=>'ɑː'), (/), ('TKPW'=>'ɡ'), (''=>'ɪ'), ('-PB'=>'n'), (/)]

    >>> tokenize_phonemes("bˈɑːɡɪn", "PWARG/-PB")
    [('PW'=>'b'), (''=>'ˈ'), ('AR'=>'ɑː'), ('-G'=>'ɡ'), (/), (''=>'ɪ'), ('-PB'=>'n'), (/)]

    >>> tokenize_phonemes("mˈaɪnəs", "PHAOEU/TPHUS")
    [('PH'=>'m'), ('AOEU'=>'ˈaɪ'), (/), ('TPH'=>'n'), ('U'=>'ə'), ('-S'=>'s'), (/)]

    >>> tokenize_phonemes("ɐksˈɛləɹənt", "ABG/SEL/RAPBT")
    [('A'=>'ɐ'), ('-BG'=>'k'), (/), ('S'=>'s'), ('E'=>'ˈɛ'), ('-L'=>'l'), (/), (''=>'ə'), ('R'=>'ɹ'), ('A'=>'ə'), ('-PB'=>'n'), ('-T'=>'t'), (/)]
    """
    q: List[N] = list()

    heapq.heappush(
        q,
        N(
            tokens=[],
            remaining_strokes=[S(s) for s in strokes.split("/")],
            remaining_phonemes=pronunciation,
        ),
    )

    while q:
        # (PW-, b)     (AR, a:) (/, ) (TKPW-, g) (-PB, in) (/, )
        # (AR/TKPW-PB)
        n = heapq.heappop(q)

        if n.remaining_phonemes == "" and not n.remaining_strokes:
            # reached the goal
            break

        if not n.remaining_strokes:
            # reached the end but still have phonemes: give up
            continue

        current_stroke = n.remaining_strokes[0]

        if not current_stroke:
            heapq.heappush(
                q,
                n._replace(
                    tokens=n.tokens + [T(S(""), "")],
                    remaining_strokes=n.remaining_strokes[1:],
                ),
            )

        if current_stroke.keys <= set("AO*EU"):
            # just vowels: move to next stroke
            heapq.heappush(
                q,
                n._replace(
                    tokens=n.tokens + [T(current_stroke, ""), T(S(""), "")],
                    remaining_strokes=n.remaining_strokes[1:],
                ),
            )

        try:
            last_stroke = n.tokens[-1].keys
        except IndexError:
            last_stroke = S("")

        for phoneme, stroke in phoneme_to_key:
            if (
                stroke in n.remaining_strokes[0]
                and phoneme in n.remaining_phonemes
                and last_stroke < stroke
            ):
                pre, post = n.remaining_phonemes.split(phoneme, maxsplit=1)

                updated_stroke = copy.deepcopy(current_stroke)
                new_tokens = list(n.tokens)

                # add a missing token entry for the vowels if this stroke has
                # 'switched' sides
                vowel_stroke = S("AOEU")
                if vowel_stroke < stroke:
                    vowel_stroke.keys &= updated_stroke.keys
                else:
                    vowel_stroke = S("")

                if pre:
                    new_tokens.append(T(vowel_stroke, pre))
                    updated_stroke -= vowel_stroke
                new_tokens.append(T(stroke, phoneme))
                updated_stroke -= stroke

                heapq.heappush(
                    q,
                    N(
                        tokens=new_tokens,
                        remaining_strokes=([updated_stroke] + n.remaining_strokes[1:]),
                        remaining_phonemes=post,
                    ),
                )
    else:
        return []

    # clean up tokens

    return compact_tokens(n.tokens)


def split_strokes(pronunciation: str, strokes: str) -> List[str]:
    return parse_phoneme_tokens(tokenize_phonemes(pronunciation, strokes))
