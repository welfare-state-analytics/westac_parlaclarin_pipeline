"""
Temporarily inlined code from Sparv v4.0.0.
Sparv dependency is made optional (lacks Stanza v1.6 support which has improved performance)
"""
import re
from os.path import join as jj
from typing import List

from loguru import logger

# try:
#     from sparv.core import paths
#     from sparv.modules.segment.segment import BetterWordTokenizer

#     if paths.data_dir is None:
#         raise ValueError("run sparv setup to specify SPARV_DATADIR")

#     SPARV_DATADIR = paths.data_dir

# except ImportError:

# pylint: disable=no-else-continue, attribute-defined-outside-init

SPARV_DATADIR = "/data/sparv"
MODEL_NAME = jj(SPARV_DATADIR, "models", "segment", "bettertokenizer.sv")
SALDO_TOKENS_NAME = jj(SPARV_DATADIR, "models", "segment", "bettertokenizer.sv.saldo-tokens")

# This class belongs to sparv-pipeline (temporarily copied out)
class BetterWordTokenizer:
    """A word tokenizer based on the PunktWordTokenizer code.

    Heavily modified to add support for custom regular expressions, wordlists, and external configuration files.
    http://nltk.googlecode.com/svn/trunk/doc/api/nltk.tokenize.punkt.PunktSentenceTokenizer-class.html
    """

    # Format for the complete regular expression to be used for tokenization
    _word_tokenize_fmt = r'''(
        %(misc)s
        |
        %(multi)s
        |
        (?:(?:(?<=^)|(?<=\s))%(number)s(?=\s|$))  # Numbers with decimal mark
        |
        (?=[^%(start)s])
        (?:%(tokens)s%(abbrevs)s(?<=\s)(?:[^\.\s]+\.){2,}|\S+?)  # Accept word characters until end is found
        (?= # Sequences marking a word's end
            \s|                                 # White-space
            $|                                  # End-of-string
            (?:[%(within)s])|%(multi)s|         # Punctuation
            [%(end)s](?=$|\s|(?:[%(within)s])|%(multi)s)  # Misc characters if at end of word
        )
        |
        \S
    )'''

    # Used to realign punctuation that should be included in a sentence although it follows the period (or ?, !).
    re_boundary_realignment = re.compile(r'[“”"\')\]}]+?(?:\s+|(?=--)|$)', re.MULTILINE)

    re_punctuated_token = re.compile(r"\w.*\.$", re.UNICODE)

    def __init__(self, model, token_list=None):
        """Parse configuration file (model) and token_list (if supplied)."""
        self.case_sensitive = False
        self.patterns = {"misc": [], "tokens": []}
        self.abbreviations = set()
        in_abbr = False

        if token_list:
            with open(token_list, encoding="UTF-8") as saldotokens:
                self.patterns["tokens"] = [re.escape(t.strip()) for t in saldotokens.readlines()]

        with open(model, encoding="UTF-8") as conf:
            for line in conf:
                if line.startswith("#") or not line.strip():
                    continue
                if not in_abbr:
                    if not in_abbr and line.strip() == "abbreviations:":
                        in_abbr = True
                        continue
                    else:
                        try:
                            key, val = line.strip().split(None, 1)
                        except ValueError as e:
                            logger.error(f"Error parsing configuration file: {line}")
                            raise e
                        key = key[:-1]

                        if key == "case_sensitive":
                            self.case_sensitive = val.lower() == "true"
                        elif key.startswith("misc_"):
                            self.patterns["misc"].append(val)
                        elif key in ("start", "within", "end"):
                            self.patterns[key] = re.escape(val)
                        elif key in ("multi", "number"):
                            self.patterns[key] = val
                        # For backwards compatibility
                        elif key == "token_list":
                            pass
                        else:
                            raise ValueError("Unknown option: %s" % key)
                else:
                    self.abbreviations.add(line.strip())

    def _word_tokenizer_re(self):
        """Compile and return a regular expression for word tokenization."""
        try:
            return self._re_word_tokenizer
        except AttributeError:
            modifiers = (re.UNICODE | re.VERBOSE) if self.case_sensitive else (re.UNICODE | re.VERBOSE | re.IGNORECASE)
            self._re_word_tokenizer = re.compile(
                self._word_tokenize_fmt
                % {
                    "tokens": ("(?:" + "|".join(self.patterns["tokens"]) + ")|") if self.patterns["tokens"] else "",
                    "abbrevs": ("(?:" + "|".join(re.escape(a + ".") for a in self.abbreviations) + ")|")
                    if self.abbreviations
                    else "",
                    "misc": "|".join(self.patterns["misc"]),
                    "number": self.patterns["number"],
                    "within": self.patterns["within"],
                    "multi": self.patterns["multi"],
                    "start": self.patterns["start"],
                    "end": self.patterns["end"],
                },
                modifiers,
            )
            return self._re_word_tokenizer

    def word_tokenize(self, s):
        """Tokenize a string to split off punctuation other than periods."""
        words = self._word_tokenizer_re().findall(s)
        if not words:
            return words
        pos = len(words) - 1

        # Split sentence-final . from the final word.
        # i.e., "peter." "piper." ")" => "peter." "piper" "." ")"
        # but not "t.ex." => "t.ex" "."
        while pos >= 0 and self.re_boundary_realignment.match(words[pos]):
            pos -= 1
        endword = words[pos]
        if self.re_punctuated_token.search(endword):
            endword = endword[:-1]
            if endword not in self.abbreviations:
                words[pos] = endword
                words.insert(pos + 1, ".")

        return words

    def span_tokenize(self, s):
        """Tokenize s."""
        begin = 0
        for w in self.word_tokenize(s):
            begin = s.find(w, begin)
            yield begin, begin + len(w)
            begin += len(w)


_TOKENIZER = None


def tokenize(text: str) -> List[str]:
    global _TOKENIZER
    _TOKENIZER = _TOKENIZER or BetterWordTokenizer(model=MODEL_NAME, token_list=SALDO_TOKENS_NAME)
    # model=os.path.join(paths.data_dir, MODEL_NAME),
    # token_list=os.path.join(
    #     paths.data_dir,
    #     SALDO_TOKENS_NAME,
    # ),
    # )
    span_tokens = list(_TOKENIZER.span_tokenize(text))
    tokens = [text[x:y] for x, y in span_tokens]
    return tokens
