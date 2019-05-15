# -*- coding: utf-8 -*-

# Copyright (c) 2016 - 2019 Detlev Offenbach <detlev@die-offenbachs.de>
#

"""
Module implementing classes and functions to dump variable contents.
"""

#
# This code was inspired by pydevd.
#

MaxItemsToHandle = 300
TooLargeMessage = ("Too large to show contents. Max items to show: " +
                   str(MaxItemsToHandle))
TooLargeAttribute = "Too large to be handled."

############################################################
## Classes implementing resolvers for various compund types
############################################################


class BaseResolver(object):
    """
    Base class of the resolver class tree.
    """
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type any
        @param attribute name of the attribute to extract
        @type str
        @return value of the attribute
        @rtype any
        @exception NotImplementedError raised to indicate a missing
            implementation
        """     # __IGNORE_WARNING_D235__
        raise NotImplementedError
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        @exception NotImplementedError raised to indicate a missing
            implementation
        """     # __IGNORE_WARNING_D235__
        raise NotImplementedError


############################################################
## Default Resolver
############################################################


class DefaultResolver(BaseResolver):
    """
    Class used to resolve the default way.
    """
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type any
        @param attribute name of the attribute to extract
        @type str
        @return value of the attribute
        @rtype any
        """
        return getattr(var, attribute, None)
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        """
        names = dir(var)
        if not names and hasattr(var, "__members__"):
            names = var.__members__
        
        d = {}
        for name in names:
            try:
                attribute = getattr(var, name)
                d[name] = attribute
            except Exception:
                pass    # if we can't get it, simply ignore it
        
        return d


############################################################
## Resolver for Dictionaries
############################################################


class DictResolver(BaseResolver):
    """
    Class used to resolve from a dictionary.
    """
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type dict
        @param attribute name of the attribute to extract
        @type str
        @return value of the attribute
        @rtype any
        """
        if attribute in ('___len___', TooLargeAttribute):
            return None
        
        if "(ID:" not in attribute:
            try:
                return var[attribute]
            except Exception:
                return getattr(var, attribute, None)
        
        expectedID = int(attribute.split("(ID:")[-1][:-1])
        for key, value in var.items():
            if id(key) == expectedID:
                return value
        
        return None
    
    def keyToStr(self, key):
        """
        Public method to get a string representation for a key.
        
        @param key key to be converted
        @type any
        @return string representation of the given key
        @rtype str
        """
        if isinstance(key, str):
            return repr(key)
        else:
            return key
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        """
        d = {}
        count = 0
        for key, value in var.items():
            count += 1
            key = "{0} (ID:{1})".format(self.keyToStr(key), id(key))
            d[key] = value
            if count > MaxItemsToHandle:
                d[TooLargeAttribute] = TooLargeMessage
                break
        
        d["___len___"] = len(var)
        
        # in case it has additional fields
        additionals = defaultResolver.getDictionary(var)
        d.update(additionals)
        
        return d


############################################################
## Resolver for Lists and Tuples
############################################################


class ListResolver(BaseResolver):
    """
    Class used to resolve from a tuple or list.
    """
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type tuple or list
        @param attribute name of the attribute to extract
        @type str
        @return value of the attribute
        @rtype any
        """
        if attribute in ('___len___', TooLargeAttribute):
            return None

        try:
            return var[int(attribute)]
        except Exception:
            return getattr(var, attribute, None)
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        """
        d = {}
        count = 0
        for value in var:
            d[str(count)] = value
            count += 1
            if count > MaxItemsToHandle:
                d[TooLargeAttribute] = TooLargeMessage
                break
        
        d["___len___"] = len(var)
        
        # in case it has additional fields
        additionals = defaultResolver.getDictionary(var)
        d.update(additionals)
        
        return d


############################################################
## Resolver for Sets and Frozensets
############################################################


class SetResolver(BaseResolver):
    """
    Class used to resolve from a set or frozenset.
    """
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type tuple or list
        @param attribute id of the value to extract
        @type str
        @return value of the attribute
        @rtype any
        """
        if attribute in ('___len___', TooLargeAttribute):
            return None

        if attribute.startswith("ID: "):
            attribute = attribute.split(None, 1)[1]
        try:
            attribute = int(attribute)
        except Exception:
            return getattr(var, attribute, None)

        for v in var:
            if id(v) == attribute:
                return v
        
        return None
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        """
        d = {}
        count = 0
        for value in var:
            count += 1
            d["ID: " + str(id(value))] = value
            if count > MaxItemsToHandle:
                d[TooLargeAttribute] = TooLargeMessage
                break

        d["___len___"] = len(var)
        
        # in case it has additional fields
        additionals = defaultResolver.getDictionary(var)
        d.update(additionals)
        
        return d


