#include <stdio.h>
#include <math.h>
#include <float.h>

#include "limace.h"
#include "salade.h"

#define	SQRT2	1.41421356237309504880
#define	sgn(x)	( (x) >= 0 ? 1 : -1 )


/* Affichage des messages d'erreur
 */
static void SalError(char *Function, char *Format, ...)
{
        va_list Params;
        (void)Verbose(); if (!Verbose()) return;
        va_start(Params,Format);
        if (Function != NULL)
                fprintf(stderr, "[Salade] (%s) : ",Function);
        vfprintf(stderr,Format,Params);
        fprintf(stderr, ".\n");
        va_end(Params);
        return;
} 


/* Transformation d'un systeme lineaire surdetermine en un systeme "carre"
 * par la methode de la pseudo-inverse
 * un systeme du type Ax=b est transforme en :
 * (transpose(A)*A)x = (transpose(A)*b).
 */
void Carre(
    Matrix MA, /* matrice des coefficients (in) */
    Matrix Mb, /* vecteur des constantes */
    Matrix *pMAtA, /* nouvelle matrice des coefficients */
    Matrix *pMAtb /* nouveau vecteur des constantes */
    )
{
    int i,k,l,NLig=MatNbRow(MA),NCol=MatNbCol(MA);
    double **A,*b,**AAtA,*AAtb;
    Matrix MAAtA,MAAtb;

    MAAtA=MatCAlloc(Double,NCol,NCol);
    MAAtb=MatCAlloc(Double,NCol,1);
    AAtA=MatGetDouble(MAAtA);
    AAtb=*(MatGetDouble(MAAtb));
    A=MatGetDouble(MA);
    b=*(MatGetDouble(Mb));
    for(k=0;k<NCol;k++)
    {
        for(l=0;l<=k;l++)
              for(i=0;i<NLig;i++)
                AAtA[l][k]=(AAtA[k][l]+=A[i][l]*A[i][k]);
          for(i=0;i<NLig;i++)
              AAtb[k]+=A[i][k]*b[i];
    }
    *pMAtA=MAAtA; *pMAtb=MAAtb;
}


#define SUCCES 1
#define SINGULIERE 0

/* Resolution d'un systeme lineaire du type Ax=b par le Pivot de Gauss
 * Retourne SUCCES si tout s'est bien passe ou SINGULIERE si MA n'est pas
 * inversible (singuliere).
 */
int Gauss(
    Matrix MA,   /* matrice des coefficients (in) */
    Matrix Mb,   /* vecteur des constantes (in) */
    Matrix *pMx  /* pointeur vers le vecteur solution (out) */
    )
{
    Matrix  MB, /* matrice de travail */
            Mw; /* vecteur de travail */
    int i,j,i1,k,l,N=MatNbRow(MA);
    double Aux,Somme,T,AB,Grand,**B,*w,*xx;
    Matrix Mxx;

    /* Creation et remplissage des matrices de travail */
    MB=MatCopy(MA);
    Mw=MatCopy(Mb);

    /* Creation du vecteur solution */
    Mxx=MatAlloc(Double,MatNbRow(Mb),1);
    
    /* Creation des acces aux elements */
    B=MatGetDouble(MB);
    w=*(MatGetDouble(Mw));
    xx=*(MatGetDouble(Mxx));

    for(i=0;i<(N-1);i++)
    {
         Grand=fabs(B[i][i]);
        l=i; i1=i+1;
        /* recherche du plus grand element */
        for(j=i1;j<N;j++)
        {
            AB=fabs(B[j][i]);
            if (AB>Grand) { Grand=AB; l=j; }
        }
        if (Grand==0.0)
        {
            MatFree(&MB);
            MatFree(&Mw);
            MatFree(&Mxx);
            return(SINGULIERE);
        }
        if (l!=i)
        {
            /* permutation de lignes jusqu'a placer le plus grand  */
             /* element en diagonale                                */
            for(j=0;j<N;j++) { Aux=B[l][j]; B[l][j]=B[i][j]; B[i][j]=Aux; }
            Aux=w[l]; w[l]=w[i]; w[i]=Aux;
        }
        for(j=i1;j<N;j++)
        {
            T=B[j][i]/B[i][i];
            for(k=i1;k<N;k++) B[j][k]-=T*B[i][k];
            w[j]-=T*w[i];    
        }
    }
    if (B[N-1][N-1]==0.0)
    {
        MatFree(&MB);
        MatFree(&Mw);
        MatFree(&Mxx);
        return(SINGULIERE);
    }
    xx[N-1]=w[N-1]/B[N-1][N-1];
    /* remplacement */
    i=N-2;
    do
    {
        for(Somme=0.0,j=i+1;j<N;j++) Somme+=B[i][j]*xx[j];
        xx[i]=(w[i]-Somme)/B[i][i];
    } while (--i>=0);
    
    *pMx=Mxx;
    MatFree(&MB);
    MatFree(&Mw);
    return(SUCCES);
}


