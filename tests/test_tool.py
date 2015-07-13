import unittest
import os
import shutil
import subprocess

from synoacl.tool import SynoACL, SynoACLSet, SynoACLArchive, SynoACLTool

class TestPermissions(unittest.TestCase):
    NO_RIGHTS = "-------------"
    RWX_RIGHTS = "rwx----------"
    ALL_RIGHTS = "rwxpdDaARWcCo"

    def test_toString(self):
        permissions = SynoACL.Permissions()
        self.assertEqual(str(permissions), TestPermissions.NO_RIGHTS)

        permissions = SynoACL.Permissions(readData = True, writeData = True, execute = True)
        self.assertEqual(str(permissions), TestPermissions.RWX_RIGHTS)

        permissions = SynoACL.Permissions(readData = True, writeData = True, execute = True,
                appendData = True, delete = True, deleteChild = True, readAttribute = True,
                writeAttribute = True, readXAttr = True, writeXAttr = True, readAcl = True,
                writeAcl = True, getOwnership = True)
        self.assertEqual(str(permissions), TestPermissions.ALL_RIGHTS)

    def test_fromString(self):
        permissions = SynoACL.Permissions.fromString(TestPermissions.NO_RIGHTS)
        self.assertEqual(permissions.readData, False)
        self.assertEqual(permissions.writeData, False)
        self.assertEqual(permissions.execute, False)
        self.assertEqual(permissions.appendData, False)
        self.assertEqual(permissions.delete, False)
        self.assertEqual(permissions.deleteChild, False)
        self.assertEqual(permissions.readAttribute, False)
        self.assertEqual(permissions.writeAttribute, False)
        self.assertEqual(permissions.readXAttr, False)
        self.assertEqual(permissions.writeXAttr, False)
        self.assertEqual(permissions.readAcl, False)
        self.assertEqual(permissions.writeAcl, False)
        self.assertEqual(permissions.getOwnership, False)

        permissions = SynoACL.Permissions.fromString(TestPermissions.RWX_RIGHTS)
        self.assertEqual(permissions.readData, True)
        self.assertEqual(permissions.writeData, True)
        self.assertEqual(permissions.execute, True)
        self.assertEqual(permissions.appendData, False)
        self.assertEqual(permissions.delete, False)
        self.assertEqual(permissions.deleteChild, False)
        self.assertEqual(permissions.readAttribute, False)
        self.assertEqual(permissions.writeAttribute, False)
        self.assertEqual(permissions.readXAttr, False)
        self.assertEqual(permissions.writeXAttr, False)
        self.assertEqual(permissions.readAcl, False)
        self.assertEqual(permissions.writeAcl, False)
        self.assertEqual(permissions.getOwnership, False)

        permissions = SynoACL.Permissions.fromString(TestPermissions.ALL_RIGHTS)
        self.assertEqual(permissions.readData, True)
        self.assertEqual(permissions.writeData, True)
        self.assertEqual(permissions.execute, True)
        self.assertEqual(permissions.appendData, True)
        self.assertEqual(permissions.delete, True)
        self.assertEqual(permissions.deleteChild, True)
        self.assertEqual(permissions.readAttribute, True)
        self.assertEqual(permissions.writeAttribute, True)
        self.assertEqual(permissions.readXAttr, True)
        self.assertEqual(permissions.writeXAttr, True)
        self.assertEqual(permissions.readAcl, True)
        self.assertEqual(permissions.writeAcl, True)
        self.assertEqual(permissions.getOwnership, True)

    def test_eq(self):
        permissions1 = SynoACL.Permissions()
        permissions2 = SynoACL.Permissions.fromString(TestPermissions.NO_RIGHTS)
        self.assertEqual(permissions1, permissions2)

        permissions1 = SynoACL.Permissions.fromString(TestPermissions.ALL_RIGHTS)
        permissions2 = SynoACL.Permissions.fromString(TestPermissions.ALL_RIGHTS)
        self.assertEqual(permissions1, permissions2)

    def test_ne(self):
        permissions1 = SynoACL.Permissions()
        permissions2 = SynoACL.Permissions.fromString(TestPermissions.ALL_RIGHTS)
        self.assertNotEqual(permissions1, permissions2)

        permissions1 = SynoACL.Permissions.fromString(TestPermissions.NO_RIGHTS)
        permissions2 = SynoACL.Permissions.fromString(TestPermissions.ALL_RIGHTS)
        self.assertNotEqual(permissions1, permissions2)

