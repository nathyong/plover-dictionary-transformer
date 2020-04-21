#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Transforms a Plover Theory dictionary to VOP style.
"""

from pathlib import Path
from typing import Dict, Generator
import dbm
import json
import re
import string

from stroke import S, T, tokenize_phonemes, parse_phoneme_tokens
import ipa

# DICTIONARY = Path(__file__).parent / "dict.json"
DICTIONARY = Path(__file__).parent / "phoenix_base.json"

START_OF_STROKE = r"(?P<startofstroke>^|/)"
END_OF_STROKE = r"(?P<endofstroke>/|$)"


def add_to_dict(d, k, v):
    """Adds the key-value pair to the dictionary ``d`` unless it already exists.
    """
    if k in d:
        if d[k] == v:
            # print("Exists", k, v)
            pass
        else:
            raise ValueError(f"Existing '{k}': '{d[k]}' when trying '{v}'")
    else:
        d[k] = v


def remove_from_dict(d, k, v):
    """Removes the key-value pair from the dictionary ``d`` if and only if it
    exists.
    """
    if not d[k] == v:
        raise ValueError(f"Tried to delete '{k}': '{v}' (is '{d[k]}')")
    del d[k]


def split_list(xs, needle):
    """Note that it doesn't do the same as str.split.
    >>> list(split_list([1, 0, 1, 1, 0], 0))
    [[1], [1, 1]]
    """
    res = []
    for x in xs:
        if x == needle:
            yield res
            res = []
        else:
            res.append(x)


def apply_vop(brief: str, tran: str, cache=None) -> str:
    """Remove any short unstressed vowels from multi-stroke words.

    >>> apply_vop("A/TKREPB/A*L", "adrenal")
    'A/TKREPB/-L'
    >>> apply_vop("PHAPBLG/EUBG", "magic")
    'PHAPBLG/-BG'
    >>> apply_vop("PHAOEUPB/US", "minus")
    'PHAOEUPB/-S'
    >>> apply_vop("AD/SREPB/KHUR", "adventure")
    'AD/SREPB/KH-R'
    >>> apply_vop("PHAOEU/TPHUS", "minus")
    'PHAOEU/TPH-S'
    >>> apply_vop("AB/S*EUPBT", "absinthe")
    'AB/S*PBT'
    """
    # try:
    #     return cache[str((brief, tran))].decode("utf-8")
    # except:
    #     pass

    strokes = S.from_brief(brief)
    ipa_str = ipa.word_to_ipa(tran, cache=cache)
    phonemes = tokenize_phonemes(pronunciation=ipa_str, strokes=brief)
    syllables = parse_phoneme_tokens(phonemes)
    phonemes_by_syllable = split_list(phonemes, T(S(""), ""))

    shortened_strokes = list()

    is_first_stroke = True

    for stroke, syllable, tokens in zip(strokes, syllables, phonemes_by_syllable):
        if ipa.is_short_unstressed_syllable(syllable) and not is_first_stroke:
            stroke.keys -= set("AOEU")

            if "*" in stroke.keys:
                # check that the star doesn't correspond to any phonemes
                if not any(("*" in t.keys.keys and t.phonemes) for t in tokens):
                    stroke.keys.remove("*")

        shortened_strokes.append(str(stroke))

        is_first_stroke = False

    result = "/".join(s for s in shortened_strokes if s)

    if cache is not None:
        cache[str((brief, tran))] = result

    return result


def strip_suffix_or_prefix(tran: str) -> str:
    """
    >>> strip_suffix_or_prefix("{^acula}")
    'acula'
    >>> strip_suffix_or_prefix("{re^}")
    're'
    """
    if tran.startswith("{^"):
        tran = tran[len("{^") :]
    if tran.startswith("{"):
        tran = tran[len("{") :]
    if tran.endswith("^}"):
        tran = tran[: -len("^}")]
    if tran.endswith("}"):
        tran = tran[: -len("}")]
    return tran


def rule_AULT_ALT(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Replace all /AULT/ for "{alt^}" with /ALT/
    """
    new_dict: Dict[str, str] = dict()

    for stroke, tran in dictionary.items():
        if "AULT" in stroke and "alt" in tran:
            stroke = stroke.replace("AULT", "ALT")
        elif "KWAULT" in stroke and "qualit" in tran:
            stroke = stroke.replace("AULT", "ALT")
        new_dict[stroke] = tran

    return new_dict

