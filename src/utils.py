import itertools
import re
from typing import Callable, Iterable, Tuple, TypeVar

T = TypeVar('T')

def split_iterable(pred: Callable[[T], bool], it: Iterable[T]) -> Tuple[Tuple[T], T, Tuple[T]]:
    """Split an iterable according to a predicate.
    Specifically, let it = (s0, s1, s2, s3, s4, ...) and suppose that
        pred(s0) = pred(s1) = ... = pred(sj) = False and pred(s(j+1)) = True.
    Then this method returns (s0, s1, s2, ..., sj), s(j+1), (s(j+2), s(j+3), ...)
    
    Example:
        >>> before, _, after = split_iterable(lambda x: x >= 4, range(10))
        >>> tuple(before)   # all elements before the first which evaluates true
        (0, 1, 2, 3)
        >>> tuple(after)    # all elements after the first which evaluates true
        (5, 6, 7, 8, 9)
    """
    it = iter(it)
    before = itertools.takewhile(lambda x: not pred(x))
    
    return tuple(before), next(it, None), tuple(it)


def chain_sub(text: str, *rules: Tuple[str, str]) -> str:
    """Perform multiple consecutive re.sub calls.
    
    Example:
        text = chain_sub(text, (pat1, repl1), (pat2, repl2))
    is the same as
        text = re.sub(pat1, repl1, text)
        text = re.sub(pat2, repl2, text)
    """
    for pattern, replacement in rules:
        text = re.sub(pattern, replacement, text)
        
    return text