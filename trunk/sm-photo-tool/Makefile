NAME		= sm-photo-tool
VERSION		= $(shell echo `grep "^version" src/sm_photo_tool.py | awk '{print $$3}' | sed 's/\"//g'`)
RELEASE		= 2

debug:
	-echo $(VERSION)
	-echo $(NAME)

clean:
	rm -rf rpm-build
	rm -rf dist

maketar:
	mkdir -p dist/$(NAME)-$(VERSION)/
	cp LICENSE.TXT dist/$(NAME)-$(VERSION)/
	cp src/sm_photo_tool.py dist/$(NAME)-$(VERSION)/
	cp src/smugmugrc dist/$(NAME)-$(VERSION)/
	cd dist/; tar czf $(NAME)-$(VERSION).tar.gz $(NAME)-$(VERSION)/
	rm -rf dist/$(NAME)-$(VERSION)/
	
release: clean maketar
	mkdir -p rpm-build
	cp dist/*.gz rpm-build/
	echo "$(VERSION) $(RELEASE)" > rpm-build/version
	rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define '_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
	--define "_specdir %{_topdir}" \
	--define "_sourcedir %{_topdir}" \
	-ba rpm/spec/sm-photo-tool.spec