############################################################
## Resolver for Numpy Arrays
############################################################


class NdArrayResolver(BaseResolver):
    """
    Class used to resolve from numpy ndarray including some meta data.
    """
    def __isNumeric(self, arr):
        """
        Private method to check, if an array is of a numeric type.
        
        @param arr array to check
        @type ndarray
        @return flag indicating a numeric array
        @rtype bool
        """
        try:
            return arr.dtype.kind in 'biufc'
        except AttributeError:
            return False
    
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type tuple or list
        @param attribute id of the value to extract
        @type str
        @return value of the attribute
        @rtype any
        """
        if attribute == '__internals__':
            return defaultResolver.getDictionary(var)
        
        if attribute == 'min':
            if self.__isNumeric(var):
                return var.min()
            else:
                return None
        
        if attribute == 'max':
            if self.__isNumeric(var):
                return var.max()
            else:
                return None
        
        if attribute == 'mean':
            if self.__isNumeric(var):
                return var.mean()
            else:
                return None
        
        if attribute == 'shape':
            return var.shape
        
        if attribute == 'dtype':
            return var.dtype
        
        if attribute == 'size':
            return var.size
        
        if attribute.startswith('['):
            container = NdArrayItemsContainer()
            count = 0
            for element in var:
                setattr(container, str(count), element)
                count += 1
                if count > MaxItemsToHandle:
                    setattr(container, TooLargeAttribute, TooLargeMessage)
                    break
            return container
        
        return None
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        """
        d = {}
        d['__internals__'] = defaultResolver.getDictionary(var)
        if var.size > 1024 * 1024:
            d['min'] = 'ndarray too big, calculating min would slow down' \
                       ' debugging'
            d['max'] = 'ndarray too big, calculating max would slow down' \
                       ' debugging'
        else:
            if self.__isNumeric(var):
                if var.size == 0:
                    d['min'] = 'empty array'
                    d['max'] = 'empty array'
                    d['mean'] = 'empty array'
                else:
                    d['min'] = var.min()
                    d['max'] = var.max()
                    d['mean'] = var.mean()
            else:
                d['min'] = 'not a numeric object'
                d['max'] = 'not a numeric object'
                d['mean'] = 'not a numeric object'
        d['shape'] = var.shape
        d['dtype'] = var.dtype
        d['size'] = var.size
        d['[0:{0}]'.format(len(var) - 1)] = list(var[0:MaxItemsToHandle])
        return d


class NdArrayItemsContainer:
    """
    Class to store ndarray items.
    """
    pass


############################################################
## Resolver for Django Multi Value Dictionaries
############################################################


class MultiValueDictResolver(DictResolver):
    """
    Class used to resolve from Django multi value dictionaries.
    """
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type dict
        @param attribute name of the attribute to extract
        @type str
        @return value of the attribute
        @rtype any
        """
        if attribute in ('___len___', TooLargeAttribute):
            return None
        
        if "(ID:" not in attribute:
            try:
                return var[attribute]
            except Exception:
                return getattr(var, attribute, None)
        
        expectedID = int(attribute.split("(ID:")[-1][:-1])
        for key in var.keys():
            if id(key) == expectedID:
                value = var.getlist(key)
                return value
        
        return None
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        """
        d = {}
        count = 0
        for key in var.keys():
            count += 1
            value = var.getlist(key)
            key = "{0} (ID:{1})".format(self.keyToStr(key), id(key))
            d[key] = value
            if count > MaxItemsToHandle:
                d[TooLargeAttribute] = TooLargeMessage
                break
        
        d["___len___"] = len(var)
        
        return d


############################################################
## Resolver for array.array
############################################################