/* Estimation aux moindres carres de la solution d'un systeme lineaire
 * surdetermine du type Ax=b par la methode de la pseudo-inverse
 * Retourne le vecteur colonne estime ou NULL si le systeme est singulier.
 */
Matrix SystResol(
    Matrix MA, /* matrice des coefficients */
    Matrix Mb  /* vecteur colonne des constantes */
    )
{
    Matrix MB,Mbb,Mx;
    int Res;

    if (MatNbRow(MA)!=MatNbRow(Mb))
    {
        fprintf(stderr,"[PInv] (SystResol) : error, dimensions must agree\n");
        return NULL;
    }
    Carre(MA,Mb,&MB,&Mbb);
    Res=Gauss(MB,Mbb,&Mx);
    MatFree(&MB); MatFree(&Mbb);
    if (Res==SINGULIERE)
    {
        fprintf(stderr,"[PInv] (SystResol) : error, singular matrix\n");
        return NULL;
    }
    return(Mx);
}



/* Les fonctions suivantes, permettant de calculer les valeurs propres et 
 * vecteurs propres d'une matrice symetrique sont une adaptation de la
 * bibliotheque :
 * Meschach Library,
 * Copyright (C) 1993 David E. Steward & Zbigniew Leyk, all rights reserved.
 */


/* givens -- returns c,s parameters for Givens rotation to
		eliminate y in the vector [ x y ]' */
static void Givens(double x,double y,double *c,double *s)
{
	double	norm;

	norm = sqrt(x*x+y*y);
	if ( norm == 0.0 )
	{	*c = 1.0;	*s = 0.0;	}	/* identity */
	else
	{	*c = x/norm;	*s = y/norm;	}
}

/* rot_cols -- postmultiply mat by givens rotation described by c,s */
static void RotCols(Matrix Mat,unsigned int i,unsigned int k,double c,double s)
{
	int	j,m;
	double	temp;
	double **M;

	M=MatGetDouble(Mat);
	m=MatNbRow(Mat);

	for ( j=0; j<m; j++ )
	{
		temp = c*M[j][i] + s*M[j][k];
		M[j][k] = -s*M[j][i] + c*M[j][k];
		M[j][i] = temp;
	}
}


/* trieig -- finds eigenvalues of symmetric tridiagonal matrices
	-- matrix represented by a pair of vectors a (diag entries)
		and b (sub- & super-diag entries)
	-- eigenvalues in a on return */
