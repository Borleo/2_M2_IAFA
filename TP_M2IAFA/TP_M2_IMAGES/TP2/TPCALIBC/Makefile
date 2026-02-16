CC=gcc
CFLAGS=-Wall -Wextra -std=c11 -Wpedantic
LDFLAGS= $(CFLAGS)
LDLIBS=-lm
RM=rm -f

OBJECTS=limace.o salade.o erreurs.o calib.o

EXE=calib

.PHONY: all
all: $(EXE)

OBJ=limace.o salade.o erreurs.o
calib: $(OBJ) calib.o 

limace.o: limace.h
salade.o: limace.h salade.h
calib.o: limace.h salade.h erreurs.h

clean:
	$(RM) $(OBJECTS) $(EXE)
