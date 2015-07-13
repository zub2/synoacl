"""
    This file is part of synoacl.

    Synoacl is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Synoacl is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with synoacl. If not, see <http://www.gnu.org/licenses/>.

    Copyright 2015 David Kozub
"""
import re
import subprocess

class SynoACL(object):
    class Permissions(object):
        def __init__(self, readData = False, writeData = False, execute = False, appendData = False,
            delete = False, deleteChild = False, readAttribute = False, writeAttribute = False,
            readXAttr = False, writeXAttr = False, readAcl = False, writeAcl = False, getOwnership = False):
            self.readData = readData
            self.writeData = writeData
            self.execute = execute
            self.appendData = appendData
            self.delete = delete
            self.deleteChild = deleteChild
            self.readAttribute = readAttribute
            self.writeAttribute = writeAttribute
            self.readXAttr = readXAttr
            self.writeXAttr = writeXAttr
            self.readAcl = readAcl
            self.writeAcl = writeAcl
            self.getOwnership = getOwnership

        @staticmethod
        def fromString(s):
            readData = False
            writeData = False
            execute = False
            appendData = False
            delete = False
            deleteChild = False
            readAttribute = False
            writeAttribute = False
            readXAttr = False
            writeXAttr = False
            readAcl = False
            writeAcl = False
            getOwnership = False

            for c in s:
                if c == "-":
                    pass
                elif c == "r":
                    readData = True
                elif c == "w":
                    writeData = True
                elif c == "x":
                    execute = True
                elif c == "p":
                    appendData = True
                elif c == "d":
                    delete = True
                elif c == "D":
                    deleteChild = True
                elif c == "a":
                    readAttribute = True
                elif c == "A":
                    writeAttribute = True
                elif c == "R":
                    readXAttr = True
                elif c == "W":
                    writeXAttr = True
                elif c == "c":
                    readAcl = True
                elif c == "C":
                    writeAcl = True
                elif c == "o":
                    getOwnership = True
                else:
                    raise Exception("Unexpected permission letter: '" + c + "'")

            return SynoACL.Permissions(readData = readData, writeData = writeData, execute = execute, appendData = appendData,
                delete = delete, deleteChild = deleteChild, readAttribute = readAttribute, writeAttribute = writeAttribute,
                readXAttr = readXAttr, writeXAttr = writeXAttr, readAcl = readAcl, writeAcl = writeAcl, getOwnership = getOwnership)

        def __str__(self):
            r = ""
            r += SynoACL._formatPermission("r", self.readData)
            r += SynoACL._formatPermission("w", self.writeData)
            r += SynoACL._formatPermission("x", self.execute)
            r += SynoACL._formatPermission("p", self.appendData)
            r += SynoACL._formatPermission("d", self.delete)
            r += SynoACL._formatPermission("D", self.deleteChild)
            r += SynoACL._formatPermission("a", self.readAttribute)
            r += SynoACL._formatPermission("A", self.writeAttribute)
            r += SynoACL._formatPermission("R", self.readXAttr)
            r += SynoACL._formatPermission("W", self.writeXAttr)
            r += SynoACL._formatPermission("c", self.readAcl)
            r += SynoACL._formatPermission("C", self.writeAcl)
            r += SynoACL._formatPermission("o", self.getOwnership)
            return r

        def __eq__(self, other):
            # Cheating a bit but performance is not that important and it saves typing
            return str(self) == str(other)

        def __ne__(self, other):
            return not self.__eq__(other)

    class Inheritance(object):
        def __init__(self, fileInherited = False, directoryInherited = False, inheritOnly = False, noPropagate = False):
            self.fileInherited = fileInherited
            self.directoryInherited = directoryInherited
            self.inheritOnly = inheritOnly
            self.noPropagate = noPropagate

        @staticmethod
        def fromString(s):
            fileInherited = False
            directoryInherited = False
            inheritOnly = False
            noPropagate = False

            for c in s:
                if c == "-":
                    pass
                elif c == "f":
                    fileInherited = True
                elif c == "d":
                    directoryInherited = True
                elif c == "i":
                    inheritOnly = True
                elif c == "n":
                    noPropagate = True
                else:
                    raise Exception("Unexpected inheritance letter: '" + c + "'")

            return SynoACL.Inheritance(fileInherited = fileInherited, directoryInherited = directoryInherited,
                inheritOnly = inheritOnly, noPropagate = noPropagate)

        def __str__(self):
            r = ""
            r += SynoACL._formatPermission("f", self.fileInherited)
            r += SynoACL._formatPermission("d", self.directoryInherited)
            r += SynoACL._formatPermission("i", self.inheritOnly)
            r += SynoACL._formatPermission("n", self.noPropagate)
            return r

        def __eq__(self, other):
            # Cheating a bit but performance is not that important and it saves typing
            return str(self) == str(other)

        def __ne__(self, other):
            return not self.__eq__(other)

    def __init__(self, role, name, aclType, permissions, inheritMode):
        self.role = role
        self.name = name
        self.aclType = aclType
        self.permissions = permissions
        self.inheritMode = inheritMode

    def setTarget(self, role, name):
        self.role = role
        self.name = name

    def setAclType(self, aclType):
        self.aclType = aclType

    def setPermissions(self, permissions):
        self.permissions = permissions

    def setInheritMode(self, inheritMode):
        self.inheritMode = inheritMode

    _SYNOACL_REGEX = re.compile(r"^([^:]+):([^:]+):([^:]+):([^:]+):([^ ]+)$")

    @staticmethod
    def fromString(s):
        m = SynoACL._SYNOACL_REGEX.match(s)
        if not m:
            raise Exception("The passed string does not match the synoacl format! (received: '%s')" % s)

        return SynoACL(role = m.group(1), name = m.group(2), aclType = m.group(3),
            permissions = SynoACL.Permissions.fromString(m.group(4)),
            inheritMode = SynoACL.Inheritance.fromString(m.group(5)))

    @staticmethod
    def _formatPermission(permissionLetter, isSet):
        if isSet:
            return permissionLetter
        else:
            return "-"

    def __str__(self):
        return self.role + ":" + self.name + ":" + self.aclType + ":" + str(self.permissions) + ":" + str(self.inheritMode)

    def __eq__(self, other):
        return self.role == other.role \
            and self.name == other.name \
            and self.aclType == other.aclType \
            and self.permissions == other.permissions \
            and self.inheritMode == other.inheritMode

    def __ne__(self, other):
        return not self.__eq__(other)


