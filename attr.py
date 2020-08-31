# This file is a part of:
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
#  ███▄▄▄▄   ▀█████████▄     ▄████████     ███      ▄██████▄   ▄██████▄   ▄█
#  ███▀▀▀██▄   ███    ███   ███    ███ ▀█████████▄ ███    ███ ███    ███ ███
#  ███   ███   ███    ███   ███    █▀     ▀███▀▀██ ███    ███ ███    ███ ███
#  ███   ███  ▄███▄▄▄██▀    ███            ███   ▀ ███    ███ ███    ███ ███
#  ███   ███ ▀▀███▀▀▀██▄  ▀███████████     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ██▄          ███     ███     ███    ███ ███    ███ ███
#  ███   ███   ███    ███    ▄█    ███     ███     ███    ███ ███    ███ ███▌    ▄
#   ▀█   █▀  ▄█████████▀   ▄████████▀     ▄████▀    ▀██████▀   ▀██████▀  █████▄▄██
# __________________________________________________________________________________
# NBSTool is a tool to work with .nbs (Note Block Studio) files.
# Author: IoeCmcomc (https://github.com/IoeCmcomc)
# Programming language: Python
# License: MIT license
# Version: 0.7.0
# Source codes are hosted on: GitHub (https://github.com/IoeCmcomc/NBSTool)
# ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾


import sys, math


class Attr:
    def __init__(self, value=None, parent=None):
        self._value_ = value
        self._parent_ = parent

    def __eq__(self, other):
        return self._value_ == other

    def __ne__(self, other):
        return self._value_ != other

    def __lt__(self, other):
        return self._value_ < other

    def __gt__(self, other):
        return self._value_ > other

    def __le__(self, other):
        return self._value_ <= other

    def __ge__(self, other):
        return self._value_ >= other

    def __pos__(self):
        return +self._value_

    def __neg__(self):
        return -self._value_

    def __abs__(self):
        return abs(self._value_)

    def __invert__(self):
        return self._value_.__invert__()

    def __round__(self, n):
        return round(self._value_, n)

    def __floor__(self):
        return math.floor(self._value_)

    def __ceil__(self):
        return math.ceil(self._value_)

    def __trunc__(self):
        return math.trunc(self._value_)

    def __add__(self, other):
        return self._value_ + other

    def __sub__(self, other):
        return self._value_ - other

    def __mul__(self, other):
        return self._value_ * other

    def __floordiv__(self, other):
        return self._value_ // other

    def __div__(self, other):
        return self._value_ / other

    def __truediv__(self, other):
        return self._value_ / other

    def __mod__(self, other):
        return self._value_ % other

    def __divmod__(self, other):
        return divmod(self._value_, other)

    def __pow__(self, other):
        return self._value_ ** other

    def __lshift__(self, other):
        return self._value_ << other

    def __rshift__(self, other):
        return self._value_ >> other

    def __and__(self, other):
        return self._value_ & other

    def __or__(self, other):
        return self._value_ | other

    def __xor__(self, other):
        return self._value_ ^ other

    def __radd__(self, other):
        return other + self._value_

    def __rsub__(self, other):
        return other - self._value_

    def __rmul__(self, other):
        return other * self._value_

    def __rfloordiv__(self, other):
        return other // self._value_

    def __rdiv__(self, other):
        return other / self._value_

    def __rtruediv__(self, other):
        return other / self._value_

    def __rmod__(self, other):
        return other % self._value_

    def __rdivmod__(self, other):
        return divmod(other, self._value_)

    def __rpow__(self, other):
        return other ** self._value_

    def __rlshift__(self, other):
        return other << self._value_

    def __rrshift__(self, other):
        return other >> self._value_

    def __rand__(self, other):
        return other & self._value_

    def __ror__(self, other):
        return other | self._value_

    def __rxor__(self, other):
        return other ^ self._value_

    def __iadd__(self, other):
        return self._value_ + other

    def __isub__(self, other):
        return self._value_ - other

    def __imul__(self, other):
        return self._value_ * other

    def __ifloordiv__(self, other):
        return self._value_ // other

    def __idiv__(self, other):
        return self._value_ / other

    def __itruediv__(self, other):
        return self._value_ / other

    def __imod__(self, other):
        return self._value_ % other

    def __idivmod__(self, other):
        return divmod(self._value_, other)

    def __ipow__(self, other):
        return self._value_ ** other

    def __ilshift__(self, other):
        return self._value_ << other

    def __irshift__(self, other):
        return self._value_ >> other

    def __iand__(self, other):
        return self._value_ & other

    def __ior__(self, other):
        return self._value_ | other

    def __ixor__(self, other):
        return self._value_ ^ other

    def __int__(self):
        return int(self._value_)

    # def __long__(self):
    #     return long(self._value_)

    def __float__(self):
        return float(self._value_)

    def __complex__(self):
        return complex(self._value_)

    def __oct__(self):
        return oct(self._value_)

    def __hex__(self):
        return hex(self._value_)

    def __index__(self):
        return self._value_

    def __str__(self):
        return str(self._value_)

    def __repr__(self):
        # return repr(self._value_)
        reprStr = "<Class: Attr; ID: {}; value's class: {}>".format(
            hex(id(self)), repr(self._value_.__class__.__name__))
        return reprStr

    # def __unicode__(self):
    #     return unicode(self._value_)

    def __format__(self, formatstr):
        pattern = '{0:'+formatstr+'}'
        return pattern.format(self._value_)

    def __hash__(self):
        return hash(self._value_)

    def __nonzero__(self):
        return bool(self._value_)

    def __dir__(self):
        return super().__dir__()

    def __sizeof__(self):
        return sys.getsizeof(self._value_)

    def __setattr__(self, name, value):
        if name[:1] == '_':
            if len(name) == 1:
                setattr(self, '_value_', value)
            else:
                super().__setattr__(name, value)
        else:
            super().__setattr__(name, Attr(value, self))

    def __getattr__(self, name):
        valueAttr = getattr(self._value_, name, None)
        if 'method' in valueAttr.__class__.__name__ or 'function' in valueAttr.__class__.__name__:
            return valueAttr
        elif name == '_':

            return self._value_
        else:
            setattr(self, name, None)
            return getattr(self, name)

    def __len__(self):
        return len(self._value_)

    def __getitem__(self, key):
        return self._value_[key]

    def __setitem__(self, key, value):
        self._value_[key] = value

    def __delitem__(self, key):
        del self._value_[key]

    def __iter__(self):
        return iter(self._value_)

    def __reversed__(self):
        return reversed(self._value_)

    def __contains__(self, item):
        return item in self._value_
    '''
	def __missing__(self, key):
		return super().__missing__(key)
	
	def __call__(self, value=None, parent=None):
		print('called')
		return self._value_
		if len(sys.argv) > 1:
			if self._value_ is not value: self._value_ = value
			if self._parent_ is not parent: self._parent_ = parent'''
