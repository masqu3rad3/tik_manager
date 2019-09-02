#!/usr/local/bin/python
# coding: utf-8
import os, sys

import unicodedata
def strip_accents(s):
    """
    Sanitarize the given unicode string and remove all special/localized
    characters from it.

    Category "Mn" stands for Nonspacing_Mark
    """
    if type(s) == str:
        s=unicode(s, "utf-8")

    newNameList = []
    for c in unicodedata.normalize('NFKD', s):
        if unicodedata.category(c) != 'Mn':
            if c == u'ı':
                newNameList.append(u'i')
            else:
                newNameList.append(c)
    return ''.join(newNameList)



a = u"ıçlı"

# print a
print strip_accents(a)