class TestInheritance(unittest.TestCase):
    INHERIT_NOTHING= "---n"
    INHERIT_ALL = "fdi-"

    def test_toString(self):
        inheritance = SynoACL.Inheritance(noPropagate = True)
        self.assertEqual(str(inheritance), TestInheritance.INHERIT_NOTHING)

        inheritance = SynoACL.Inheritance(fileInherited = True, directoryInherited = True,
            inheritOnly = True)
        self.assertEqual(str(inheritance), TestInheritance.INHERIT_ALL)

    def test_fromString(self):
        inheritance = SynoACL.Inheritance.fromString(TestInheritance.INHERIT_NOTHING)
        self.assertEqual(inheritance.fileInherited, False)
        self.assertEqual(inheritance.directoryInherited, False)
        self.assertEqual(inheritance.inheritOnly, False)
        self.assertEqual(inheritance.noPropagate, True)

        inheritance = SynoACL.Inheritance.fromString(TestInheritance.INHERIT_ALL)
        self.assertEqual(inheritance.fileInherited, True)
        self.assertEqual(inheritance.directoryInherited, True)
        self.assertEqual(inheritance.inheritOnly, True)
        self.assertEqual(inheritance.noPropagate, False)

    def test_eq(self):
        inheritance1 = SynoACL.Inheritance(noPropagate = True)
        inheritance2 = SynoACL.Inheritance.fromString(TestInheritance.INHERIT_NOTHING)
        self.assertEqual(inheritance1, inheritance2)

        inheritance1 = SynoACL.Inheritance(fileInherited = True, directoryInherited = True,
            inheritOnly = True)
        inheritance2 = SynoACL.Inheritance.fromString(TestInheritance.INHERIT_ALL)
        self.assertEqual(inheritance1, inheritance2)

    def test_ne(self):
        inheritance1 = SynoACL.Inheritance(noPropagate = True)
        inheritance2 = SynoACL.Inheritance.fromString(TestInheritance.INHERIT_ALL)
        self.assertNotEqual(inheritance1, inheritance2)

        inheritance1 = SynoACL.Inheritance(fileInherited = True, directoryInherited = True,
            inheritOnly = True)
        inheritance2 = SynoACL.Inheritance.fromString(TestInheritance.INHERIT_NOTHING)
        self.assertNotEqual(inheritance1, inheritance2)

