from setuptools import setup, find_packages


def readme():
	with open('./README.md') as f:
		return f.read()


setup(
	name='soupspoon',
	version='2022.4.20',
	license='MIT',

	url='https://github.com/idin/soupspoon',
	author='Idin',
	author_email='py@idin.ca',

	description='Additional functionality for BeautifulSoup',
	long_description=readme(),
	long_description_content_type='text/markdown',

	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Programming Language :: Python :: 3 :: Only',
		'Programming Language :: Python :: 3.6',
		'Programming Language :: Python :: 3.7',
		'Topic :: Software Development :: Libraries :: Python Modules'
	],

	packages=find_packages(exclude=["jupyter_tests", ".idea", ".git"]),
	install_requires=['bs4', 'joblib', 'pandas', 'disk', 'lxml', 'slytherin', 'txt'],
	python_requires='~=3.6',
	zip_safe=False
)
