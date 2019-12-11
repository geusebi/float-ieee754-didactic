import setuptools

short_desc = (
    "Educational python module to parse floats and inspect the "
    "IEEE754 algorithm's internals."
)
long_desc = open("README.md").read()

setuptools.setup(
    name='floatedu',
    version='0.0.2',
    packages=('floatedu', ),

    description=short_desc,
    long_description=long_desc,
    long_description_content_type='text/markdown',

    # url git
    url='https://gitlab.com/geusebi/float-ieee754-didactic',

    python_requires='>=3.6',
    install_requires=tuple(),

    author='Giampaolo Eusebi',
    author_email='giampaolo.eusebi@gmail.com',

    license='GNU GPL 3.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Education',
    ],
)
