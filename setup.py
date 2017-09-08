from distutils.core import setup
import sys

if sys.version_info >= (3,):
    sys.exit('Sorry, Python 3 is not supported')

setup(
    name='codequick',
    version='0.0.1',
    description='Launch kodi add-ons from outside kodi.',
    keywords='kodi plugin addon add-on cli',
    classifiers=['Development Status :: 4 - Beta',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: MIT License',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 2.7',
                 'Topic :: Software Development'],
    url='',
    author='william Forde',
    author_email='willforde@gmail.com',
    license='MIT License',
    platforms=['OS Independent'],
    package_dir={'': 'cli'},
    packages=['codequickcli'],
    py_modules=['xbmc', 'xbmcaddon', 'xbmcgui', 'xbmcplugin'],
    entry_points={'console_scripts': ['codequickcli=codequickcli.cli:main']}
)