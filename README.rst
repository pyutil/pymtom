## Why this package?

SOAP support in Python is weak.
Zeep (Suds) for client: Has MTOM support for incomming message, lacks support for outgoing message.
	(see MessagePack object described here: https://docs.python-zeep.org/en/master/attachments.html)
Spyne as server: Has MTOM support for incomming message, lacks support for outgoing message.
	(see spyne/protocol/soap/mime.py)

This package should create and parse the MTOM message.
For parse we just proxy to Zeep's support.


## Notes: How this package was created?

```
# outside of venv (which results to the debian system python as version in pyproject.toml) :
pyenv 3.7.16  # lowest supported python version will be: 3.7
poetry new pymtom
cd pymtom/
poetry shell
touch pymtom/create.py
touch pymtom/parse.py
# add names which you want import easily into pymtom/__init__.py: from .pymtom.create import mtom_create, from .pymtom.parse import mtom_parse
poetry build
# install for package development via pip:
pip install -e ../<path>/pymtom/ (revert via: pip uninstall pymtom)

# empty repo pyutils/pymtom created; don't initialized with anything
git init
git add .
git commit -m "initial commit"
git remote add origin git@github.com:zvolsky/openstreetways_web.git  # ssh; v nouzi lze nahradit https
git push -u origin master

```

## Notes: How this package was uploaded to PyPI?
