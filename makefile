CC=g++
CFLAGS=-I.
DEPS = serialib.h
OBJ = main.o serialib.o 

%.o: %.c $(DEPS)
	$(CC) -c -o $@ $< $(CFLAGS)

hellomake: $(OBJ)
	$(CC) -o $@ $^ $(CFLAGS)