static void TriEig(Matrix a, Matrix b, Matrix Q)
{
	int	i, i_min, i_max, n, split;
	double	*a_ve, *b_ve;
	double	b_sqr, bk, ak1, bk1, ak2, bk2, z;
	double	c, c2, cs, s, s2, d, mu;

	n = MatNbRow(a);
	a_ve = *MatGetDouble(a);		b_ve = *MatGetDouble(b);

	i_min = 0;
	while ( i_min < n )		/* outer while loop */
	{
		/* find i_max to suit;
			submatrix i_min..i_max should be irreducible */
		i_max = n-1;
		for ( i = i_min; i < n-1; i++ )
		    if ( b_ve[i] == 0.0 )
		    {	i_max = i;	break;	}
		if ( i_max <= i_min )
		{
		    i_min = i_max + 1;
		    continue;	/* outer while loop */
		}

		/* repeatedly perform QR method until matrix splits */
		split = 0;
		while ( ! split )		/* inner while loop */
		{

		    /* find Wilkinson shift */
		    d = (a_ve[i_max-1] - a_ve[i_max])/2;
		    b_sqr = b_ve[i_max-1]*b_ve[i_max-1];
		    mu = a_ve[i_max] - b_sqr/(d + sgn(d)*sqrt(d*d+b_sqr));

		    /* initial Givens' rotation */
		    Givens(a_ve[i_min]-mu,b_ve[i_min],&c,&s);
		    s = -s;
		    if ( fabs(c) < SQRT2 )
		    {	c2 = c*c;	s2 = 1-c2;	}
		    else
		    {	s2 = s*s;	c2 = 1-s2;	}
		    cs = c*s;
		    ak1 = c2*a_ve[i_min]+s2*a_ve[i_min+1]-2*cs*b_ve[i_min];
		    bk1 = cs*(a_ve[i_min]-a_ve[i_min+1]) +
						(c2-s2)*b_ve[i_min];
		    ak2 = s2*a_ve[i_min]+c2*a_ve[i_min+1]+2*cs*b_ve[i_min];
		    bk2 = ( i_min < i_max-1 ) ? c*b_ve[i_min+1] : 0.0;
		    z  = ( i_min < i_max-1 ) ? -s*b_ve[i_min+1] : 0.0;
		    a_ve[i_min] = ak1;
		    a_ve[i_min+1] = ak2;
		    b_ve[i_min] = bk1;
		    if ( i_min < i_max-1 )
			b_ve[i_min+1] = bk2;
		    RotCols(Q,i_min,i_min+1,c,-s);

		    for ( i = i_min+1; i < i_max; i++ )
		    {
			/* get Givens' rotation for sub-block -- k == i-1 */
			Givens(b_ve[i-1],z,&c,&s);
			s = -s;

			/* perform Givens' rotation on sub-block */
		        if ( fabs(c) < SQRT2 )
		        {	c2 = c*c;	s2 = 1-c2;	}
		        else
		        {	s2 = s*s;	c2 = 1-s2;	}
		        cs = c*s;
			bk  = c*b_ve[i-1] - s*z;
			ak1 = c2*a_ve[i]+s2*a_ve[i+1]-2*cs*b_ve[i];
			bk1 = cs*(a_ve[i]-a_ve[i+1]) +
						(c2-s2)*b_ve[i];
			ak2 = s2*a_ve[i]+c2*a_ve[i+1]+2*cs*b_ve[i];
			bk2 = ( i+1 < i_max ) ? c*b_ve[i+1] : 0.0;
			z  = ( i+1 < i_max ) ? -s*b_ve[i+1] : 0.0;
			a_ve[i] = ak1;	a_ve[i+1] = ak2;
			b_ve[i] = bk1;
			if ( i < i_max-1 )
			    b_ve[i+1] = bk2;
			if ( i > i_min )
			    b_ve[i-1] = bk;
		        RotCols(Q,i,i+1,c,-s);
		    }

		    /* test to see if matrix should be split */
		    for ( i = i_min; i < i_max; i++ )
			if ( fabs(b_ve[i]) < DBL_EPSILON*
					(fabs(a_ve[i])+fabs(a_ve[i+1])) )
			{   b_ve[i] = 0.0;	split = 1;	}

		}
	}
}

/* get_col -- gets a specified column of a matrix and retruns it as a vector */
static void GetCol(Matrix Mat,int Col, Matrix Vec)
{
  int        i,m=MatNbRow(Mat);
  double     **M=MatGetDouble(Mat),*v=*MatGetDouble(Vec);
 
   for ( i=0; i<m; i++ )
     v[i] = M[i][Col];
}              




/* hhvec -- calulates Householder vector to eliminate all entries after the
	i0 entry of the vector vec. It is returned as out. May be in-situ */