class TestSynoACL(unittest.TestCase):
    TEST_ROLE = "user"
    TEST_NAME = "boss"
    TEST_TYPE = "allow"
    TEST_PERMISSIONS = "rwxpdDaARWcCo"
    TEST_INHERITANCE = "fdi-"
    def test_toString(self):
        acl = SynoACL(TestSynoACL.TEST_ROLE, TestSynoACL.TEST_NAME, TestSynoACL.TEST_TYPE,
            SynoACL.Permissions.fromString(TestSynoACL.TEST_PERMISSIONS),
            SynoACL.Inheritance.fromString(TestSynoACL.TEST_INHERITANCE))

        aclString = TestSynoACL.TEST_ROLE + ":" + TestSynoACL.TEST_NAME + ":" + \
            TestSynoACL.TEST_TYPE + ":" + TestSynoACL.TEST_PERMISSIONS + ":" + TestSynoACL.TEST_INHERITANCE
        self.assertEqual(aclString, str(acl))

    def test_fromString(self):
        aclString = TestSynoACL.TEST_ROLE + ":" + TestSynoACL.TEST_NAME + ":" + \
            TestSynoACL.TEST_TYPE + ":" + TestSynoACL.TEST_PERMISSIONS + ":" + TestSynoACL.TEST_INHERITANCE
        acl = SynoACL.fromString(aclString)

        self.assertEqual(acl.role, TestSynoACL.TEST_ROLE)
        self.assertEqual(acl.name, TestSynoACL.TEST_NAME)
        self.assertEqual(acl.aclType, TestSynoACL.TEST_TYPE)
        self.assertEqual(str(acl.permissions), TestSynoACL.TEST_PERMISSIONS)
        self.assertEqual(str(acl.inheritMode), TestSynoACL.TEST_INHERITANCE)

    def test_eq(self):
        aclString = TestSynoACL.TEST_ROLE + ":" + TestSynoACL.TEST_NAME + ":" + \
            TestSynoACL.TEST_TYPE + ":" + TestSynoACL.TEST_PERMISSIONS + ":" + TestSynoACL.TEST_INHERITANCE

        acl1 = SynoACL.fromString(aclString)
        acl2 = SynoACL.fromString(aclString)
        self.assertEqual(acl1, acl2)

    def test_ne(self):
        aclString = TestSynoACL.TEST_ROLE + ":" + TestSynoACL.TEST_NAME + ":" + \
            TestSynoACL.TEST_TYPE + ":" + TestSynoACL.TEST_PERMISSIONS + ":" + TestSynoACL.TEST_INHERITANCE
        acl1 = SynoACL.fromString(aclString)

        acl2 = SynoACL.fromString(aclString)
        acl2.role = "other"
        self.assertNotEqual(acl1, acl2)

        acl2 = SynoACL.fromString(aclString)
        acl2.name = "other"
        self.assertNotEqual(acl1, acl2)

        acl2 = SynoACL.fromString(aclString)
        acl2.aclType = "other"
        self.assertNotEqual(acl1, acl2)

        acl2 = SynoACL.fromString(aclString)
        acl2.permissions = SynoACL.Permissions()
        self.assertNotEqual(acl1, acl2)

        acl2 = SynoACL.fromString(aclString)
        acl2.inheritMode = SynoACL.Inheritance()
        self.assertNotEqual(acl1, acl2)

class TestSynoACLSet(unittest.TestCase):
    def test_emptyCtor(self):
        acls = SynoACLSet([])

        self.assertEqual(len(acls.getDirect()), 0)
        self.assertEqual(len(acls.getAll()), 0)

    def test_onlyDirectCtor(self):
        testACLs = [
            SynoACL.Permissions(),
            SynoACL.Permissions.fromString("rwx----------"),
            SynoACL.Permissions.fromString("rwxpdD-------")
        ]
        acls = SynoACLSet(testACLs)

        directACLs = acls.getDirect()
        self.assertEqual(len(directACLs), len(testACLs))
        for i in range(len(directACLs)):
            self.assertEqual(directACLs[i], testACLs[i])

        allACLs = acls.getAll()
        self.assertEqual(len(allACLs), len(allACLs))
        for i in range(len(allACLs)):
            entry = allACLs[i]
            self.assertEqual(entry["acl"], testACLs[i])
            self.assertEqual(entry["level"], 0)

    def test_mixedCtor(self):
        testACLs = [
            { "acl": SynoACL.Permissions(), "level": 0 },
            { "acl": SynoACL.Permissions.fromString("rwx----------"), "level": 1 },
            { "acl": SynoACL.Permissions.fromString("rwxpdD-------"), "level": 1 }
        ]
        testDirectACLs = list(map(lambda entry: entry["acl"], filter(lambda entry: entry["level"] == 0, testACLs)))

        allACLs = list(map(lambda entry: entry["acl"], testACLs))
        levels = list(map(lambda entry: entry["level"], testACLs))
        acls = SynoACLSet(allACLs, levels)

        directACLs = acls.getDirect()
        expectedDirectACLCount = sum(1 if entry["level"] == 0 else 0 for entry in testACLs)
        self.assertEqual(len(directACLs), expectedDirectACLCount)
        for i in range(len(directACLs)):
            self.assertEqual(directACLs[i], testDirectACLs[i])

        allACLs = acls.getAll()
        self.assertEqual(len(allACLs), len(allACLs))
        for i in range(len(allACLs)):
            entry = allACLs[i]
            self.assertEqual(entry["acl"], testACLs[i]["acl"])
            self.assertEqual(entry["level"], testACLs[i]["level"])

