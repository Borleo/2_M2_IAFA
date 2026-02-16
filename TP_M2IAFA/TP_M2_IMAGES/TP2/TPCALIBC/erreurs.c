#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "erreurs.h"

/*
 * Fonction a appeler en debut de main pour initialiser la gestion des erreurs 
 */
char *InitMesg(char *argv[])
{
  static char *Prog=NULL;
  
  if (Prog==NULL)
  {
    if ((Prog=strrchr(argv[0],'/')))
      Prog++;
    else
      Prog=argv[0];
  }
  return Prog;
}

/*
 * Affichage d'un message formate sur stderr
 */
void Mesg(const char *Msg, ...)
{
  va_list Params;

  va_start(Params, Msg);
  vfprintf(stderr, Msg, Params);
  va_end(Params);
}

/*
 * Affichage de la syntaxe d'appel du programme sur stderr
 */
void Usage(char *Syntaxe)
{
  char *Ligne, *Copie;

  Copie=malloc(strlen(Syntaxe)+1);
  strcpy(Copie,Syntaxe);
  Mesg("SYNTAXE\n");
  Ligne=strtok(Copie,"\n");
  while (Ligne!=NULL)
  {
    Mesg("\t%s %s\n",InitMesg(NULL),Ligne);
    Ligne=strtok(NULL,"\n");
  }
  free(Copie);
}

/*
 * Affichage d'un message d'erreur sur stderr
 */
void Erreur(char *Msg)
{
  Mesg("[%s] %s\n",InitMesg(NULL),Msg);
}
