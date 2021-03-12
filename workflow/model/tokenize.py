import os
from typing import List

from sparv.core import paths
from sparv.modules.segment.segment import BetterWordTokenizer

MODEL_NAME = 'models/segment/bettertokenizer.sv'
SALDO_TOKENS_NAME = 'models/segment/bettertokenizer.sv.saldo-tokens'

tokenizer = None


def tokenize(text: str) -> List[str]:
    global tokenizer
    tokenizer = tokenizer or BetterWordTokenizer(
        model=os.path.join(paths.data_dir, MODEL_NAME),
        token_list=os.path.join(
            paths.data_dir,
            SALDO_TOKENS_NAME,
        ),
    )
    span_tokens = list(tokenizer.span_tokenize(text))
    tokens = [text[x:y] for x, y in span_tokens]
    return tokens
