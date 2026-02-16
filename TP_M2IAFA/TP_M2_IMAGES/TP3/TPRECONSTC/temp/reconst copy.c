#include <stdio.h>
#include <string.h>
#include <math.h>
#include "limace.h"
#include "salade.h"
#include "erreurs.h"

/* Codes de retour */
#define OK                 0
#define HELP               1
#define ERR_NB_PARAM       2
#define ERR_MAT_P_G        3
#define ERR_MAT_P_G_TYPE   4
#define ERR_MAT_P_G_SIZE   5
#define ERR_MAT_P_D        6
#define ERR_MAT_P_D_TYPE   7
#define ERR_MAT_P_D_SIZE   8
#define ERR_MAT_2D_G       9
#define ERR_MAT_2D_G_TYPE 10
#define ERR_MAT_2D_G_SIZE 11
#define ERR_MAT_2D_D      12
#define ERR_MAT_2D_D_TYPE 13
#define ERR_MAT_2D_D_SIZE 14
#define ERR_MAT_2D_SIZE   15
#define ERR_MAT_OUT       16

/* Affichage de la syntaxe d'appel du programme */
void Syntaxe(void)
{
  Usage("Pg.mx Pd.mx p2g.mx p2d.mx p3.mx\n"
        "-h\n");
}

/* Affichage de la description du programme */
void Description(void)
{
  Mesg("ROLE\n");
  Mesg("\tReconstruction 3D par triangulation\n");
  Mesg("ARGUMENTS\n");
  Mesg("\tPg.mx : Matrice 3 x 4 (format Matrix) de projection perspective gauche\n");
  Mesg("\tPd.mx : Matrice 3 x 4 (format Matrix) de projection perspective droite\n");
  Mesg("\tp2g.mx : Matrice n x 2 (format Matrix) des coordonnées des points à gauche\n");
  Mesg("\tp2d.mx : Matrice n x 2 (format Matrix) des coordonnées des correspondants à droite\n");
  Mesg("\tp3.mx : nom du fichier destination qui va contenir la matrice n x 3 (format Matrix) des coordonnées des points reconstruits\n");
  Mesg("OPTION\n");
  Mesg("\t-h : affichage de l'aide\n");
  Mesg("DIAGNOSTIC (codes de retour)\n");
  Mesg("\t 0 : opération réalisée sans problème\n");
  Mesg("\t 1 : aide demandée\n");
  Mesg("\t 2 : mauvais nombre de paramètres\n");
  Mesg("\t 3 : problème d'ouverture du fichier de la matrice de projection perspective gauche\n");
  Mesg("\t 4 : type de la matrice de projection perspective gauche incorrect (Double attendu)\n");
  Mesg("\t 5 : taille de la matrice de projection perspective gauche incorrecte (3 x 4 attendue)\n");
  Mesg("\t 6 : problème d'ouverture du fichier de la matrice de projection perspective droite\n");
  Mesg("\t 7 : type de la matrice de projection perspective droite incorrect (Double attendu)\n");
  Mesg("\t 8 : taille de la matrice de projection perspective droite incorrecte (3 x 4 attendue)\n");
  Mesg("\t 9 : problème d'ouverture du fichier des coordonnées 2D gauche \n");
  Mesg("\t10 : type de la matrice 2D gauche incorrect (Double attendu)\n");
  Mesg("\t11 : taille de la matrice 2D gauche incorrecte (2 colonnes attendues)\n");
  Mesg("\t12 : problème d'ouverture du fichier des coordonnées 2D droite \n");
  Mesg("\t13 : type de matrice 2D droite incorrect (Double attendu)\n");
  Mesg("\t14 : taille de la matrice 2D droite incorrecte (2 colonnes attendues)\n");
  Mesg("\t15 : les deux matrices 2D n'ont pas le même nombre de lignes\n");
  Mesg("\t16 : problème lors du calcul de la matrice des coordonnées des points 3D reconstruits\n");
}

/*
 * Produit de deux matrices de type Double
 * Entrées :
 *    - MA : première matrice
 *    - MB : seconde matrice
 * Valeur de retour : nouvelle matrice résultat du produit de MA par MB 
 *                    ou NULL en cas de problème
 */
