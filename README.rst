Synoacl
=======

Python module to interact with ``synoacltool``, the CLI tool for
accessing Synology_ NAS proprietary ACL implementation.

The module is to be run on an actual Synology NAS itself. It can be
useful when scripting tasks that involve setting the ACLs.

Installation
------------

This package can be installed with ``pip``:

.. code-block:: bash

    $ pip install git+https://github.com/zub2/synoacl.git

Some tests are included. You can run them by cloning the repository and
running

.. code-block:: bash

    $ python setup.py test

The module should work both with python 2 and python 3. It installs even
on the PC but it's not of much use outside of a Synology NAS and the
tests won't pass for obvious reasons.

.. links:
.. _Synology: https://www.synology.com/

Synology ACLs
-------------

Unfortunately, there is not much documentation about ``synoacltool`` and
the details of Synology ACL implementation (at least I haven't found
much) so using ``synoacltool`` is a bit of a guesswork.

To get an idea it's useful to run ``synoacltool`` without any arguments
and read the usage summary it prints.

The two important concepts are:

- *ACL Archive* (think directory flags): these specify among others if
  the directory can have ACLs at all (``is_support_ACL``) and if ACLs
  from the parents are inherited into this directory (``is_inherit``)
- *ACL entries*: these specify the actual rights in a way similar to
  normal Linux ACLs but with more flags. Also note that each ACL has a
  *level*. A level of 0 means it's ACL defined on the directory you
  query. Higher levels (1, 2, ...) mean it's an entry inherited from a
  parent, or a parent of a parent, etc. The level only shows up when
  querying the ACLs, it makes no sense when setting ACLs (you always
  set ACLs on the directory you specify, so they end up as ACL entries
  with level 0).

Usage
-----

This module mostly just wraps the ``synoacltool``. To use this module,
import ``synoacl.tool``. The main class to access the ACLs is
``synoacl.tool.SynoACLTool``. To get the ACLs you can do:

.. code-block:: python

    from synoacl.tool import SynoACLTool
    aclSet = SynoACLTool.get(".")
    print(aclSet)

and you get something like:

::

    [0] user:zub:allow:rwxpdDaARWc--:fd-- (level: 0)
    [1] group:administrators:allow:rwxpdDaARWc--:fd-- (level: 1)
    [2] group:wheel:allow:rwxp--a-R-c--:fd-- (level: 1)

which is similar to what you get with ``synoacltool -get .``, but with
this module the results are already parsed and so they are a bit easier
to manipulate.

To add an ACL entry:

.. code-block:: python

    from synoacl.tool import SynoACL, SynoACLTool
    newAcl = SynoACL("user", "guest", "allow", SynoACL.Permissions(readData = True, readAttribute = True,
        readXAttr = True, readAcl = True), SynoACL.Inheritance(noPropagate = True))
    newAclSet = SynoACLTool.add(".", newAcl)
    print(newAclSet)

and you get something like:

::

    [0] user:guest:allow:r-----a-R-c--:---n (level: 0)
    [1] user:zub:allow:rwxpdDaARWc--:fd-- (level: 0)
    [2] group:administrators:allow:rwxpdDaARWc--:fd-- (level: 1)
    [3] group:wheel:allow:rwxp--a-R-c--:fd-- (level: 1)

Note that all the classes that are used to hold an ACL entry
(``SynoACL.Permissions``, ``SynoACL.Inheritance``, ``SynoACL``) as well
as the class for ACL flags (``SynoACLArchive``) define a static
``fromString`` method that can be used to parse the format as used by
``synoacltool`` and they also define the ``__str__`` method that
produces the string representation of the instance, e.g.:

.. code-block:: python

    from synoacl.tool import SynoACL
    acl = SynoACL.fromString("user:guest:allow:r-----a-R-c--:---n")
    print(acl)

On top of wrapping the ``synoacltool``, there are some helper methods:

- ``SynoACLTool.deleteForRole(path, role, name)``: delete ACL entry for
  given role and name. This essentially combines a get with a lookup
  of the entry to be deleted and deletion.
- ``SynoACLTool.adaptTo(path, aclSet)``: A "softer" way to make sure the
  ACLs are as requested. Instead of deleting all ACLs and setting the
  new ACLs, this function makes only the changes that are necessary;
  in case the current ACLs are identical to the requested ACLs, no
  change is made
- ``SynoACLTool.setArchiveTo(path, requestedFlags)``: ``synoacltool``'s
  --set-archive only turns requested flags *on*; this function can be
  used to make sure the archive flags are exactly as requested

TODOs
-----
There are some important things missing:

- support special roles with empty names (``Owner``/``Everyone``/``Authenticated Users``)
- improve documentation
- better error handling: capture ``stderr``
