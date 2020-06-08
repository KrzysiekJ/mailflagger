from setuptools import find_namespace_packages, setup


with open('README.md') as f:
    long_description = f.read()

setup(
    name='mailflagger',
    version='0.1.0',
    description='A program which flags emails, typically after an incoming payment',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://mailflagger.org',
    author='Krzysztof Jurewicz',
    author_email='krzysztof.jurewicz@gmail.com',
    python_requires='>=3.8, <4',
    packages=find_namespace_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: No Input/Output (Daemon)',
        'Environment :: MacOS X :: Cocoa',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Framework :: AsyncIO',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.8',
        'Topic :: Communications :: Email :: Filters',
    ],
    install_requires=[
        'pyzmq>=19,<20',
        'setuptools',
        'msgpack>=1,<2',
    ],
    extras_require={
        'GUI': [
            # Freezing wxPython version because of https://github.com/chriskiehl/Gooey/pull/555/ and https://github.com/chriskiehl/Gooey/issues/549 .
            'wxpython==4.0.7.post2',
            'Gooey==1.0.3',
        ],
    },
    entry_points={
        'gui_scripts': [
            'mailflagger = mailflagger.cmd:main',
        ],
        'mailflagger.plugins.commands': [
            'flag = mailflagger.plugins.manual',
            'daemon = mailflagger.server',
        ],
    },
)
