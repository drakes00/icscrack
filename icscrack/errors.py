""" Exceptions and errors for SACADE tool API. """

##  @file   errors.py
#   @brief  Exceptions and errors for SACADE tool API.
#   @author Maxime Puys
#   @date   2017-01-09
#   Exceptions and errors for SACADE tool API.
#
#   Copyright (c) 2016 University Grenoble Alpes
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#   of this software and associated documentation files (the "Software"), to
#   deal in the Software without restriction, including without limitation the
#   rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#   sell copies of the Software, and to permit persons to whom the Software is
#   furnished to do so, subject to the following conditions:
#
#   The above copyright notice and this permission notice shall be included in
#   all copies or substantial portions of the Software.
#
#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#   IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#   FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#   AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#   LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#   FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
#   IN THE SOFTWARE.


##  Deviation of an automaton.
class TransitionError(Exception):
    """ Deviation of an automaton. """

    ##  @var _value
    #   Value of the exception.
    _value = None

    ##  Constructor.
    #   @param  value   Value to assign to the exception.
    def __init__(self,
                 value
                ):
        super(TransitionError, self).__init__(value)
        self._value = value


    ##  String representation of the exception.
    #   @return The string representation of the exception.
    def __str__(self):
        return str(self._value)


##  Automaton parse error.
class ParseError(Exception):
    """ Automaton parse error. """

    ##  @var _value
    #   Value of the exception.
    _value = None

    ##  Constructor.
    #   @param  value   Value to assign to the exception.
    def __init__(self,
                 value
                ):
        super(ParseError, self).__init__(value)
        self._value = value


    ##  String representation of the exception.
    #   @return The string representation of the exception.
    def __str__(self):
        return str(self._value)
