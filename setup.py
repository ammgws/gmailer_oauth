from setuptools import setup

version = {}
with open("__version__.py") as fp:
    exec(fp.read(), version)

setup(
    name='gmailer_oauth',
    version=version['__version__'],
    description='Send emails via Gmail using OAuth',
    url='https://github.com/ammgws/gmailer-oauth',
    author='Jason N.',
    author_email='ammgws@users.noreply.github.com',
    py_modules=['gmailer_oauth'],
    entry_points='''
        [console_scripts]
        gmailer_oauth=gmailer_oauth:main
    ''',
    python_requires='>=3.6',
    install_requires=[
        'click',
        'requests',
        'google_auth',
    ],
    dependency_links=['git+https://github.com/ammgws/google_auth.git/#egg=google_auth-0'],
    classifiers=[
        'Topic :: Communications :: Email',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.6',
    ],
)