static void hhvec(Matrix vec,int i0,double *beta,Matrix out,double *newval)
{
	double	norm,*v=*MatGetDouble(vec),*o=*MatGetDouble(out);
	int i,n=MatNbRow(vec);

	for (i=i0;i<n;i++) o[i] = v[i];
	for (i=i0,norm=.0;i<n;i++) norm+=o[i] * o[i];
	if ( norm <= 0.0 )
	{
		*beta = 0.0;
		return;
	}
	norm = sqrt(norm);
	*beta = 1.0/(norm * (norm+fabs(o[i0])));
	if ( o[i0] > 0.0 )
		*newval = -norm;
	else
		*newval = norm;
	o[i0] -= *newval;
}


/* hhtrrows -- transform a matrix by a Householder vector by rows
	starting at row i0 from column j0 -- in-situ */
static void hhtrrows(Matrix Mat,int i0,int j0,Matrix hh,double beta)
{
	double	ip, scale,**M=MatGetDouble(Mat),*h=*MatGetDouble(hh);
	int	i , j ,m=MatNbRow(Mat),n=MatNbCol(Mat);

	if ( beta == 0.0 )	return;

	/* for each row ... */
	for ( i = i0; i < m; i++ )
	{	/* compute inner product */
		
	  for ( j = j0,ip=.0; j < n; j++ )
	    ip += M[i][j]*h[j];
	  scale = beta*ip;
	  if ( scale == 0.0 )
	    continue;

	  /* do operation */		
	  for ( j = j0; j < n; j++ )
	    M[i][j] -= scale*h[j];
	}

}


/* hhtrcols -- transform a matrix by a Householder vector by columns
	starting at row i0 from column j0 -- in-situ */
static void hhtrcols(Matrix Mat,int i0,int j0,Matrix hh,double beta)
{
	int	i , k ,m=MatNbRow(Mat),n=MatNbCol(Mat);
	Matrix ww=MatCAlloc(Double,n,1);
	double **M=MatGetDouble(Mat),*w=*MatGetDouble(ww),*h=*MatGetDouble(hh);

	if ( beta == 0.0 )	return;

	for ( i = i0; i < m; i++ )
	    if ( h[i] != 0.0 )
		for (k=j0;k<n;k++)
		  w[k]+=h[i]*M[i][k];
	for ( i = i0; i < m; i++ )
	    if ( h[i] != 0.0 )
		for (k=j0;k<n;k++)
		  M[i][k]-=beta*h[i]*w[k];
	MatFree(&ww);
	return;
}




/* Hfactor -- compute Hessenberg factorisation in compact form.
	-- factorisation performed in situ
	-- for details of the compact form see QRfactor.c and matrix2.doc */
static void Hfactor(Matrix A, Matrix diag, Matrix beta)
{
	Matrix tmp1;
	int	k, limit;
	double *b=*MatGetDouble(beta),*d=*MatGetDouble(diag),*t1,**a=MatGetDouble(A);

	limit = MatNbRow(A) - 1;

	tmp1 = MatAlloc(Double,MatNbRow(A),1);
	t1=*MatGetDouble(tmp1);
	
	for ( k = 0; k < limit; k++ )
	{
		GetCol(A,k,tmp1);
		hhvec(tmp1,k+1,&b[k],tmp1,&a[k+1][k]);
		d[k]=t1[k+1];
		hhtrcols(A,k+1,k+1,tmp1,b[k]);
		hhtrrows(A,0  ,k+1,tmp1,b[k]);
	}
	MatFree(&tmp1);
	return;
}


/* hhtrvec -- apply Householder transformation to vector -- may be in-situ */
static void hhtrvec(Matrix hh,double beta,int i0,Matrix in,Matrix out)
{
	double	scale,p,*h=*MatGetDouble(hh),*o=*MatGetDouble(out),*ai=*MatGetDouble(in);
	int	i,n=MatNbRow(hh),k,d=MatNbRow(in);

	for (i=i0,p=.0;i<n;i++) p+=h[i]*ai[i];
	scale = beta*p;
	for (i=0;i<n;i++) o[i]=ai[i];
	for (k=i0;k<d;k++) o[k]-=scale*h[k];
}


/* makeHQ -- construct the Hessenberg orthogonalising matrix Q;
	-- i.e. Hess M = Q.M.Q'	*/