Matrix Mult(Matrix MA, Matrix MB)
{
  int la=MatNbRow(MA);
  int ca=MatNbCol(MA);
  int lb=MatNbRow(MB);
  int cb=MatNbCol(MB);
  if (ca!=lb)
  {
    Erreur("Mult : tailles des matrices incompatibles");
    return NULL;
  }
  Matrix MC=MatAlloc(Double,la,cb);
  if (MC==NULL)
  {
    Erreur("Mult : problème d'allocation mémoire");
    return NULL;
  }
  double **A=MatGetDouble(MA);
  double **B=MatGetDouble(MB);
  double **C=MatGetDouble(MC);

  for (int i=0;i<la;i++)
    for (int j=0;j<cb;j++)
    {
      C[i][j]=0.0;
      for (int k=0;k<ca;k++)
        C[i][j]+=A[i][k]*B[k][j];
    }

  return MC;
}

/* Transposition d'une matrice de type Double
 * Entrée :
 *    - Mat : matrice de type Double à transposer
 * Valeur de retour : nouvelle matrice transposée de Mat ou NULL en cas
 *                    de problème
 */
Matrix Transp(Matrix Mat)
{
  int l=MatNbRow(Mat);
  int c=MatNbCol(Mat);
  Matrix Res=MatAlloc(Double,c,l);
  if (Res==NULL)
  {
    Erreur("Transp : problème d'allocation memoire");
    return NULL;
  }
  double **M=MatGetDouble(Mat);
  double **R=MatGetDouble(Res);
  for (int i=0;i<c;i++)
    for (int j=0;j<l;j++)
      R[i][j]=M[j][i];
  return Res;
}

/* Indice de la ligne du plus petit élément de la première colonne d'une matrice
 * de type Double
 * Entrée :
 *    - Mat : matrice de type Double
 * Valeur de retour : indice de la ligne du plus petit élément de la première
 *                    colonne de Mat
 */
int IndMin(Matrix Mat)
{
  int n=MatNbRow(Mat);
  double **M=MatGetDouble(Mat);
  int IndM=0;
  double Min=M[0][0];
  for (int i=0; i<n; i++)
    if (M[i][0]<Min)
    {
      Min=M[i][0];
      IndM=i;
    }
  return IndM;
}

/*

Stéréovision binoculaire : reconstruction 3D par triangulation : 

- estimation au sens des moindres carrés totaux des coordonnées 3D  
- des points reconstruits à partir de correspondances 2D <--> 2D et 
- des matrices de projection perspective des deux caméras.

Entrées :

- MatPg  : matrice de projection perspective de la caméra gauche de type Double de taille 3 x 4 
- MatPd  : matrice de projection perspective de la caméra droite de type Double de taille 3 x 4 
- Matp2g : matrice de type Double de taille n x 2 des coordonnées des projections sur l'image gauche
- Matp2d : matrice de type Double de taille n x 2 des coordonnées des projections correspondantes sur l'image droite
   
Valeur de retour : matrice de type Double de taille n x 3 des coordonnées 3D des points reconstruits

1°) construction de la matrice des coefficients A ;     
2°) calcul de la matrice A⊤A ;
3°) calcul des valeurs et vecteurs propres de cette matrice ;
4°) détermination du vecteur propre correspondant à la plus petite valeur propre;
5°) calcul des coordonnées estimées (X , Y , Z) du point reconstruit.  

*/