class TestSynoACLArchive(unittest.TestCase):
    def test_toString(self):
        archive = SynoACLArchive()
        self.assertEqual(str(archive), "None")

        archive = SynoACLArchive(isInherit = True, hasACL = True, isSupportACL = True)
        self.assertEqual(str(archive), "is_inherit,has_ACL,is_support_ACL")

    def test_fromString(self):
        archive = SynoACLArchive.fromString("None")
        self.assertEqual(archive.isInherit, False)
        self.assertEqual(archive.isReadOnly, False)
        self.assertEqual(archive.isOwnerGroup, False)
        self.assertEqual(archive.hasACL, False)
        self.assertEqual(archive.isSupportACL, False)

        archive = SynoACLArchive.fromString("is_inherit,has_ACL,is_support_ACL")
        self.assertEqual(archive.isInherit, True)
        self.assertEqual(archive.isReadOnly, False)
        self.assertEqual(archive.isOwnerGroup, False)
        self.assertEqual(archive.hasACL, True)
        self.assertEqual(archive.isSupportACL, True)

class TestSynoACLTool(unittest.TestCase):
    """The the SynoACLTool class

    This test can only be run on an actual Synology NAS where there is the
    "synoacltool" executable.
    """
    def setUp(self):
        self.testRunRoot = os.path.join(os.getcwd(), "test_run_dir")
        if os.path.exists(self.testRunRoot):
            raise Exception("The path '" + self.testRunRoot + "' already exists. Please delete it and run the test again.")
        os.mkdir(self.testRunRoot)

        # set the ACLs and archive flags to a known state
        fnull = open(os.devnull, 'w')
        subprocess.call([
            "synoacltool", "-del-archive", self.testRunRoot, "is_inherit,is_read_only,is_owner_group,is_support_ACL"
        ], stdout = fnull)
        subprocess.call([
            "synoacltool", "-set-archive", self.testRunRoot, "is_support_ACL"
        ], stdout = fnull) # don't inherit from parents to isolate outside interference
        subprocess.call([
            "synoacltool", "-del", self.testRunRoot
        ], stdout = fnull)
        subprocess.call([
            "synoacltool", "-add", self.testRunRoot, "group:administrators:allow:rwxpdDaARWc--:fd--"
        ], stdout = fnull)

        self.testDir = os.path.join(self.testRunRoot, "guinea-pig")
        os.mkdir(self.testDir)
        subprocess.call([
            "synoacltool", "-del-archive", self.testDir, "is_inherit,is_read_only,is_owner_group,is_support_ACL"
        ], stdout = fnull)
        subprocess.call([
            "synoacltool", "-set-archive", self.testDir, "is_support_ACL,is_inherit"
        ], stdout = fnull)
        subprocess.call([
            "synoacltool", "-del", self.testDir], stdout = fnull)
        subprocess.call([
            "synoacltool", "-add", self.testDir, "user:guest:allow:rwxpd--------:fd--"
        ], stdout = fnull)
        # It seems that the -del above affects the archive flags - it drops is_inherit
        subprocess.call([
            "synoacltool", "-set-archive", self.testDir, "is_inherit"
        ], stdout = fnull)

    def tearDown(self):
        shutil.rmtree(self.testRunRoot)

    @staticmethod
    def compareACLSets(a, b):
        """Compare two ACLSets without regards to the order of the entries."""
        allA = a.getAll()
        allB = b.getAll()

        if len(allA) != len(allB):
            return False

        for entryA in allA:
            # find entryA in allB
            i = 0
            while i < len(allB) and entryA["acl"] != allB[i]["acl"]:
                i += 1
            if i == len(allB):
                return False # entryA was not found in allB
            del allB[i]

        # all A's matched in B's and they have the same length -> they are the same
        return True

    def assertAclsEqual(self, a, b):
        if not TestSynoACLTool.compareACLSets(a, b):
            self.fail("ACLs differ: " + str(a) + " vs. " + str(b))

    def test_get(self):
        acls = SynoACLTool.get(self.testDir)
        expectedACLs = SynoACLSet([
            SynoACL.fromString("user:guest:allow:rwxpd--------:fd--"),
            SynoACL.fromString("group:administrators:allow:rwxpdDaARWc--:fd--")
        ], [0, 1])
        self.assertAclsEqual(acls, expectedACLs)

    # TODO: add more tests...


if __name__ == '__main__':
    unittest.main()
