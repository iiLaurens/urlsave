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
		'pyyaml',
        'websocket-client',
        'requests',
        'python-telegram-bot'		
      ],
      zip_safe=False)