Matrix Reconstruction(Matrix _MatPg, Matrix _MatPd, Matrix _Matp2g, Matrix _Matp2d)
{
  // _MatPg  = 3 x 4,  _MatPd  = 3 x 4
  // _Matp2g = 40 x 2, _Matp2d = 40 x 2 

  Verbose();

  int n_pg       = MatNbRow(_MatPg);
  int m_pg       = MatNbCol(_MatPg);
  double **MatPg = MatGetDouble(_MatPg);

  printf("\n MatPg nombre ligne %d, colonne : %d\n",n_pg,m_pg);

  int n_p2g       = MatNbRow(_Matp2g);
  int m_p2g       = MatNbCol(_Matp2g);
  double **Matp2g = MatGetDouble(_Matp2g);

  printf("\n Matp2g nombre ligne %d, colonne : %d\n",n_p2g,m_p2g);

  //-----------------------------------------------------------------//

  int n_pd       = MatNbRow(_MatPd);
  int m_pd       = MatNbCol(_MatPd);
  double **MatPd = MatGetDouble(_MatPd);

  printf("\n MatPd nombre ligne %d, colonne : %d\n",n_pd,m_pd);

  int n_p2d       = MatNbRow(_Matp2d);
  int m_p2d       = MatNbCol(_Matp2d);
  double **Matp2d = MatGetDouble(_Matp2d);

  printf("\n Matp2d nombre ligne %d, colonne : %d\n",n_p2d,m_p2d);

/*-----------------------------------------------------------------
  1°) construction de la matrice des coefficients A; 
      _MatPg  = 3 x 4,  _MatPd  = 3 x 4
      _Matp2g = 40 x 2, _Matp2d = 40 x 2 
------------------------------------------------------------------*/

  Matrix _A      = MatAlloc(Double,4*n_p2d,3);
  if (_A==NULL)
  {
    Erreur("Mult : problème d'allocation mémoire");
    return NULL;
  }

  double **A    = MatGetDouble(_A);
  int n_pA      = MatNbRow(_A);
  int m_pA      = MatNbCol(_A);
  
  printf("\n\nA nombre ligne %d, colonne : %d\n",n_pA,m_pA);  

  Matrix _B     = MatAlloc(Double,4*n_p2d,1);
  if (_B==NULL)
  {
    Erreur("Mult : problème d'allocation mémoire");
    return NULL;
  }

  double **B    = MatGetDouble(_B);
  int n_pB      = MatNbRow(_B);
  int m_pB      = MatNbCol(_B);

  printf("\n\nB nombre ligne %d, colonne : %d\n",n_pB,m_pB);  

  for ( int i=0 , j=0 ; i < n_p2d ; i+=1, j+=4 )
   { 
    A[j][0] = MatPg[0][0]  - (Matp2g[i][0] * MatPg[2][0]);
    A[j][1] = MatPg[0][1]  - (Matp2g[i][0] * MatPg[2][1]);
    A[j][2] = MatPg[0][2]  - (Matp2g[i][0] * MatPg[2][2]);
    B[j][0] =(Matp2g[i][0] *  MatPg[2][3]) - MatPg[0][3];

    A[j+1][0] = MatPg[1][0]  - (Matp2g[i][1] * MatPg[2][0]);
    A[j+1][1] = MatPg[1][1]  - (Matp2g[i][1] * MatPg[2][1]);
    A[j+1][2] = MatPg[1][2]  - (Matp2g[i][1] * MatPg[2][2]);
    B[j+1][0] =(Matp2g[i][1] *  MatPg[2][3]) - MatPg[1][3];   

    A[j+2][0] = MatPd[0][0]  - (Matp2d[i][0] * MatPd[2][0]);
    A[j+2][1] = MatPd[0][1]  - (Matp2d[i][0] * MatPd[2][1]);
    A[j+2][2] = MatPd[0][2]  - (Matp2d[i][0] * MatPd[2][2]);
    B[j+2][0] =(Matp2d[i][0] *  MatPd[2][3]) - MatPd[0][3]; 

    A[j+3][0] = MatPd[1][0] - (Matp2d[i][1] * MatPd[2][0]);
    A[j+3][1] = MatPd[1][1] - (Matp2d[i][1] * MatPd[2][1]);
    A[j+3][2] = MatPd[1][2] - (Matp2d[i][1] * MatPd[2][2]);
    B[j+3][0] =(Matp2d[i][1] * MatPd[2][3]) - MatPd[1][3];  
   }

MatWriteAsc(_A, "");  
printf("\n\n---------------------------");  
MatWriteAsc(_B, "");  

/*
 calcul de la matrice ATA;
*/
  Matrix AT    = Transp(_A);
  int n_pAT    = MatNbRow(AT);
  MatWriteAsc(AT, "");

  Matrix _ATA   = MatAlloc(Double,n_pAT,m_pA);

   _ATA         = Mult(AT,_A);
  int n_ATA    = MatNbRow(_ATA);
  int m_ATA    = MatNbCol(_ATA);

  printf("\n\n ligne 283 - AT*A nombre ligne %d, colonne : %d\n",n_ATA,m_ATA);
  MatWriteAsc(_ATA, "");
  
  /* 
   Calcul des valeurs et vecteurs propres de cette matrice.
   Calcul des valeurs et vecteurs propres d'une matrice symetrique
   pVal : adresse de la matrice (vecteur colonne) qui contiendra les valeurs propres ;
   pVec : adresse de la matrice qui contiendra les vecteurs propres correspondants, un vecteur par colonne.
  */

  Matrix pVal;
  Matrix pVec;

  printf("\n\nLigne 296 - Identification du vecteur propre unitaire associé à la plus petite valeur propre de ATA");
  
  int res_sigEig = 0;
  res_sigEig =  SymEig(_ATA, &pVal, &pVec);
  if (res_sigEig != 0) 
    {
      printf("Ligne 284 - SymEig result %d\n",res_sigEig);
      return NULL;
    }
   
  printf("\n\n Ligne 306 - pVec contient les vecteurs propres du système ATA\n");
  MatWriteAsc(pVec, "");  

 /*
  Détermination du vecteur propre correspondant à la plus petite valeur propre;
  */

  double *p_Val = *MatGetDouble(pVal);
  int n_ppepc = IndMin(pVal);

  printf("\n\n Ligne 316 - pVal contient les valeurs propres du système de ATA\n");
  MatWriteAsc(pVal, "");
  printf("\nLigne 301 - l'Indice %d de la plus petite valeur % .16e des valeurs propres\n",n_ppepc, p_Val[n_ppepc]);


  int n_pVec = MatNbRow(pVec);
  int m_pVec = MatNbCol(pVec);

  printf("\n\n ligne 324 - pVec nombre ligne %d, colonne : %d\n",n_pVec,m_pVec);

  Matrix _ppVec = MatAlloc(Double,n_pVec,m_pVec); 
  double **p_ppVec = MatGetDouble(_ppVec);
  double **p_Vec = MatGetDouble(pVec);

  double lstpVecVal = 0.0; 
 
  for ( int i = 0 ; i < n_pVec ; i++ )
    for ( int j = 0, k = 0; j < m_pVec ; j++)
    {
      p_ppVec[i][j] = p_Vec[k][n_ppepc];
      lstpVecVal    = p_Vec[k][n_ppepc];
      k+=1;

    }
  
  printf("\nLigne 335 - % .16e est la dernière valeur vecteur propre unitaire\n",lstpVecVal);    
  printf("\nLigne 336 - L’estimée Pb de la matrice de projection perspective avant normalisation vaut\n"); 
  MatWriteAsc(_ppVec, ""); 

  return NULL;

}

