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

import os
import re
import ast
import xml.etree.ElementTree as ET
import yaml


from . import errors


##  Returns as many automata instance as behaviors provided in a Yaml file.
##  @param  yamlPath Input Yaml file path.
#   @return The list of automata from a Yaml file.
def fromYaml(yamlPath):
    """ Returns as many automata instance as behaviors provided in a Yaml file. """
    with open(yamlPath, "r") as handle:
        yamlObj = yaml.load(handle.read())

    agents = yamlObj["topology"]["servers"].copy()
    agents.update(yamlObj["topology"]["clients"])
    res = []
    for name, attributes in agents.items():
        try:
            variables = {k:tuple(v) for k,v in attributes["variables"].items()}
            behavior = "{}/{}".format(
                os.path.dirname(yamlPath),
                attributes["behavior"]
            )
            res.append(Automaton.fromJFF(name, behavior, variables))
        except KeyError:
            pass

    return res


class Automaton(object):
    _name       = None
    _states     = None
    _start      = None
    _variables  = None
    _transFunc  = None
    _outputFunc = None
    _current    = None

    def __init__(self, name, states, start, variables, transFunc, outputFunc):
        self._name       = name
        self._states     = states
        self._start      = start
        self._variables  = variables
        self._transFunc  = transFunc
        self._outputFunc = outputFunc
        self._values     = {k: None for k in self._variables.values()}

        self._current    = self._start


    ##  Returns the name of the automaton.
    #   @return The name of the automaton.
    def getName(self):
        """ Returns the name of the automaton. """
        return self._name


    ##  Returns the name of a variable from its mapping.
    #   @param  mapping Mapping of the variable.
    #   @return The name of a variable from its mapping or None if not found.
    def getVariableName(self, mapping):
        """ Returns the name of a variable from its mapping. """
        for varName,varMap in self._variables.items():
            if varMap == mapping:
                return varName

        return None


    ##  Update the automaton from a list of input messages.
    #   @param  msgL Input messages list.
    #   @return The outputs corresponding to the list of input messages.
    def update(self, msgL):
        """ Update the automaton from a list of input messages. """
        def _computeInputs(msgL):
            notNones = set()
            nones = set()
            for varMap in self._variables.values():
                if varMap in msgL:
                    notNones.add((varMap, msgL[varMap]))
                elif self._values[varMap] is not None:
                    notNones.add((varMap, self._values[varMap]))
                else:
                    nones.add(varMap)

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
                for varMap,newVal in msgL:
                    if varMap in self._variables.values():
                        self._values[varMap] = newVal

                return (self._current, res)

        # If no transition was matching and missing transition "seems" relevant, raise.
        # Transition is declared relevant if at least one of its variables is an
        # input of the automaton and changes value.
        for varMap,newVal in msgL:
            if varMap in self._variables.values():
                if self._values[varMap] is None:
                    self._values[varMap] = newVal
                elif self._values[varMap] != newVal:
                    raise errors.TransitionError(msgL)


    ##  Returns an automaton from a JFF file.
    #   @param  name        Name of the automaton.
    #   @param  jffPath     Input JFF file path.
    #   @param  variables   Variables mappings.
    #   @return An automaton from a JFF file.
    @classmethod
    def fromJFF(cls, name, jffPath, variables):
        """ Returns an automaton from a JFF file. """
        pattern = re.compile("(\w+), (\w+)")
        def _parseTrans(trans):
            res = []
            if trans is not None:
                for varName,val in pattern.findall(trans):
                    res += [(tuple(variables[varName]), val == "True")]

            return res

        typ,auto = ET.parse(jffPath).getroot().getchildren()
        if typ.text != "mealy":
            raise errors.ParseError("Mealy automaton expected!")

        states     = {}
        start      = None
        transFunc  = {}
        outputFunc = {}
        for node in auto.getchildren():
            if node.tag == "state":
                nodeId = node.get("id")
                nodeName = node.get("name")
                states[nodeId] = nodeName
                if any(_.tag == "initial" for _ in node.getchildren()):
                    start = nodeName
            elif node.tag == "transition":
                nodeFrom,nodeTo,trans,output = [_.text for _ in node.getchildren()]
                trans = _parseTrans(trans)
                output = _parseTrans(output)

                transFunc[(states[nodeFrom], tuple(trans))] = states[nodeTo]
                outputFunc[(states[nodeFrom], states[nodeTo])] = output

        return cls(
            name,
            states,
            start,
            variables,
            transFunc,
            outputFunc
        )
