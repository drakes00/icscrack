PRIVATE=private
PUBLIC=public
SPECS=specs

all: doxy pdflatex

.PHONY: doxy pdflatex

doxy:
	@doxygen Doxyfile
	@doxygen Doxyfile.public

pdflatex:
	cd $(PRIVATE)/latex && $(MAKE)
	cd $(PUBLIC)/latex && $(MAKE)
	cd $(SPECS)/latex && $(MAKE)
