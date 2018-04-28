from setuptools import setup

setup(name='urlsave',
      version='0.1',
      description='Parse websites and save content specified with XPath',
      url='https://github.com/iiLaurens/urlsave',
      author='Laurens Janssen',
      author_email='github@laurens.xyz',
      license='MIT',
      packages=['urlsave'],
      install_requires=[
          'lxml',
		  'selenium',
		  'poyo'
      ],
      zip_safe=False)