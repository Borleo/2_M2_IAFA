#ifndef __erreurs_h_
#define __erreurs_h_

#include <stddef.h>
#include <stdarg.h>

#ifdef __cplusplus
extern "C" {
#endif

/* Fonction a appeler en debut de main pour initialiser la gestion des erreurs */
extern char *InitMesg(char *argv[]);

/* Affichage d'un message formate sur stderr */
extern void Mesg(const char *Msg, ...);

/* Affichage de la syntaxe d'appel d'un operateur sur stderr */
extern void Usage(char *Syntaxe);

/* Affichage d'un message d'erreur sur stderr */
extern void Erreur(char *Msg);

#define DEBOGAGE
#ifdef DEBOGAGE
#define DEBUG fprintf(stderr,"Fichier %s, ligne %d\n",__FILE__,__LINE__);
#else
#define DEBUG
#endif

#ifdef __cplusplus
}
#endif


#endif /* !__erreurs_h_ */