static void makeHQ(Matrix H, Matrix diag, Matrix beta, Matrix Qout)
{
	int	i, j, m=MatNbRow(H),limit,k;
	Matrix tmp1,tmp2;
	double *t1,*t2,*d=*MatGetDouble(diag),*b=*MatGetDouble(beta),**Qo=MatGetDouble(Qout);

	limit = m - 1;    
	tmp1 = MatAlloc(Double,m,1);tmp2 = MatAlloc(Double,m,1);
	t1=*MatGetDouble(tmp1);t2=*MatGetDouble(tmp2);

	for ( i = 0; i < m; i++ )
	{
		/* tmp1 = i'th basis vector */
		for ( j = 0; j < m; j++ )
			t1[j] = 0.0; 
		   
		t1[i] = 1.0;

		/* apply H/h transforms in reverse order */
		for ( j = limit-1; j >= 0; j-- )
		{
			GetCol(H,j,tmp2);
			 t2[j+1] = d[j];
			hhtrvec(tmp2,b[j],j+1,tmp1,tmp1);
		}

		/* insert into Qout */
		for (k=0;k<m;k++) Qo[k][i]=t1[k];/*m??*/
	}
	MatFree(&tmp1); MatFree(&tmp2);
}

static int MatSym(Matrix Mat)
{
  double **M=MatGetDouble(Mat);
  int i,j,m=MatNbRow(Mat),n=MatNbCol(Mat);

  if (m!=n) return 0;
  for (i=1;i<m;i++)
    for (j=0;j<i;j++)
      if (M[i][j]!=M[j][i]) return 0;
  return 1;
}

/* Calcul des valeurs et vecteurs propres d'une matrice symetrique
 * pVal : adresse de la matrice (vecteur colonne) qui contiendra les
 *        valeurs propres ;
 * pVec : adresse de la matrice qui contiendra les vecteurs propres
 *        correspondants, un vecteur par colonne.
 *
 * Retourne 0 si tout s'est bien passe, un code d'erreur sinon :
 *    NULL_MATRIX si la matrice est vide ;
 *    MATRIX_NOT_SQUARE si la matrice n'est pas carree ;
 *    MATRIX_NOT_SYMMETRIC si la matrice n'est pas symetrique.
 */

/* symmeig -- computes eigenvalues of a dense symmetric matrix
	-- A **must** be symmetric on entry
	-- eigenvalues stored in out
	-- Q contains orthogonal matrix of eigenvectors
	-- returns vector of eigenvalues */
int SymEig(Matrix Mat,Matrix *pVal,Matrix *pVec)
{
	int	i,m=MatNbRow(Mat),n=MatNbCol(Mat);
	Matrix Q,out,tmp,bb,diag,beta;
	double **t,*o,*b;
	/*	static MAT	*tmp = MNULL;
		static VEC	*b   = VNULL, *diag = VNULL, *beta = VNULL;*/

	if ( Mat==NULL )
	  {
		SalError("SymEig","NULL Matrix");
		return NULL_MATRIX;
	  }
	if ( m != n )
	  {
		SalError("SymEig","Matrix must be square");
		return MATRIX_NOT_SQUARE;
	  }
	if ( ! MatSym(Mat) )
	  {
		SalError("SymEig","Matrix must be symmetric");
		return MATRIX_NOT_SYMMETRIC;
	  }	
	Q=MatAlloc(Double,m,m);
	out=MatAlloc(Double,m,1);
	tmp  = MatCopy(Mat);
	bb   = MatAlloc(Double,m-1,1);
	diag = MatAlloc(Double,m,1);
	beta = MatAlloc(Double,m,1);

	Hfactor(tmp,diag,beta);
        makeHQ(tmp,diag,beta,Q);
	t=MatGetDouble(tmp); o=*MatGetDouble(out); b=*MatGetDouble(bb);
	for ( i = 0; i < m - 1; i++ )
	{
		o[i] = t[i][i];
		b[i] = t[i][i+1];
	}
	o[i] = t[i][i];
	TriEig(out,bb,Q);
	MatFree(&tmp);MatFree(&bb);MatFree(&diag);MatFree(&beta);
	*pVal=out;
	*pVec=Q;
	return 0;
}

