import os
import stat
from random import randint
from hashlib import md5


def zerostatus():
    return {"OK": 0, "TC": 0, "NC": 0, "MD": 0, "LC": 0, "RM": 0, "??": 0}


def randrepo():
    return f"gin-test-{randint(0, 9999):04}"


def mkrandfile(name, size=100):
    """
    Make a random binary file with a given name and size in kilobytes
    (default: 100k)
    """
    with open(name, "wb") as f:
        f.write(os.urandom(size*1024))


def getrevcount(r):
    """
    Total number of revisions from HEAD.
    """
    n, _ = r.runcommand("git", "rev-list", "--count", "master")
    return int(n)


def assert_status(r, path=".", status=dict()):
    """
    Run `gin ls --short` and check the count for each status against the given
    `status` dictionary.
    """
    out, err = r.runcommand("gin", "ls", "--short", path)
    actual = {}
    for code, count in status.items():
        s = sum(1 for line in out.splitlines() if line.startswith(code))
        actual[code] = s
    assert status == actual, (f"Status count mismatch\n"
                              f"Exp: {status}\n"
                              f"Act: {actual}")


def md5sum(filename, printhash=False):
    with open(filename, "rb") as thefile:
        fdata = thefile.read()
        msum = md5(fdata).hexdigest()
    return msum


def hashtree(r):
    curtree = dict()
    head, err = r.runcommand("git", "rev-parse", "HEAD")
    print(f"Hashing files in working tree (at {head})")

    gitfiles, err = r.runcommand("git", "ls-files")
    gitfiles = gitfiles.splitlines()
    r.runcommand("gin", "get-content", ".")
    for filepath in gitfiles:
        # normalise path separator (for Windows)
        filepath = os.path.normpath(filepath)
        msum = md5sum(filepath)
        curtree[filepath] = msum
        # print(f"{filepath}: {msum}")

    return head, curtree


def lsfiles(path):
    files = []
    for root, dirs, fnames in os.walk(path):
        files.extend([os.path.join(root, f)
                      for f in fnames])
    return files


def isannexed(r, fname):
    """
    Figure out if a file is annexed or not:
    - If the file's git content is binary (UnicodeDecodeError), it's not
      annexed [False]
    - If it's not binary and the contents include the string "/objects/", it's
      a pointer file for annexed content [True]
    - If it's a symlink, it's a pointer file for annexed content [True]
    - Otherwise, it's not annexed [False]
    """
    try:
        out, err = r.runcommand("git", "cat-file", "-p", f":{fname}")
    except (UnicodeDecodeError, IndexError):
        # For some reason on Windows a UnicodeDecodeError results in an
        # IndexError
        # binary file in git -> not annexed
        return False
    if "/objects/" in out:
        return True
    if os.path.islink(fname):
        return True
    return False


def force_rm(func, path, excinfo):
    os.chmod(path, stat.S_IWRITE)
    func(path)


def set_rwx_recursive(path):
    # set full permissions on everything under the tempdir
    for root, dirs, files in os.walk(path):
        for d in dirs:
            dname = os.path.join(root, d)
            os.chmod(dname, 0o777)
        for f in files:
            fname = os.path.join(root, f)
            if os.path.exists(fname):  # skip broken links
                os.chmod(fname, 0o777)
