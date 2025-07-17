from setuptools import setup, find_packages

setup(
    name='py_package_upgrader',
    version='0.1.0',
    author='Anish Karim',
    description="Tool to clean and upgrade requirements.txt intelligently",
    packages=find_packages(),
    install_requires=[
        'requests',
        'pip-autoremove',
        'pipreqs',
        'argparse'
    ],
    entry_points={
        'console_scripts': [
            'py-package-upgrader=py_package_upgrader.cli:main'
        ]
    },
    python_requires='>=3.6',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ]
)