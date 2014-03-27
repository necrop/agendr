#-------------------------------------------------------------------------------
# Name: regexcompiler
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

import re


class ReplacementListCompiler(object):
    """Run a list of regex substitutions over a single string, in sequence.

    Arguments:
    1. A list of uncompiled regexes, where each element is a tuple in
    the form (pattern, replacement), e.g. (r"abc", r"xyz").
    """

    def __init__(self, uncompiled):
        self.uncompiled = uncompiled
        self.compile_list()

    def compile_list(self):
        """Compiles a list or tuple of pattern/replacement tuples.

        Arguments:
        None
        """
        self.compiled = [(re.compile(pattern), replacement) for\
                          pattern, replacement in self.uncompiled]

    def edit(self, input):
        """Edit a string, list, or tuple by running the compiled regexes.

        If the argument is none of these types, it will be returned unchanged.
        Similarly, if any element within a list or tuple is not a string, that
        element will be returned unchanged: there's no type coercion.

        For each input string, each of the compiled regexes is run in turn;
        i.e. regex2 runs on the output of regex1, etc.
        - Use 'edit_once' for a version that breaks as soon as one of the
        matches is successful.

        Arguments:
        1. A string, list, or tuple

        Returns the edited version of the string, list, or tuple (whichever
        was passed as the argument)
        """
        return self.__edit_engine(input, break_on_success=False)

    def edit_once(self, input):
        """Edit a string, list, or tuple by running the compiled regexes.

        If the argument is none of these types, it will be returned unchanged.
        Similarly, if any element within a list or tuple is not a string, that
        element will be returned unchanged: there's no type coercion.

        Each of the compiled regexes is run in turn, *until* one is
        successful, at which point the process breaks.

        Arguments:
        1. A string, list, or tuple

        Returns the edited version of the string, list, or tuple (whichever
        was passed as the argument)
        """
        return self.__edit_engine(input, break_on_success=True)

    def __edit_engine(self, input, break_on_success=False):
        output = input
        if isinstance(input, (list, tuple)):
            output = []
            for string in input:
                for pattern, replacement in self.compiled:
                    string, matches = pattern.subn(replacement, string)
                    if matches and break_on_success:
                        break
                output.append(string)
            if isinstance(input, tuple):
                output = tuple(output) # convert back to a tuple
        else:
            for pattern, replacement in self.compiled:
                output, matches = pattern.subn(replacement, output)
                if matches and break_on_success:
                    break
        return output


class ReMatcher(object):
    """Check and capture regular expression in one pass.

    Used to support if ... elif ... else constructions without nesting.

    Initialize with the string to be checked:
        m = ReMatcher(some_string)

    Usage:
        m.match(regexp) - returns True or False if regexp is successful
        m.search(regexp) - returns True or False if regexp is successful

    'regexp' can either be a regex string or a compiled regex (i.e. the
    result of 're.compile(regexp)')

    If the match was successful, captured groups can then be retrieved
    with m.group(n), e.g. 'm.group(1)' returns the first captured group.

    Example:
        m = ReMatcher(statement)
        if m.match(r"I love (\w+)"):
            print "He loves", m.group(1)
        elif m.match(r"Ich liebe (\w+)"):
            print "Er liebt", m.group(1)
        elif m.match(r"Je t'aime (\w+)"):
            print "Il aime", m.group(1)
        else:
            print "???"
    """

    def __init__(self, matchstring):
        self.matchstring = matchstring

    def search(self, regexp):
        try:
            self.rematch = regexp.search(self.matchstring)
        except AttributeError:
            self.rematch = re.search(regexp, self.matchstring)
        return bool(self.rematch)

    def match(self, regexp):
        try:
            self.rematch = regexp.match(self.matchstring)
        except AttributeError:
            self.rematch = re.match(regexp, self.matchstring)
        return bool(self.rematch)

    def group(self, i):
        return self.rematch.group(i)