def rule_AU_O(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Replace all /..AU.. for "o" sounds with /O
    """
    # delete_entries = {"A*UBG": "October"}

    # for stroke, tran in delete_entries.items():
    #     remove_from_dict(dictionary, stroke, tran)

    new_dict: Dict[str, str] = dict(dictionary)

    remove_from_dict(new_dict, "PWAR/OE", "borrow")

    o_sounds = ("əʊ", # volt
                "ɒ", # office
                "ə", # oblige
               )

    keep_original_stroke = [
        "{on^}",
        "{oz^}",
        "{aero^}",
        "{^.}{>}gov",
        "{baro^}",
    ]

    # these will inherit the "O" stroke
    force_swap = [
        "alcohol"
        "exon"
    ]

    with dbm.open("ipa_cache", "c") as cache:
        for stroke, tran in dictionary.items():
            # "AU" in first stroke indicates prefix-ness
            # e.g. /MAUN => mon^, /MON => mon
            # e.g. /AUR => aero^
            # e.g. /PAUR => para^
            # "O" in first stroke indicates "full word"
            # time to swap that around
            if (
                ("AU" in stroke or "A*U" in stroke)
                and (not stroke.endswith("AU"))  # "-ah" ending
                and ("AU/R-R" not in stroke)
                and "o" in tran
            ):
                ipa_str = ipa.word_to_ipa(tran, cache=cache)
                if any(x in ipa_str for x in o_sounds):
                    o_stroke = stroke.replace("A*U", "O*")
                    o_stroke = o_stroke.replace("AU", "O")
                    try:
                        add_to_dict(new_dict, o_stroke, tran)
                        remove_from_dict(new_dict, stroke, tran)
                    except ValueError as e:
                        # try and swap prefixes
                        if ("{" in tran and tran not in keep_original_stroke) or tran in force_swap:
                            print("Swapping", e)
                            new_dict[stroke], new_dict[o_stroke] = new_dict[o_stroke], tran
                        else:
                            print(e)

    add_to_dict(new_dict, "O*BGT", "October")
    add_to_dict(new_dict, "SHRAUT", "slaught")
    add_to_dict(new_dict, "SHRAUTS", "slaughts")

    return new_dict


def rule_AEUR_to_AR_ER(dictionary: Dict[str, str]) -> Dict[str, str]:
    """e.g.:
    /SPAEUR/OE => /SPAR/OE
    /EBGS/PAEURPLT => /EBGS/PERPLT
    """
    new_dict: Dict[str, str] = dict(dictionary)

    pre_apply = {
        "HRAR/KWR-T": ("HRAUR/KWR-T", "laureate"),
        "HRAR/KWR-TS": ("HRAUR/KWR-TS", "laureates"),
        "HRAR/KWRAEUT": ("HRAUR/KWRAEUT", "laureate"),
        "HRAR/KWRAEUT/-D": ("HRAUR/KWRAEUT/-D", "laureated"),
        "HRAR/KWRAEUT/-G": ("HRAUR/KWRAEUT/-G", "laureating"),
        "HRAR/KWRAEUTS": ("HRAUR/KWRAEUTS", "laureates"),
        "AEUR/AEURT": ("AEUR/AEURT", "aerator"),
        "AEUR/AEURTS": ("AEUR/AEURTS", "aerators"),
        "AEUR/KAEURT": ("AR/KAEURT", "{^aricator}"),
        "AEUR/KAEURTS": ("AR/KAEURTS", "{^aricators}"),
        "PREUFB/AEUR/KAEURT": ("PREUFB/AR/KAEURT", "prevaricator"),
        "PREUFB/AEUR/KAEURTS": ("PREUFB/AR/KAEURTS", "prevaricators"),
        "TKAOEUFB/AEUR/KAEURT": ("TKAOEUFB/AR/KAEURT", "divaricator"),
        "TKAOEUFB/AEUR/KAEURTS": ("TKAOEUFB/AR/KAEURTS", "divaricators"),
        "TPH/TAEUR/TKPWAEURT": ("TPH/TER/TKPWAEURT", "interrogator"),
        "TPH/TAEUR/TKPWAEURTS": ("TPH/TER/TKPWAEURTS", "interrogators"),
        "TPHAEUR/AEURT": ("TPHAR/AEURT", "narrator"),
        "TPHAEUR/AEURTS": ("TPHAR/AEURTS", "narrators"),
        "HRAEURG": ("HRARPBG", "{laryng^}"),
    }

    for stroke in pre_apply:
        new_stroke, tran = pre_apply[stroke]
        add_to_dict(new_dict, new_stroke, tran)
        remove_from_dict(new_dict, stroke, tran)

    force_translate_parts = {
        "lariat",
        "curare",
        "parentis",
        "varietal",
        "vario",
        "Pharaoh",
        "hystero",
        "humero",
        "anaero",
        "caldera",
        "concerto",
        "Bering",
    }

    pattern_ator = re.compile("(ator|atur|aiter|ater)s?}?$")

    with dbm.open("ipa_cache", "c") as cache:
        for stroke, tran in dictionary.items():
            # AEURT ~= "^ator" and should be ignored, these are the exceptions
            if "AEURT" in stroke and pattern_ator.search(tran) is not None:
                continue

            if "AEUR" or "A*EUR" in stroke:
                new_stroke = stroke
                if "ar" in tran:
                    pronunciation = ipa.word_to_ipa(tran, cache=cache)
                    if "eə" not in pronunciation or any(
                        part in tran for part in force_translate_parts
                    ):
                        new_stroke = new_stroke.replace("AEUR", "AR")
                        new_stroke = new_stroke.replace("A*EUR", "A*R")

                if "er" in tran:
                    pronunciation = ipa.word_to_ipa(tran, cache=cache)
                    if "eə" not in pronunciation or any(
                        part in tran for part in force_translate_parts
                    ):
                        new_stroke = new_stroke.replace("AEUR", "ER")
                        new_stroke = new_stroke.replace("A*EUR", "*ER")

                try:
                    add_to_dict(new_dict, new_stroke, tran)
                except ValueError as e:
                    print(e)
                    if tran in ("marry", "{var^}", "parody"):
                        print("Swapping", e)
                        new_dict[stroke], new_dict[new_stroke] = new_dict[new_stroke], tran

    return new_dict


def rule_punctuation(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Change punctuation to the way I prefer it.
    """
    new_dict: Dict[str, str] = dict(dictionary)

    period_stroke = re.compile(fr"{START_OF_STROKE}PH-PL{END_OF_STROKE}")

    # remove unnecessary space
    for stroke, tran in new_dict.items():
        new_dict[stroke] = tran.replace("} ", "}")

    return new_dict


def rule_been(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Change been/bean/bin
    """
    dictionary["PWAOEPB"] = "been"
    dictionary["PWAEPB"] = "bean"
    dictionary["PWEUPB"] = "bin"
    del dictionary["PW*EUPB"]

    return dictionary


def rule_number_star(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Swap all entries with numbers with an identical non-star number.
    """
    add_to_dict(dictionary, "KWA*EPBGTS", "eighteenths")

    numbers = re.compile(r"[0-9]+(st|nd|rd|th)?s?")

    do_not_swap = ["OERBGS"]

    to_swap = []

    for stroke, tran in dictionary.items():
        if numbers.fullmatch(tran) and not any(digit in stroke for digit in string.digits):
            strokes = [S(s) for s in stroke.split("/")]
            if "*" in strokes[0].keys:
                continue

            with_star = strokes[0]
            with_star.keys.add("*")

            stroke_with_star = "/".join(str(s) for s in strokes)
            try:
                print(stroke, tran)
                print(stroke_with_star, dictionary[str(stroke_with_star)])
                to_swap.append((stroke, stroke_with_star))
            except KeyError as e:
                print("No corresponding entry", e)

    for stroke, stroke_with_star in to_swap:
        dictionary[stroke], dictionary[stroke_with_star] = dictionary[stroke_with_star], dictionary[stroke]

    return dictionary


def rule_TH_the(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Replace all /-T for "the" with /TH as per Philadelphia Clinic,
    Phoenix styles.

    Use /THEUS for "this".
    """
    delete_entries = {"TH/AOEF": "this eve", "TH": "this"}

    for stroke, tran in delete_entries.items():
        remove_from_dict(dictionary, stroke, tran)

    new_dict: Dict[str, str] = dict()

    think_stroke = re.compile(fr"{START_OF_STROKE}THEU")

    sub_pattern = re.compile(fr"{START_OF_STROKE}-T{END_OF_STROKE}")
    the_pattern = re.compile(fr"\bthe\b")

    for stroke, tran in dictionary.items():
        if think_stroke.search(stroke) is not None and "think" in tran:
            # delete entry
            continue

        if the_pattern.search(tran) is not None:
            stroke = sub_pattern.sub(r"\1TH\2", stroke)
        add_to_dict(new_dict, stroke, tran)

    add_to_dict(new_dict, "THEUS", "this")

    return new_dict


def rule_FR_for(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Move "for" to /FR- and change /FR.. entries to use "for" instead of
    "from".

    Adds /FROMT for "from the".
    """
    new_dict = dict(dictionary)

    delete_entries = {
        "TPR": "from",
        "TPR-S": "{^s from}",
        "TPR-T": "from the",
        "TPR-Z": "{^s} from",
        "KOPL/-BG/TPR": "coming from",
    }

    for k, v in delete_entries.items():
        remove_from_dict(new_dict, k, v)

    add_to_dict(new_dict, "TPR", "for")
    add_to_dict(new_dict, "TPR-T", "for the")
    add_to_dict(new_dict, "TPROPLT", "from the")

    return new_dict


def rule_PLT_consistency(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Change all /*PLT strokes to be just /-PLT.
    """
    new_dict: Dict[str, str] = dict()

    pat = re.compile(fr"{START_OF_STROKE}\*PLT{END_OF_STROKE}")
    for stroke, tran in dictionary.items():
        new_stroke = pat.sub(r"\1-PLT\2", stroke)
        add_to_dict(new_dict, new_stroke, tran)

    return new_dict


def rule_vop_shortvowels(dictionary: Dict[str, str]) -> Dict[str, str]:
    """Changes dictionary entries to remove short unstressed vowels from
    appended strokes with short vowels.

    Does not attempt to change any names (i.e. entries where the translation has
    a capital letter).

    Expected changes:
    /*ER => /-R
    /*OR => /-R
    /AL => /-L
    /ET => /-T
    /MAL => /M-L
    etc.
    """
    del dictionary["-R"]  # = "are"
    del dictionary["-S"]  # = "{^s}"

    new_dict: Dict[str, str] = dict()

    # note that the RHS consonant is necessary, while left is optional
    left_consonants = r"(?P<left>[STKPWHR]*)"
    right_consonants = r"(?P<right>[FRPBLGTSDZ]+)"
    shortvowel = r"(?P<vowels>A\*|O\*|\*E|\*U|\*EU|A|O|E|U|EU)"

    # note that it must be at least the second stroke
    shortvowel_pattern = re.compile(
        fr"/{left_consonants}{shortvowel}{right_consonants}{END_OF_STROKE}"
    )
    lowercase_tran_pattern = re.compile(r"[a-z]+")
    any_digit_pattern = re.compile(r"[0-9]")

    with dbm.open("ipa_cache", "c") as cache:
        for stroke, tran in dictionary.items():
            # ignore multi-words, capital names, compound-hyphenated-words
            if (
                not lowercase_tran_pattern.fullmatch(tran)
                or "#" in stroke
                or any_digit_pattern.search(stroke) is not None
            ):
                continue  # TODO add to dict

            # # ignore extremely long strokes
            # if tran.count("/") > 3:
            #     continue

            if shortvowel_pattern.search(stroke) is not None:
                # DO THE THING
                reduced_stroke = apply_vop(stroke, tran, cache)
                if reduced_stroke:
                    print(stroke, tran, reduced_stroke)
                    try:
                        add_to_dict(new_dict, reduced_stroke, tran)
                    except ValueError as e:
                        print(e)

    add_to_dict(new_dict, "-R", "{^er}")
    add_to_dict(new_dict, "-S", "{^us}")

    return new_dict


def process_all() -> None:
    dictionary = json.loads(DICTIONARY.read_text())

    if "phoenix" in DICTIONARY.name:
        steps = [rule_AULT_ALT, rule_AU_O, rule_AEUR_to_AR_ER, rule_been, rule_punctuation, rule_number_star]
    else:
        steps = [rule_TH_the, rule_FR_for, rule_PLT_consistency, rule_vop_shortvowels]

    for ix, transform in enumerate(steps):
        dictionary = transform(dictionary)
        Path(f"stage_{ix}_dict.json").write_text(
            json.dumps(dictionary, indent=0, ensure_ascii=False, sort_keys=True)
        )


if __name__ == "__main__":
    process_all()