class SynoACLSet(object):
    def __init__(self, acls, levels = None):
        if levels != None and len(acls) != len(levels):
            raise Exception("Number of ACLs and number of levels don't match!")

        self._direct = []

        if levels == None:
            # all ACLs are direct
            self._all = []
            for acl in acls:
                self._direct.append(acl)
                self._all.append({"acl": acl, "level": 0})
        else:
            # there can be indirect ACLs too
            self._all = []
            for i in range(0, len(acls)):
                acl = acls[i]
                level = levels[i]
                if level == 0:
                    self._direct.append(acl)
                self._all.append({"acl": acl, "level": level})

    def getDirect(self):
        return self._direct

    def getAll(self):
        return self._all

    def __str__(self):
        s = ""
        if self._all != None:
            for i in range(0, len(self._all)):
                entry = self._all[i]
                acl = entry["acl"]
                level = entry["level"]
                s += "[" + str(i) + "] " + str(acl) + " (level: " + str(level) + ")\n"
        else:
            for i in range(0, len(self._direct)):
                acl = self._direct[i]
                s += "[" + str(i) + "] " + str(acl) + "\n"
        return s

    class Iterator(object):
        def __init__(self, synoAclSet):
            self._index = 0
            self._synoAclSet = synoAclSet

        def __iter__(self):
            return self

        def next(self):
            acls = self._synoAclSet._direct
            if self._index >= len(acls):
                raise StopIteration()
            acl = acls[self._index]
            self._index += 1
            return acl

    # TODO: the semantics of this is wrong, remove it and use explicit getAll/getDirect
    def __iter__(self):
        return SynoACLSet.Iterator(self)

