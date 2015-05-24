# This program is free software; you can redistribute it and/or modify
# it under the terms of the (LGPL) GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the 
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library Lesser General Public License for more details at
# ( http://www.gnu.org/licenses/lgpl.html ).
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# written by: Jeff Ortel ( jortel@redhat.com )
#

PKG = python-suds
SPEC = $(PKG).spec
SETUP = setup.py
DOCTAR = suds-docs.tar.gz
FEDORAPEOPLE = jortel@fedorapeople.org

all : rpm docs

dist : clean
	mkdir dist
	./sdist
	./sdist python

rpm : dist
	cp dist/$(PKG)*.gz /usr/src/redhat/SOURCES
	rpmbuild -ba $(SPEC)
	cp /usr/src/redhat/RPMS/noarch/$(PKG)*.rpm dist
	cp /usr/src/redhat/SRPMS/$(PKG)*.rpm dist
	rpmlint -i dist/$(PKG)*.rpm

release : rpm rdocs
	scp dist/python*.tar.gz fedorahosted.org:suds
	scp dist/python*.rpm fedorahosted.org:suds

register :
	python setup.py sdist bdist_egg register upload

rdocs : docs
	scp /tmp/$(DOCTAR) $(FEDORAPEOPLE):
	ssh $(FEDORAPEOPLE) 'cd public_html/suds; rm -rf doc; tar xmzvf ~/$(DOCTAR)'

docs :
	rm -rf doc
	rm -f /tmp/$(DOCTAR)
	epydoc -vo doc `find suds -name "*.py"`
	tar czvf /tmp/$(DOCTAR) doc

pdf :
	epydoc -vo doc --pdf `find suds -name \*.py`
	mv doc/api.pdf doc/sudsapi.pdf

clean :
	rm -rf dist
	rm -rf build
	rm -rf doc
	rm -rf *.egg-info
	rm -rf /usr/src/redhat/BUILD/$(PKG)*
	rm -rf /usr/src/redhat/RPMS/noarch/$(PKG)*
	rm -rf /usr/src/redhat/SOURCES/$(PKG)*
	rm -rf /usr/src/redhat/SRPMS/$(PKG)*
	find . -name "*.pyc" -exec rm -f {} \;
	find . -name "*~" -exec rm -f {} \;

.PHONY : clean register docs pdf
