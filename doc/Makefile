LATEXFLAGS=\
	-interaction=nonstopmode \
	-halt-on-error \
	-file-line-error \
	-output-directory=pdf

IMG_TEXS=$(wildcard *-img.tex)
IMG_PDFS=$(patsubst %-img.tex,pdf/%-img.pdf,$(IMG_TEXS))
IMGS=$(patsubst pdf/%-img.pdf,img/%.png,$(IMG_PDFS))

.PHONY = all clean-builds clean


all: pdf/document.pdf $(IMGS) $(IMG_PDFS)
	

pdf/document.pdf: document.tex $(wildcard *.tex)
	pdflatex $(LATEXFLAGS) $<
	while grep "Rerun to get cross-references right" \
		  $(patsubst %.tex,pdf/%.log,$<); \
		do pdflatex $(LATEXFLAGS) $<; \
	done

pdf/%-img.pdf: %-img.tex %.tex pdf_template.tex
	pdflatex $(LATEXFLAGS) $<

img/%.png: pdf/%-img.pdf
	pdftoppm -png -singlefile $< $(patsubst %.png,%,$@)

clean-builds:
	rm -f pdf/*.aux
	rm -f pdf/*.log

clean:
	rm -f pdf/*.pdf
	rm -f pdf/*.aux
	rm -f pdf/*.log
	rm -f img/*.png
