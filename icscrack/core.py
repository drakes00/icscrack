""" Class hierarchy for SACADE tool API. """

##  @file   core.py
#   @brief  Class hierarchy for SACADE tool API.
#   @author Maxime Puys
#   @date   2016-10-07
#   Class hierarchy for SACADE tool API.
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


from . import errors

import yaml


class Automaton(object):
    _states     = None
    _start      = None
    _inputs     = None
    _outputs    = None
    _transFunc  = None
    _outputFunc = None
    _current    = None

    def __init__(self, states, start, inputs, outputs, transFunc, outputFunc):
        self._states     = states
        self._start      = start
        self._inputs     = inputs
        self._outputs    = outputs
        self._transFunc  = transFunc
        print(self._transFunc)
        self._outputFunc = outputFunc
        self._values     = {k: None for k in self._inputs}

        self._current    = self._start


    ##  Update the automaton from a list of input messages.
    #   @param  msgL Input messages list.
    #   @return The outputs corresponding to the list of input messages.
    def update(self, msgL):
        """ Update the automaton from a list of input messages. """
        def _computeInputs(msgL):
            notNones = set()
            nones = set()
            for var in self._inputs:
                if var in msgL:
                    notNones.add((var, msgL[var]))
                elif self._values[var] is not None:
                    notNones.add((var, self._values[var]))
                else:
                    nones.add(var)

            return notNones,nones

        def _removeIgnored(varsL, ignored):
            return set(filter(lambda _: _[1] not in ignored, varsL))

        inputs,ignored = _computeInputs(msgL)
        for state,varsL in self._transFunc.keys():
            transVars = _removeIgnored(set(varsL), ignored)
            if self._current == state and transVars and transVars.issubset(inputs):
                newState = self._transFunc[(state, varsL)]
                res = self._outputFunc[(self._current, newState)]

                self._current = newState
                for var,newVal in msgL:
                    if var in self._inputs:
                        self._values[var] = newVal

                return (self._current, res)

        # If no transition was matching and missing transition "seems" relevant, raise.
        # Transition is declared relevant if at least one of its variables is an
        # input of the automaton and changes value.
        for var,newVal in msgL:
            if var in self._inputs:
                if self._values[var] is None:
                    self._values[var] = newVal
                elif self._values[var] != newVal:
                    raise errors.TransitionError(msgL)


    ##  Returns an automaton from a Yaml file.
    ##  @param  yamlPath Input Yaml file path.
    #   @return An automaton from a Yaml file.
    @classmethod
    def fromYaml(cls, yamlObj):
        """ Returns an automaton from a Yaml file. """
        with open(yamlPath, "r") as handle:
            yamlObj = yaml.load(handle.read())

        return cls(
            yamlObj["states"],
            yamlObj["start"],
            yamlObj["inputs"],
            yamlObj["outputs"],
            yamlObj["transFunc"],
            yamlObj["outputFunc"]
        )


    ##  Returns an automaton from a parsed JFF object.
    ##  @param  yamlObj Input parsed JFF object.
    #   @return An automaton from a parsed JFF object.
    @classmethod
    def fromJFF(cls, jffObj):
        """ Returns an automaton from a parsed JFF object. """
        return None#cls(
