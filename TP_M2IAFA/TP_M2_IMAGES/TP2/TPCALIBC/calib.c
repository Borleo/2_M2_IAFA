#include <stdio.h>
#include <string.h>
#include <math.h>
#include "limace.h"
#include "salade.h"
#include "erreurs.h"

/* Codes de retour */
#define OK              0
#define HELP            1
#define ERR_NB_PARAM    2
#define ERR_MAT_3D      3
#define ERR_MAT_3D_TYPE 4
#define ERR_MAT_3D_SIZE 5
#define ERR_MAT_2D      6
#define ERR_MAT_2D_TYPE 7
#define ERR_MAT_2D_SIZE 8
#define ERR_MAT_SIZE    9
#define ERR_MAT_OUT    10

/* Affichage de la syntaxe d'appel du programme */
void Syntaxe(void)
{
  Usage("p3d.mx p2d.mx mpp.mx\n"
        "-h\n");
}

/* Affichage de la description du programme */
void Description(void)
{
  Mesg("ROLE\n");
  Mesg("\tCalibrage 3D d'une caméra\n");
  Mesg("ARGUMENTS\n");
  Mesg("\tp3d.mx : Matrice n x 3 (format Matrix) des coordonnées des points de la mire\n");
  Mesg("\tp2d.mx : Matrice n x 2 (format Matrix) des coordonnées des projections dans l'image des points de la mire\n");
  Mesg("\tmpp.mx : nom du fichier destination qui va contenir la matrice 3 x 4 (format Matrix) de projection perspective\n");
  Mesg("OPTION\n");
  Mesg("\t-h : affichage de l'aide\n");
  Mesg("DIAGNOSTIC (codes de retour)\n");
  Mesg("\t 0 : opération réalisée sans problème\n");
  Mesg("\t 1 : aide demandée\n");
  Mesg("\t 2 : mauvais nombre de paramètres\n");
  Mesg("\t 3 : problème d'ouverture du fichier des coordonnées 3D\n");
  Mesg("\t 4 : type de matrice 3D incorrect (Double attendu)\n");
  Mesg("\t 5 : taille de la matrice 3D incorrecte (3 colonnes attendues)\n");
  Mesg("\t 6 : problème d'ouverture du fichier des coordonnées 2D\n");
  Mesg("\t 7 : type de matrice 2D incorrect (Double attendu)\n");
  Mesg("\t 8 : taille de la matrice 2D incorrecte (2 colonnes attendues)\n");
  Mesg("\t 9 : les deux matrices doivent avoir le même nombre de lignes\n");
  Mesg("\t10 : problème lors du calcul de la matrice de projection perspective\n");
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

/* Calibrage 3D : estimation au sens des moindres carrés totaux de la matrice
   de projection perspective à partir de correspondances 3D <--> 2D
   Entrées :
      - MatP3 : matrice de type Double de taille n x 3 des coordonnées des 
                n points de référence de la mire
      - Matp2 : matrice de type Double de taille n x 2 des coordonnées des
                projections sur l'image des n points de référence de la mire
   Valeur de retour : matrice de projection perspective de la caméra de type
                      Double et de taille 3 x 4

   Matrice de projection
   La relation entre un point 3D et son image 2D peut être exprimée
   à l'aide d'une matrice de projection 3x4, notée M, qui combine 
   les paramètres intrinsèques et extrinsèques de la caméra2:
    
    M = K ⋅ T
  Où :
       K est la matrice des paramètres intrinsèques (3x3)
       T est la matrice des paramètres extrinsèques (3x4)

   Application de la transformation
   Pour transformer un point P_world du repère monde en un point P_camera dans le repère caméra, 
   on utilise la multiplication matricielle suivante : 
   
    - P_camera = M_world->camera * P_world Où 
    - P_world et P_camera sont exprimés en coordonnées homogènes (vecteurs 4x1).
    - [x,y,z,1] = [[r11,r12,r13,tx],[r21,r22,r23,ty],[r31,r32,r33,tz],[0,0,0,1]] * [X,Y,Z,1]
    - Paramètres de la matrice extrinsèque 
      - [[r11,r12,r13,tx],[r21,r22,r23,ty],[r31,r32,r33,tz],[0,0,0,1]]
      - Ils définissent la position et l'orientation de la caméra dans l'espace 3D.

*/ 
Matrix Calibrage(Matrix _MatP3, Matrix _Matp2)
{
  Verbose();
  int res_sigEig = 0;

  int n_p3       = MatNbRow(_MatP3);
  int m_p3       = MatNbCol(_MatP3);
  double **MatP3 = MatGetDouble(_MatP3);

  printf("\nMatp3 nombre ligne %d, colonne : %d\n",n_p3,m_p3);

  int n_p2       = MatNbRow(_Matp2);
  int m_p2       = MatNbCol(_Matp2);
  double **Matp2 = MatGetDouble(_Matp2);

  printf("Matp2 nombre ligne %d, colonne : %d\n\n",n_p2,m_p2);

  Matrix _A      = MatAlloc(Double,2*n_p2,12);
  if (_A==NULL)
  {
    Erreur("Mult : problème d'allocation mémoire");
    return NULL;
  }
/* 
1°) construction de la matrice des coefficients A; 
*/
  double **A    = MatGetDouble(_A);
  int n_pA      = MatNbRow(_A);
  int m_pA      = MatNbCol(_A);

  printf("\n\nA nombre ligne %d, colonne : %d\n",n_pA,m_pA);  

  for ( int i = 0, j = 0 ; i < 2*n_p2 ; i+=2  )
   { 
    A[i][0] = MatP3[j][0];
    A[i][1] = MatP3[j][1];
    A[i][2] = MatP3[j][2];
    A[i][3] = 1;
    A[i][4] = 0;
    A[i][5] = 0;
    A[i][6] = 0;
    A[i][7] = 0;

    A[i][8] =  -Matp2[j][0]*MatP3[j][0];
    A[i][9] =  -Matp2[j][0]*MatP3[j][1];
    A[i][10] = -Matp2[j][0]*MatP3[j][2];
    A[i][11] = -Matp2[j][0];

    A[i+1][0] = 0;
    A[i+1][1] = 0;
    A[i+1][2] = 0;
    A[i+1][3] = 0;
    A[i+1][4] = MatP3[j][0];
    A[i+1][5] = MatP3[j][1];
    A[i+1][6] = MatP3[j][2];
    A[i+1][7] = 1;

    A[i+1][8]  = -Matp2[j][1]*MatP3[j][0];
    A[i+1][9]  = -Matp2[j][1]*MatP3[j][1];
    A[i+1][10] = -Matp2[j][1]*MatP3[j][2];
    A[i+1][11] = -Matp2[j][1];
    j+=1;  
   }
MatWriteAsc(_A, "");  

/*
 calcul de la matrice ATA;
*/
  Matrix AT    = Transp(_A);
  int n_pAT    = MatNbRow(AT);
  MatWriteAsc(AT, "");

  Matrix _ATA   = MatAlloc(Double,n_pAT,m_pA);
 /*
  Quand m > n  on dit que le système est sur contraint car le 
  nombre d'équation Y est spérieur aux nombre de variales X,
  *********************************************************************
  dans le cas d'un modèle Y = AX il n'existe pas de solution X = A^1 Y.
  *********************************************************************
  Pour résoudre ce système on passe par les moindres carrés on cherche 
  *********************************************************************
  une approximation de x qui soit la plus petite possible. 
  *******************************
  telle que l'erreur e = Y - AX.
  *******************************
  On définit une fonction coût telle que J = ||e||^2 = e^T*e.
  *********************************************************************************
  La solution des moindres carrés es X^= argmin J, tel que X^=(A^T*A)^-1 * A^T * Y.
  ********************************************************************************** 
  _ATA répresent notre fonction coût J qui réprésente une mtrice carrés symétrique.
 */

  _ATA         = Mult(AT,_A);
  int n_ATA    = MatNbRow(_ATA);
  int m_ATA    = MatNbCol(_ATA);

  printf("\n\n ligne 267 - AT*A nombre ligne %d, colonne : %d\n",n_ATA,m_ATA);
  MatWriteAsc(_ATA, "");
  
  /* 
   Calcul des valeurs et vecteurs propres de cette matrice.
   Calcul des valeurs et vecteurs propres d'une matrice symetrique
   pVal : adresse de la matrice (vecteur colonne) qui contiendra les valeurs propres ;
   pVec : adresse de la matrice qui contiendra les vecteurs propres correspondants, un vecteur par colonne.
  */

  Matrix pVal;
  Matrix pVec;

  printf("Ligne 280 - Vecteur propre unitaire associé à la plus petite valeur propre de ATA");
  res_sigEig =  SymEig(_ATA, &pVal, &pVec);
  if (res_sigEig != 0) 
    {
      printf("Ligne 284 - SymEig result %d\n",res_sigEig);
      return NULL;
    }
   
  printf("\n\n Ligne 288 - pVec contient les vecteurs propres du système ATA\n");
  MatWriteAsc(pVec, "");  

  /*
  Détermination du vecteur propre correspondant à la plus petite valeur propre;
  */

  double *p_Val = *MatGetDouble(pVal);
  int n_ppepc = IndMin(pVal);

  printf("\n\n Ligne 297 - pVal contient les valeurs propres du système de ATA\n");
  MatWriteAsc(pVal, "");
  printf("\nLigne 301 - l'Indice %d de la plus petite valeur % .16e des valeurs propres\n",n_ppepc, p_Val[n_ppepc]);

  Matrix _ppVec = MatAlloc(Double,3,4); 
  double **p_ppVec = MatGetDouble(_ppVec);
  double **p_Vec = MatGetDouble(pVec);

  double lstpVecVal = 0.0; 
 
  for ( int i = 0, k = 0  ; i < 3 ; i++ )
    for ( int j = 0; j < 4 ; j++)
    {
      p_ppVec[i][j] = p_Vec[k][n_ppepc];
      lstpVecVal    = p_Vec[k][n_ppepc];
      k+=1;

    }
  
  printf("\nLigne 313 - % .16e est la dernière valeur vecteur propre unitaire\n",lstpVecVal);    
  printf("\nLigne 314 - L’estimée Pb de la matrice de projection perspective avant normalisation vaut\n"); 
  MatWriteAsc(_ppVec, ""); 
  
  Matrix _pestmx = MatAlloc(Double,3,4); 
  double **p_pestmx = MatGetDouble(_pestmx);

  for ( int i = 0 ; i < 3 ; i++ )
    for ( int j = 0; j < 4 ; j++)
      p_pestmx[i][j] = p_ppVec[i][j]/lstpVecVal;

  printf("\nLigne 327 - L’estimée Pb de la matrice de projection perspective après normalisation vaut\n"); 
  MatWriteAsc(_pestmx, "");      

  /*
   * Estimation aux moindres carres de la solution d'un systeme lineaire
   * surdetermine du type Ax=b par la methode de la pseudo-inverse
   * Retourne Mx le vecteur colonne estime ou NULL si le systeme est singulier.
   * _A, matrice des coefficients
   * p_Val  vecteur colonne des constantes 
  */

  /*
   * l'approximation de x = argmin || A x ||^2 
   * l'approximation de x = vecteur propre unitaire associé à la plus petite valeur propre de A>
  */

  //  int SymEig(Matrix Mat,Matrix *pVal,Matrix *pVec)
  //  IndMin(donne la plus petite valeur propre )
  //  retourne l'indice de la colonne du vecteur propre
  //  qui retourne un estimé de la matrice P projection perspective
  //  Normaliser cette matrice perspectve ce sont les trois derniers élements
  //  de la dernière ligne  norme euclidienne  le signe de P34 est négatif * 

  MatFree(&_A);
  MatFree(&pVal);
  MatFree(&pVec);
  MatFree(&AT);
  MatFree(&_ATA);
  //MatFree(&_pestmx);
  MatFree(&_ppVec);

   
  return _pestmx;
  // printf("---> Calibrage à écrire.\n"); return NULL; // LIGNE À SUPPRIMER
}


/* Fonction principale */
int main(int argc, char *argv[])
{
  // Initialisation du mécanisme d'affichage des messages
  InitMesg(argv);
  // Vérification du nombre de paramètres
  if (argc!=2 && argc!=4)
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
  // Lecture de la matrice des points 3D
  Matrix MatP3=MatReadAsc(argv[1]);
  if (MatP3==NULL)
    {
    Erreur("Problème lors de la lecture de la matrice des coordonnées 3D");
	  return ERR_MAT_3D;
    }
  // Vérification du type de la matrice
  if (MatType(MatP3)!=Double)
    {
    Erreur("La matrice des coordonnées 3D doit être Double");
	  MatFree(&MatP3);
	  return ERR_MAT_3D_TYPE;
    }
  // Vérification de la taille de la matrice
  if (MatNbCol(MatP3)!=3)
    {
    Erreur("La matrice des coordonnées 3D doit avoir 3 colonnes");
	  MatFree(&MatP3);
	  return ERR_MAT_3D_SIZE;
    }
  // Lecture de la matrice des points 2D
  Matrix Matp2=MatReadAsc(argv[2]);
  if (Matp2==NULL)
    {
    Erreur("Problème lors de la lecture de la matrice des coordonnées 2D");
	  MatFree(&MatP3);
	  return ERR_MAT_2D;
    }
  // Vérification du type de la matrice
  if (MatType(Matp2)!=Double)
    {
    Erreur("La matrice des coordonnées 2D doit être Double");
	  MatFree(&MatP3);
	  MatFree(&Matp2);
	  return ERR_MAT_2D_TYPE;
    }
  // Vérification de la taille de la matrice
  if (MatNbCol(Matp2)!=2)
    {
    Erreur("La matrice des coordonnées 2D doit avoir 2 colonnes");
	  MatFree(&MatP3);
	  MatFree(&Matp2);
	  return ERR_MAT_2D_SIZE;
    }
  // Vérification des nombres de points
  if (MatNbRow(MatP3)!=MatNbRow(Matp2))
    {
    Erreur("Les deux matrices doivent avoir le même nombre de lignes");
	  MatFree(&MatP3);
	  MatFree(&Matp2);
	  return ERR_MAT_SIZE;
    }
  // Estimation de la matrice de projection perspective
  Matrix MatProjPers=Calibrage(MatP3,Matp2);
  // Libération des deux matrices de points
    MatFree(&MatP3);
    MatFree(&Matp2);
  if (MatProjPers==NULL)
    {
    Erreur("Problème lors de l'estimation de la matrice de projection perspective");
	  return ERR_MAT_OUT;
    }
  // Écriture de la matrice résultat
  MatWriteAsc(MatProjPers,argv[3]);
  // Libération de la matrice résultat 
  MatFree(&MatProjPers);

  return OK;
}
