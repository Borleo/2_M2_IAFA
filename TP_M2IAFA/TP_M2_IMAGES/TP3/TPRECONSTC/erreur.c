#include <stdio.h>
#include <string.h>
#include <math.h>
#include "limace.h"
#include "erreurs.h"

/* Codes de retour */
#define OK            0
#define HELP          1
#define ERR_NB_PARAM  2
#define ERR_MAT1      3
#define ERR_MAT1_TYPE 4
#define ERR_MAT1_SIZE 5
#define ERR_MAT2      6
#define ERR_MAT2_TYPE 7
#define ERR_MAT2_SIZE 8
#define ERR_MAT_SIZE  9

/* Affichage de la syntaxe d'appel du programme */
void Syntaxe(void)
{
  Usage("p3d1.mx p3d2.mx\n"
        "-h\n");
}

/* Affichage de la description du programme */
void Description(void)
{
  Mesg("ROLE\n");
  Mesg("\tAffichage de l'erreur de reconstruction\n");
  Mesg("ARGUMENTS\n");
  Mesg("\tp3d1.mx : Matrice n x 3 (format Matrix) de coordonnées de points 3D\n");
  Mesg("\tp3d2.mx : Matrice n x 3 (format Matrix) de coordonnées de points 3D\n");
  Mesg("OPTION\n");
  Mesg("\t-h : affichage de l'aide\n");
  Mesg("DIAGNOSTIC (codes de retour)\n");
  Mesg("\t0 : opération réalisée sans problème\n");
  Mesg("\t1 : aide demandée\n");
  Mesg("\t2 : mauvais nombre de paramètres\n");
  Mesg("\t3 : problème d'ouverture du fichier de la première matrice de coordonnées\n");
  Mesg("\t4 : type de la première matrice incorrect (Double attendu)\n");
  Mesg("\t5 : taille de la première matrice incorrecte (3 colonnes attendues)\n");
  Mesg("\t6 : problème d'ouverture du fichier de la seconde matrice de coordonnées\n");
  Mesg("\t7 : type de la seconde matrice incorrect (Double attendu)\n");
  Mesg("\t8 : taille de la seconde matrice incorrecte (3 colonnes attendues)\n");
  Mesg("\t9 : les deux matrices n'ont pas le même nombre de lignes\n");
}


/* Calcul de l'erreur moyenne de reconstruction 
 * Entrées :
 *    - Mat1 : matrice de coordonnées de points  
 *              de type Double de taille n x 3 
 *    - Mat1 : matrice de coordonnées de points  
 *              de type Double de taille n x 3 
 * Valeur de retour : distance euclidienne moyenne entre les points 
 */
double ErreurMoy(Matrix _Mat1, Matrix _Mat2)
{
  int n_mat1       = MatNbRow(_Mat1);
  double **Mat1 = MatGetDouble(_Mat1);
  double **Mat2 = MatGetDouble(_Mat2);

  double sum_error = 0.0;

  for (int i = 0; i < n_mat1; i++) 
    {
      double dx = Mat1[i][0] - Mat2[i][0];
      double dy = Mat1[i][1] - Mat2[i][1];
      double dz = Mat1[i][2] - Mat2[i][2];
      sum_error += sqrt(dx*dx + dy*dy + dz*dz);
    }

    double error = sum_error / n_mat1;
    printf("\nL'erreur moyenne de reconstruction calculée est de % .16e\n", error);
    /*L'erreur moyenne de reconstruction calculée est de 9.3156463720701921e-01*/
    return error;
}


/* Fonction principale */
int main(int argc, char *argv[])
{
  // Initialisation du mécanisme d'affichage des messages
  InitMesg(argv);
  // Vérification du nombre de paramètres
  if (argc!=2 && argc!=3)
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
  Matrix Mat1=MatReadAsc(argv[1]);
  if (Mat1==NULL)
  {
    Erreur("Problème lors de la lecture de la première matrice");
	return ERR_MAT1;
  }
  if (MatType(Mat1)!=Double)
  {
    Erreur("La première matrice doit être Double");
	MatFree(&Mat1);
	return ERR_MAT1_TYPE;
  }
  if (MatNbCol(Mat1)!=3)
  {
    Erreur("La première matrice doit être avoir 3 colonnes");
	MatFree(&Mat1);
	return ERR_MAT1_SIZE;
  }
  Matrix Mat2=MatReadAsc(argv[2]);
  if (Mat2==NULL)
  {
    Erreur("Problème lors de la lecture de la seconde matrice");
    MatFree(&Mat1);
	return ERR_MAT2;
  }
  if (MatType(Mat2)!=Double)
  {
    Erreur("La seconde matrice doit être Double");
    MatFree(&Mat1);
	MatFree(&Mat2);
	return ERR_MAT2_TYPE;
  }
  if (MatNbCol(Mat2)!=3)
  {
    Erreur("La seconde matrice doit avoir 3 colonnes");
    MatFree(&Mat1);
	MatFree(&Mat2);
	return ERR_MAT2_SIZE;
  }
  if (MatNbRow(Mat1)!=MatNbRow(Mat2))
  {
    Erreur("Les deux matrices doivent avoir le même nombre de lignes");
    MatFree(&Mat1);
	MatFree(&Mat2);
	return ERR_MAT_SIZE;
  }
     
  // Calcul de l'erreur moyenne
  double Err=ErreurMoy(Mat1,Mat2);
  MatFree(&Mat1);
  MatFree(&Mat2);
  printf("% .16e\n",Err);

  return OK;
}
