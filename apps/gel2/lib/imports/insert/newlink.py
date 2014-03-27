#-------------------------------------------------------------------------------
# Name: NewLink
# Purpose:
#
# Author: James McCracken
#-------------------------------------------------------------------------------

class NewLink(object):

    def __init__(self, args, i):
        self.__dict__ = args
        self.recordID = int(self.recordID)
        self.status = "null"
        self.row_num = i


class NewEntry(object):

    def __init__(self, args, i):
        self.__dict__ = args
        self.status = "null"
        self.row_num = i
