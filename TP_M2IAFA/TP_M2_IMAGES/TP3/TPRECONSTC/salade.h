/* Copyright (C) 12/05/2000 A. Crouzil  Salade release 1.4 (14/12/2010) */
/* Debugging : G. Gales (14/12/2010)
 */
#ifndef __salade_h_
#define __salade_h_

#include "limace.h"

#ifdef __cplusplus
extern "C" {
#endif


/* Estimation aux moindres carres de la solution d'un systeme lineaire
 * surdetermine du type Ax=b par la methode de la pseudo-inverse
 * Retourne le vecteur colonne estime ou NULL si le systeme est singulier.
 */
extern Matrix SystResol(
                         Matrix MA, /* matrice des coefficients */
                         Matrix Mb  /* vecteur colonne des constantes */
                       );


#define NULL_MATRIX 1
#define MATRIX_NOT_SQUARE 2
#define MATRIX_NOT_SYMMETRIC 3

/* Calcul des valeurs et vecteurs propres d'une matrice symetrique
 * pVal : adresse de la matrice (vecteur colonne) qui contiendra les
 *        valeurs propres ;
 * pVec : adresse de la matrice qui contiendra les vecteurs propres
 *        correspondants, un vecteur par colonne.
 * L'allocation de ces deux matrices est faite dans SymEig.
 * La liberation est donc a la charge de l'appelant.
 *
 * Retourne 0 si tout s'est bien passe, un code d'erreur sinon :
 *    NULL_MATRIX si la matrice est vide ;
 *    MATRIX_NOT_SQUARE si la matrice n'est pas carree ;
 *    MATRIX_NOT_SYMMETRIC si la matrice n'est pas symetrique.
 */
extern int SymEig(
		  Matrix Mat,  /* matrice symatrique */
		  Matrix *pVal,/* adresse de la matrice des valeurs propres */
                  Matrix *pVec /* adresse de la matrice des vecteurs propres */
                 );




#ifdef __cplusplus
}
#endif


#endif /* !__salade_h_ */
