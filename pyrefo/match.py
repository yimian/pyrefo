from pyrefo._refo import ffi, lib
from pyrefo.patterns import *


@ffi.def_extern()
def comp_func_callback(o, y):
    o = ffi.from_handle(o)
    y = ffi.from_handle(y)
    return o.comparison_function(y)


class Seq(object):
    def __init__(self, iterable):
        self._p = [ffi.new_handle(item) for item in iterable]
        self._seq = ffi.new('Seq*', {'len': len(iterable), 'start': self._p})
        
    def __len__(self):
        return self._seq.len
    
    @property
    def len(self):
        return self._seq.len
    
class Match(object):
    def __init__(self, state):
        self.state = state
        self.len = len(self.state)
        self._pos = ffi.new('Pos[]', self.len)
        self._m = ffi.new('SubMatch*', {'len': self.len, 'pos': self._pos})
        
    def span(self, key=None):
        return self[key]
    
    def start(self, key=None):
        return self[key][0]
    
    def end(self, key=None):
        return self[key][1]
    
    def group(self, key=None):
        return self[key]
    
    def __getitem__(self, key):
        try:
            pos = self._m.pos[self.state[key] - 1]
            return pos.start, pos.end
        except KeyError:
            raise KeyError(key)
            
    def __contains__(self, key):
        return key in self.state
    
    def __iter__(self):
        for key in self.state:
            yield key
            
            
def _match(pat, iterable):
    code = pat.compile()
    print(pat._state)
    prog = ffi.new('Prog*', {'len': len(pat), 'start': code._inst})
    seq = Seq(iterable)
    match = Match(pat._state_i)
    matched = lib.search(prog, seq._seq, match._m)
    if matched:
        return match
    return None
    
        
def search(pat, iterable):
    pat = Star(Any(), greedy=False) + Group(pat, None)
    return _match(pat, iterable)

def match(pat, iterable):
    pat = Group(pat, None)
    return _match(pat, iterable)