class ArrayResolver(BaseResolver):
    """
    Class used to resolve from array.array including some meta data.
    """
    TypeCodeMap = {
        "b": "int (signed char)",
        "B": "int (unsigned char)",
        "u": "Unicode character (Py_UNICODE)",
        "h": "int (signed short)",
        "H": "int (unsigned short)",
        "i": "int (signed int)",
        "I": "int (unsigned int)",
        "l": "int (signed long)",
        "L": "int (unsigned long)",
        "q": "int (signed long long)",
        "Q": "int (unsigned long long)",
        "f": "float (float)",
        "d": "float (double)",
    }
    
    def resolve(self, var, attribute):
        """
        Public method to get an attribute from a variable.
        
        @param var variable to extract an attribute or value from
        @type tuple or list
        @param attribute id of the value to extract
        @type str
        @return value of the attribute
        @rtype any
        """
        if attribute == 'itemsize':
            return var.itemsize
        
        if attribute == 'typecode':
            return var.typecode
        
        if attribute == 'type':
            if var.typecode in ArrayResolver.TypeCodeMap:
                return ArrayResolver.TypeCodeMap[var.typecode]
            else:
                return 'illegal type'
        
        if attribute.startswith('['):
            container = ArrayItemsContainer()
            count = 0
            for element in var:
                setattr(container, str(count), element)
                count += 1
                if count > MaxItemsToHandle:
                    setattr(container, TooLargeAttribute, TooLargeMessage)
                    break
            return container
        
        return None
    
    def getDictionary(self, var):
        """
        Public method to get the attributes of a variable as a dictionary.
        
        @param var variable to be converted
        @type any
        @return dictionary containing the variable attributes
        @rtype dict
        """
        d = {}
        d['typecode'] = var.typecode
        if var.typecode in ArrayResolver.TypeCodeMap:
            d['type'] = ArrayResolver.TypeCodeMap[var.typecode]
        else:
            d['type'] = 'illegal type'
        d['itemsize'] = var.itemsize
        d['[0:{0}]'.format(len(var) - 1)] = var.tolist()[0:MaxItemsToHandle]
        return d


class ArrayItemsContainer:
    """
    Class to store array.array items.
    """
    pass


defaultResolver = DefaultResolver()
dictResolver = DictResolver()
listResolver = ListResolver()
setResolver = SetResolver()
ndarrayResolver = NdArrayResolver()
multiValueDictResolver = MultiValueDictResolver()
arrayResolver = ArrayResolver()

############################################################
## Methods to determine the type of a variable and the
## resolver class to use
############################################################

_TypeMap = None


def _initTypeMap():
    """
    Protected function to initialize the type map.
    """
    global _TypeMap
    
    _TypeMap = [
        (type(None), None,),
        (int, None),
        (float, None),
        (complex, None),
        (str, None),
        (tuple, listResolver),
        (list, listResolver),
        (dict, dictResolver),
    ]
    
    try:
        _TypeMap.append((long, None))           # __IGNORE_WARNING__
    except Exception:
        pass    # not available on all python versions

    try:
        _TypeMap.append((unicode, None))        # __IGNORE_WARNING__
    except Exception:
        pass    # not available on all python versions

    try:
        _TypeMap.append((set, setResolver))     # __IGNORE_WARNING__
    except Exception:
        pass    # not available on all python versions

    try:
        _TypeMap.append((frozenset, setResolver))     # __IGNORE_WARNING__
    except Exception:
        pass    # not available on all python versions
    
    try:
        import array
        _TypeMap.append((array.array, arrayResolver))
    except ImportError:
        pass  # array.array may not be available
    
    try:
        import numpy
        _TypeMap.append((numpy.ndarray, ndarrayResolver))
    except ImportError:
        pass  # numpy may not be installed
    
    try:
        from django.utils.datastructures import MultiValueDict
        _TypeMap.insert(0, (MultiValueDict, multiValueDictResolver))
        # it should go before dict
    except ImportError:
        pass  # django may not be installed


def getType(obj):
    """
    Public method to get the type information for an object.
    
    @param obj object to get type information for
    @type any
    @return tuple containing the type, type name, type string and resolver
    @rtype tuple of type, str, str, BaseResolver
    """
    typeObject = type(obj)
    typeName = typeObject.__name__
    typeStr = str(typeObject)[8:-2]
    
    if typeStr.startswith(("PyQt5.", "PyQt4.")):
        resolver = None
    else:
        if _TypeMap is None:
            _initTypeMap()
        
        for typeData in _TypeMap:
            if isinstance(obj, typeData[0]):
                resolver = typeData[1]
                break
        else:
            resolver = defaultResolver
    
    return typeObject, typeName, typeStr, resolver

#
# eflag: noqa = M702