class SynoACLArchive(object):
    """This class represents the flags that SynoACL associates with each directory. They determine:
        * if SynoACL is enabled for given path (is_support_ACL)
        * if the directory is read-only (isReadOnly)
        * if all the files created in the directory are owned by the group that owns the directory (isOwnerGroup)
        * if the path has any ACLs set (has_ACL)
        * if the ACLs of the parent directory are to be inherited (is_inherit)
    """

    _FLAG_IS_INHERIT = "is_inherit"
    _FLAG_IS_READ_ONLY = "is_read_only"
    _FLAG_IS_OWNER_GROUP = "is_owner_group"
    _FLAG_HAS_ACL = "has_ACL"
    _FLAG_IS_SUPPORT_ACL = "is_support_ACL"
    _FLAG_NONE = "None"

    def __init__(self, isInherit = False, isReadOnly = False, isOwnerGroup = False, hasACL = False, isSupportACL = False):
        self.isInherit = isInherit
        self.isReadOnly = isReadOnly
        self.isOwnerGroup = isOwnerGroup
        self.hasACL = hasACL
        self.isSupportACL = isSupportACL

    def isNone(self):
        return not(self.isInherit or self.isReadOnly or self.isOwnerGroup or self.hasACL or self.isSupportACL)

    @staticmethod
    def fromString(s):
        flags = filter(lambda s: s != "", map(lambda s: s.strip(), s.split(',')))

        isInherit = False
        isReadOnly = False
        isOwnerGroup = False
        hasACL = False
        isSupportACL = False
        for flag in flags:
            if flag == SynoACLArchive._FLAG_IS_INHERIT:
                isInherit = True
            elif flag == SynoACLArchive._FLAG_IS_READ_ONLY:
                isReadOnly = True
            elif flag == SynoACLArchive._FLAG_IS_OWNER_GROUP:
                isOwnerGroup = True
            elif flag == SynoACLArchive._FLAG_HAS_ACL:
                hasACL = True
            elif flag == SynoACLArchive._FLAG_IS_SUPPORT_ACL:
                isSupportACL = True
            elif flag == SynoACLArchive._FLAG_NONE:
                pass # ignore

        return SynoACLArchive(isInherit = isInherit, isReadOnly = isReadOnly, isOwnerGroup = isOwnerGroup,
            hasACL = hasACL, isSupportACL = isSupportACL)

    def __str__(self):
        flags = []
        if self.isInherit:
            flags.append(SynoACLArchive._FLAG_IS_INHERIT)
        if self.isReadOnly:
            flags.append(SynoACLArchive._FLAG_IS_READ_ONLY)
        if self.isOwnerGroup:
            flags.append(SynoACLArchive._FLAG_IS_OWNER_GROUP)
        if self.hasACL:
            flags.append(SynoACLArchive._FLAG_HAS_ACL)
        if self.isSupportACL:
            flags.append(SynoACLArchive._FLAG_IS_SUPPORT_ACL)
        if len(flags) == 0:
            return SynoACLArchive._FLAG_NONE
        return ",".join(flags)

    def __eq__(self, other):
        # Cheating a bit but performance is not that important and it saves typing
        return str(self) == str(other)

    def __ne__(self, other):
        return not self.__eq__(other)

