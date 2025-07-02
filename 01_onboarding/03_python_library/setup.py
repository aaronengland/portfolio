from setuptools import setup, find_packages

setup(
    name='my_library',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
    ],
    author='Bison Dele',
    author_email='bisondele@gopfs.com',
    description='Bison\'s Library',
    url='https://github.com/PFS-Risk-DS/my_library.git',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
