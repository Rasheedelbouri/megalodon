import imp
import os
import subprocess
import sys
import time

from glob import glob
from setuptools import setup, find_packages
from setuptools.extension import Extension


__pkg_name__ = 'megalodon'

MAJOR = 0
MINOR = 0
REVISION = 1


def git_hash():
    commit=0
    #commit = subprocess.check_output([
    #    'git', 'rev-parse', '--short', 'HEAD']).decode().strip()
    return commit

def git_revision():
    revision=0
    #revision = subprocess.check_output([
    #    'git', 'rev-list', '--count', 'HEAD']).decode().strip()
    return int(revision)

version_module = '''"""
{pkg_name}/version.py
This file was generated by setup.py at: {time}
"""

__version__ = "{version}"
major = {major}
minor = {minor}
revision = {revision}
git_revision = {git_revision}
git_hash = "{git_hash}"
'''

def write_version(fn="{}/version.py".format(__pkg_name__)):
    GIT_REVISION = git_revision()
    GIT_HASH = git_hash()
    version = "{}.{}.{}".format(MAJOR, MINOR, REVISION)
    with open(fn, 'w') as f:
        f.write(version_module.format(
            pkg_name=__pkg_name__,
            time=time.strftime("%a, %d %b %Y %H:%M:%S GMT%z", time.localtime()),
            version=version, major=MAJOR, minor=MINOR,
            revision=REVISION, git_revision=GIT_REVISION, git_hash=GIT_HASH))


THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(THIS_DIR, ".git")):
    # If this is a git repo, write the version. Otherwise assume we are
    # installing from a wheel
    write_version()


_version = imp.load_source(
    "version", "{}/version.py".format(__pkg_name__))
version = _version.__version__


try:
    root_dir = os.environ['ROOT_DIR']
except KeyError:
    root_dir = '.'


install_requires = [
    "h5py >= 2.2.1",
    "numpy >= 1.9.0",
    "Cython >= 0.25.2",
    "mappy >= 2.15",
    "pysam >= 0.15",
    "tqdm",
]


#  Build extensions
try:
    import numpy as np
    from Cython.Build import cythonize
    extensions = cythonize([
        Extension(__pkg_name__ + ".decode", [
            os.path.join(__pkg_name__, "_decode.pyx"),
            os.path.join(__pkg_name__, "_c_decode.c")],
                  include_dirs=[np.get_include()],
                  extra_compile_args=["-O3", "-fopenmp", "-std=c99",
                                      "-march=native"],
                  extra_link_args=["-fopenmp"]),
    ])
except ImportError:
    extensions = []
    sys.stderr.write("WARNING: Numpy and Cython are required to build " +
                     "megalodon extensions\n")
    if any([cmd in sys.argv for cmd in [
            "install", "build", "build_clib", "build_ext", "bdist_wheel"]]):
        raise


setup(
    name=__pkg_name__,
    version=version,
    description='Nanopore base calling augmentation',
    maintainer='Marcus Stoiber',
    maintainer_email='marcus.stoiber@nanoporetech.com',
    url='http://www.nanoporetech.com',
    long_description=(
        'Megalodon contains base calling augmentation capabilities, mainly ' +
        'including direct, reference-guided SNP and modified base detection.'),

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Mathematics'
    ],

    packages=find_packages(exclude=[
        "*.test", "*.test.*", "test.*", "test", "bin"]),
    package_data={'configs': 'data/configs/*'},
    exclude_package_data={'': ['*.hdf', '*.c', '*.h']},
    ext_modules=extensions,
    install_requires=install_requires,
    dependency_links=[],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            '{0} = {0}.{0}:_main'.format(__pkg_name__)
        ]
    },

)