class SynoACLTool(object):
    """A wrapper around synoacltool.

    ACLs and Archive flags are wrapped in python classes which should be
    easier to work with than with plain strings.

    Soem naming is rather strange ("archive" used for ACL flags) but I chose to keep
    the names used close to synoacltool to stay consistent.
    """

    _SYNOACL_CMD = "synoacltool"
    _SYNOACL_REGEX = re.compile(r"^\t *\[([0-9]+)\] +([^ ]+) +\(level:([0-9]+)\)$")
    _ARCHIVE_REGEX = re.compile(r"^Archive: (.+)$")

    @staticmethod
    def _communicate(args):
        return subprocess.check_output([ SynoACLTool._SYNOACL_CMD ] + args, universal_newlines = True).split("\n")

    @staticmethod
    def _parseACLResult(results):
        acls = []
        levels = []
        for line in results:
            m = SynoACLTool._SYNOACL_REGEX.match(line)
            if m:
                entryId = int(m.group(1))
                aclString = m.group(2)
                if entryId != len(acls):
                    raise Exception("Unexpected index of ACL entry: expected " + str(entryId) + ", got: " + str(len(acls)))
                level = int(m.group(3))
                acls.append(SynoACL.fromString(aclString))
                levels.append(level)
        return SynoACLSet(acls, levels)

    @staticmethod
    def get(path):
        """Return the ACLs that are associated with given path.

        The returned object is an instance of SynoACLSet.
        """
        try:
            return SynoACLTool._parseACLResult(SynoACLTool._communicate(["-get", path]))
        except subprocess.CalledProcessError:
            # FIXME: synoacltool -get returns "(synoacltool.c, 350)It's Linux mode" when there are no ACLs for the path
            return SynoACLSet([])

    @staticmethod
    def add(path, acl):
        """Add an ACL entry to given path.

        Returns the resulting ACLs as an SynoACLSet.
        """
        return SynoACLTool._parseACLResult(SynoACLTool._communicate(["-add", path, str(acl)]))

    @staticmethod
    def deleteEntry(path, index):
        """Delete an existing ACL entry by its index.

        Returns the resulting ACLs as an SynoACLSet.
        """
        return SynoACLTool._parseACLResult(SynoACLTool._communicate(["-del", path, str(index)]))

    @staticmethod
    def replace(path, index, acl):
        """Replace an existing ACL entry.

        Returns the resulting ACLs as an SynoACLSet.
        """
        return SynoACLTool._parseACLResult(SynoACLTool._communicate(["-replace", path, str(index), str(acl)]))

    @staticmethod
    def deleteAll(path):
        """Deletes all (direct) ACL entris for given path.

        Note that the actual Synology NAS behaviour seems to be to also reset archive flags.
        """
        # synoacltool returns "(synoacltool.c, 385)Index out of range" when
        # there are no ACLs defined and -del is used
        if len(SynoACLTool.get(path).getAll()) > 0:
            SynoACLTool._communicate(["-del", path])
        # else: no need to do anything

    @staticmethod
    def deleteForRole(path, role, name):
        """A helper function that deletes ACLs for given name."""
        # find role
        acls = SynoACLTool.get(path)
        directACLs = acls.getDirect()

        # FIXME: there could be probably two entries - an ALLOW and a DENY entry
        for i in range(0, len(directACLs)):
            acl = directACLs[i]
            if acl.role == role and acl.name == name:
                return SynoACLTool.deleteEntry(path, i)

        raise Exception("Could not find role:name " + role + ":" + name + " in ACL for path " + path)

    @staticmethod
    def reset(path, acls):
        SynoACLTool.deleteAll(path)
        for acl in acls:
            SynoACLTool.add(path, acl)

    @staticmethod
    def adaptTo(path, acls):
        """A "softer" version of SynoACLTool.reset().

        It does not delete all rules and set the new ones, but only adapts existing rules
        doing minimal number of changes.
        """
        requestedAclMap = dict()

        def aclKey(acl):
            return (acl.role, acl.name, acl.aclType)

        # turn the acls list into a map of (role, name, type) -> rights
        for acl in acls:
            requestedAclMap[aclKey(acl)] = acl

        existingAcls = SynoACLTool.get(path).getDirect()

        # the indices do change after a replace() and perhaps also after other operations
        # => store the operations and then perform them
        aclsToDelete = []
        aclsToModify = []

        def findACLIndex(path, acl):
            acls = SynoACLTool.get(path).getDirect()
            for i in range(len(acls)):
                if acl == acls[i]:
                    return i
            # this should not happen - unless the ACLs change from the outside while we're changing it
            raise Exception("ACL " + str(acl) + " not present in the ACL list for " + path)

        # iterate over existing ACLs and record required changes
        for existingAcl in existingAcls:
            try:
                key = aclKey(existingAcl)
                matchedAcl = requestedAclMap[key]
                # compare and check if the right is to be adapted or kept as is
                if existingAcl.permissions != matchedAcl.permissions or existingAcl.inheritMode != matchedAcl.inheritMode:
                    aclsToModify.append((existingAcl, matchedAcl))
                #else: keep as is
                # delete the key so at to mark is as processed
                del requestedAclMap[key]
            except KeyError:
                # no such entry in the requested keys -> delete the entry
                aclsToDelete.append(existingAcl)

        for aclToDelete in aclsToDelete:
            SynoACLTool.deleteEntry(path, findACLIndex(path, aclToDelete))

        for (aclToModifyFrom, aclToModifyTo) in aclsToModify:
            SynoACLTool.replace(path, findACLIndex(path, aclToModifyFrom), aclToModifyTo)

        # add what's left
        for aclToAdd in requestedAclMap.itervalues():
            SynoACLTool.add(path, aclToAdd)

    @staticmethod
    def _parseArchiveResult(result):
        if len(result) != 2 or result[1] != "":
            raise Exception("Unexpected format of SynoACL archive flags: %s" % result)

        m = SynoACLTool._ARCHIVE_REGEX.match(result[0])
        if not m:
            raise Exception("Unexpected format of SynoACL archive flags: %s" % result)

        return SynoACLArchive.fromString(m.group(1))

    @staticmethod
    def getArchive(path):
        """Return SynoACL Archive flags.

        See the documentation of SynoACLArchive for more info on the flags.
        """
        return SynoACLTool._parseArchiveResult(SynoACLTool._communicate(["-get-archive", path]))

    @staticmethod
    def setArchive(path, synoACLArchive):
        """Set one or more archive flags for given path.

        This only adds flags that are dpecified, no flags are unset by this.

        See the documentation of SynoACLArchive for more info on the flags.
        """
        return SynoACLTool._parseArchiveResult(SynoACLTool._communicate(["-set-archive", path, str(synoACLArchive)]))

    @staticmethod
    def delArchive(path, synoACLArchive):
        """Unset one or more archive flags for given path.

        See the documentation of SynoACLArchive for more info on the flags.
        """
        return SynoACLTool._parseArchiveResult(SynoACLTool._communicate(["-del-archive", path, str(synoACLArchive)]))

    @staticmethod
    def setArchiveTo(path, requestedFlags):
        """Set SynoACL Archive flags to match the flags passed."""
        existingFlags = SynoACLTool.getArchive(path)
        # drop flags which are to be dropped
        flagsToDrop = SynoACLArchive()
        if existingFlags.isInherit and not requestedFlags.isInherit:
            flagsToDrop.isInherit = True
        if existingFlags.isReadOnly and not requestedFlags.isReadOnly:
            flagsToDrop.isReadOnly = True
        if existingFlags.isOwnerGroup and not requestedFlags.isOwnerGroup:
            flagsToDrop.isOwnerGroup = True
        if existingFlags.isSupportACL and not requestedFlags.isSupportACL:
            flagsToDrop.isSupportACL = True
        if not flagsToDrop.isNone():
            SynoACLTool.delArchive(path, flagsToDrop)
        # else: no need to do anything

        # set flags which are to be set
        flagsToSet = SynoACLArchive()
        if not existingFlags.isInherit and requestedFlags.isInherit:
            flagsToSet.isInherit = True
        if not existingFlags.isReadOnly and requestedFlags.isReadOnly:
            flagsToSet.isReadOnly = True
        if not existingFlags.isOwnerGroup and requestedFlags.isOwnerGroup:
            flagsToSet.isOwnerGroup = True
        if not existingFlags.isSupportACL and requestedFlags.isSupportACL:
            flagsToSet.isSupportACL = True
        if not flagsToSet.isNone():
            SynoACLTool.setArchive(path, flagsToSet)
        # else: no need to do anything

    @staticmethod
    def enforceInherit(path):
        SynoACLTool._communicate(["-enforce-inherit", path])
