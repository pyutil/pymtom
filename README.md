# pymtom

Sources on GitHub: [github.com/pyutil/pymtom](https://github.com/pyutil/pymtom).

## About state of this package

**Warning**: This package at first publishing is just alfa version.  
&nbsp;&nbsp;&nbsp;&nbsp;It could work, it could fail on some detail, it could fail with heavy things unsolved.  
&nbsp;&nbsp;&nbsp;&nbsp;The reason is that it is big problem to find a correct and free accessible SOAP MTOM service for development.  
&nbsp;&nbsp;&nbsp;&nbsp;So, give a try and go away, or (of course better) send a Merge Request.

**Warning**: My knowledges about SOAP and MTOM are low.  
&nbsp;&nbsp;&nbsp;&nbsp;I will be not very helpfull with future development if there will be any.  
&nbsp;&nbsp;&nbsp;&nbsp;If somebody more oriented in SOAP will create Merge Request it could be nice,  
&nbsp;&nbsp;&nbsp;&nbsp;otherwise you cannot wait something new here in the future.

However I see that we have no MTOM support in Python SOAP servers (Spyne)
and no MTOM creating support in Python Zeep library.  
So maybe this work can be a little usefull? I'm sorry if not.

## Why this package?

SOAP support in Python is weak.

Zeep as client: Has MTOM support for incomming message, lacks support for outgoing message.  
&nbsp;&nbsp;&nbsp;&nbsp;(see MessagePack object described here: https://docs.python-zeep.org/en/master/attachments.html)

Spyne as server: Has MTOM support for incomming message, lacks support for outgoing message.
&nbsp;&nbsp;&nbsp;&nbsp;(see spyne/protocol/soap/mime.py)

This package should create and parse the MTOM message.  
For parse we just proxy to Zeep's support, no idea if it works correctly.

## How to use this package

For **mtom_parse** this package uses internally Zeep library.  
That means that you can use their support directly.  
Not sure if their support run well or not.  
mtom_parse gives just different result structures - the values have fixed type,
	while in Zeep you will receive a plain xml or MultiPack.

For **mtom_create** we  
- take a xml message,
- add files as binary attachments,
- create a http header include mimetypes for each part,
- replaces text b"cid:{cid}" in a xml message for each attachment,
- return
	- the content of message
	- updating dict for wrapping http header

As an usage example we can take the usage from Zeep.  
mtom_create is here wrapped into Transport class **MTOMTransport** which will  
- take a message prepared for requests call
- modify it (see mtom_create above),
- update outer headers using update_headers obtained from mtom_create,
- call requests for POST

		files = ["tmp/black.png", "tmp/white.png"]
		transport = MTOMTransport()  # older style (files=files) you can still use here
		client = zeep.Client(
			"https://service.url",
			transport=transport,
		)
		params = {
			"fileName_1": "dark.png",
			"imageData_1": "cid:{cid}",  # will change to <xop:Include href="cid:1">
			"fileName_2": "light.png",
			"imageData_2": "cid:{cid}",  # will change to <xop:Include href="cid:2">
		}
		transport.add_files(files=files)
		client.service.upload(**params)

Usage from Django and Zeep:  
You can add a logger:  

	"zeep.transports": {
		"level": env("LOGLEVEL_SOAP_ZEEP", default="INFO"),  # DEBUG pro logování
		"handlers": ["console"],
		"propagate": True,
	},

and then you can call  

	LOGLEVEL_SOAP_ZEEP=DEBUG ./manage.py runserver
	LOGLEVEL_SOAP_ZEEP=DEBUG pytest -s -k mtom  # if you have test_mtom() which instantiate zeep.Client and call some its service

## Notes: How this package was created?

	# BASICS
	# outside of venv (which results to the debian system python as version in pyproject.toml) :
	pyenv 3.7.16  # lowest supported python version will be: 3.7
	poetry new pymtom
	cd pymtom/
	# not made, but probably would be good: touch poetry.toml , content:
	#	[virtualenvs]
	#	create = true
	#	in-project = true
	poetry shell
	pip install --upgrade pip setuptools
	touch README.md  # https://www.markdownguide.org/basic-syntax/
	touch .gitignore
	#	__pycache__/
	#	*.py[cod]
	#	.idea
	#	.vscode/
	#	.history/
	#	dist/
	touch pymtom/create.py
	touch pymtom/parse.py
	# add names which you want import easily into pymtom/__init__.py: from .pymtom.create import mtom_create, from .pymtom.parse import mtom_parse
	poetry build
	# install for package development from outside, via pip:
	pip install -e ../<path>/pymtom/ (revert via: pip uninstall pymtom)

	# GIT
	# empty repo pyutils/pymtom created; don't initialized with anything
	git init
	git add .
	git commit -m "initial commit"
	git branch -M main
	git remote add origin git@github-pyutil-account:pyutil/pymtom.git
	git config --local user.name "pyutil"
	git push -u origin main  # if `push` fails kill temporary the agent: eval $(ssh-agent -k)
	# so instead of github.com Host directly, we use the github-pyutil-account Host defned in ~/.ssh/config
	#   with `HostName github.com` and `IdentityFile ~/.ssh/id_ed25519_...` where corresponding public key (.pub) is uploaded to GitHub

	# PYPI
	# add into pyproject.toml [tool.poetry]: readme = "README.md"  # https://python-poetry.org/docs/pyproject/#readme
	# add token from your account on PyPI web: poetry config pypi-token.pypi pypi-xxxxxxxxxxxxxxxx
	# bump version? in pymtom/__init__.py & pyproject.toml
	# commit+push
	rm -rf dist/
	poetry build  # or together: poetry publish --build
	# zkontrolovat dist/
	# (pip install pkginfo:) pkginfo dist/pymtom... must have `description` and `description_content_type` (thx readme=..)
	poetry publish
	# [pypi.org/project/pymtom/](https://pypi.org/project/pymtom/)

## What is new?

### 0.3.0

Earlier versions in Zeep scenario were able to add files during instantiating of transport class only: `MTOMTransport(files=files)`.  
To repair this bad design decision you have now the method `.add_files()` of the transport class which you can use before each service call.  
Docs were updated.
