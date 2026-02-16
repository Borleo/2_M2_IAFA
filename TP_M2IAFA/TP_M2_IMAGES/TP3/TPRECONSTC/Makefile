CC=gcc
CFLAGS=-Wall -Wextra -std=c11 -Wpedantic -g
LDFLAGS= $(CFLAGS)
LDLIBS=-lm
RM=rm -f

OBJECTS=limace.o salade.o erreurs.o reconst.o erreur.o

EXE=reconst erreur

.PHONY: all
all: $(EXE)

OBJ1=limace.o erreurs.o
OBJ2=$(OBJ1) salade.o
reconst: $(OBJ2) reconst.o 
erreur: $(OBJ1) erreur.o 

limace.o: limace.h
salade.o: limace.h salade.h
reconst.o: limace.h salade.h erreurs.h
erreur.o: limace.h erreurs.h

clean:
	$(RM) $(OBJECTS) $(EXE)
