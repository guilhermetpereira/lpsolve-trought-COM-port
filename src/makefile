IDIR = ../inc
CC=g++
CFLAGS=-I$(IDIR)

ODIR=obj
LDIR =../lib

LIBS=-lm


_DEPS = serialib.h
DEPS = $(patsubst %,$(IDIR)/%,$(_DEPS))

_OBJ = main.o serialib.o 
OBJ = $(patsubst %,$(ODIR)/%,$(_OBJ))

OBJ = main.o serialib.o 

$(ODIR)/%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

main: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS) $(LIBS)

.PHONY: clean

clean:
	rm -f $(ODIR)/*.o *~ core $(INCDIR)/*~ 