/* Fonction principale */
int main(int argc, char *argv[])
{
  // Initialisation du mécanisme d'affichage des messages
  InitMesg(argv);
  // Vérification du nombre de paramètres
  if (argc!=2 && argc!=6)
  {
	Syntaxe();
	return ERR_NB_PARAM;
  }
  if (argc==2)
  {
    if (!strcmp(argv[1],"-h"))
	{
	  Syntaxe();
	  Description();
	  return HELP;
	}
	else // un seul paramètre différent de -h
	{
	  Syntaxe();
	  return ERR_NB_PARAM;
	}
  }
  // Lecture des matrices
  Matrix MatPg=MatReadAsc(argv[1]);
  if (MatPg==NULL)
  {
    Erreur("Problème lors de la lecture de la matrice de projection perspective gauche");
	return ERR_MAT_P_G;
  }
  if (MatType(MatPg)!=Double)
  {
    Erreur("La matrice de projection perspective gauche doit être Double");
	MatFree(&MatPg);
	return ERR_MAT_P_G_TYPE;
  }
  if (MatNbRow(MatPg)!=3 || MatNbCol(MatPg)!=4)
  {
    Erreur("La matrice de projection perspective gauche doit être de taille 3 x 4");
	MatFree(&MatPg);
	return ERR_MAT_P_G_SIZE;
  }
  Matrix MatPd=MatReadAsc(argv[2]);
  if (MatPd==NULL)
  {
    Erreur("Problème lors de la lecture de la matrice de projection perspective droite");
	MatFree(&MatPg);
	return ERR_MAT_P_D;
  }
  if (MatType(MatPd)!=Double)
  {
    Erreur("La matrice de projection perspective droite doit être Double");
	MatFree(&MatPg);
	MatFree(&MatPd);
	return ERR_MAT_P_D_TYPE;
  }
  if (MatNbRow(MatPd)!=3 || MatNbCol(MatPd)!=4)
  {
    Erreur("La matrice de projection perspective droite doit être de taille 3 x 4");
	MatFree(&MatPg);
	MatFree(&MatPd);
	return ERR_MAT_P_D_SIZE;
  }
  Matrix Matp2g=MatReadAsc(argv[3]);
  if (Matp2g==NULL)
  {
    Erreur("Problème lors de la lecture de la matrice des coordonnées 2D gauche");
	MatFree(&MatPg);
	MatFree(&MatPd);
	return ERR_MAT_2D_G;
  }
  if (MatType(Matp2g)!=Double)
  {
    Erreur("La matrice des coordonnées 2D gauche doit être Double");
	MatFree(&MatPg);
	MatFree(&MatPd);
	MatFree(&Matp2g);
	return ERR_MAT_2D_G_TYPE;
  }
  if (MatNbCol(Matp2g)!=2)
  {
    Erreur("La matrice des coordonnées 2D gauche doit avoir 2 colonnes");
	MatFree(&MatPg);
	MatFree(&MatPd);
	MatFree(&Matp2g);
	return ERR_MAT_2D_G_SIZE;
  }
  Matrix Matp2d=MatReadAsc(argv[4]);
  if (Matp2d==NULL)
  {
    Erreur("Problème lors de la lecture de la matrice des coordonnées 2D droite");
	MatFree(&MatPg);
	MatFree(&MatPd);
	MatFree(&Matp2g);
	return ERR_MAT_2D_D;
  }
  if (MatType(Matp2d)!=Double)
  {
    Erreur("La matrice des coordonnées 2D droite doit être Double");
	MatFree(&MatPg);
	MatFree(&MatPd);
	MatFree(&Matp2g);
	MatFree(&Matp2d);
	return ERR_MAT_2D_D_TYPE;
  }
  if (MatNbCol(Matp2d)!=2)
  {
    Erreur("La matrice des coordonnées 2D droite doit avoir 2 colonnes");
	MatFree(&MatPg);
	MatFree(&MatPd);
	MatFree(&Matp2g);
	MatFree(&Matp2d);
	return ERR_MAT_2D_D_SIZE;
  }
  if (MatNbRow(Matp2g)!=MatNbRow(Matp2d))
  {
    Erreur("Les deux matrices de coordonnées 2D doivent avoir le même nombre de lignes");
	MatFree(&MatPg);
	MatFree(&MatPd);
	MatFree(&Matp2g);
	MatFree(&Matp2d);
	return ERR_MAT_2D_SIZE;
  }
  // Reconstruction 3D par triangulation
  Matrix Matp3d=Reconstruction(MatPg,MatPd,Matp2g,Matp2d);
  MatFree(&MatPg);
  MatFree(&MatPd);
  MatFree(&Matp2g);
  MatFree(&Matp2d);
  if (Matp3d==NULL)
  {
    Erreur("Problème lors de la triangulation des points");
	return ERR_MAT_OUT;
  }
  // Écriture de la matrice résultat
  MatWriteAsc(Matp3d,argv[5]);
  // Libération de la matrice résultat 
  MatFree(&Matp3d);

  return OK;
}
