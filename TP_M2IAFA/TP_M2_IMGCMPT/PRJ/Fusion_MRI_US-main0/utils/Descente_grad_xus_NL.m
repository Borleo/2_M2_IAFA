function [x2,fopt,niter] = Descente_grad_xus_NL(y2,x1k,x2k,c,gama,tau1,tau2,tau3,display,alpha)
% Cette fonction résout analytiquement le problème 
% xirm = argmin_x ||SHx-yirm||^2 + ||Dx||^2 + || xus - (c1+c2*gradY+c3*xirm)||^2
% 
% Entrées : 
%    y1 : image IRM (observation) n1y*n2y
%    xus : Image Us apres le débruitage (à l'étape k) n1*n2
%    B : Filtre 2D pour le floutage de l'image IRM (H =F^hBF) 7*7
%    d : ratio de la super résolution (entier)
%    c1,c2 : coefs du polymone qui relie xus et xirm
%    F2D: transformée de Fourier de la dérivé analytique 
%    tau : hyperparamètre => influence de la TV
%    tau10 : huperparamètre => influence de l'écho
%    a : affichage de la sortie (si a = 'true')
%
% Sortie : 
%    x1 : image super-résolue n1*n2
%
%

[n1,n2] = size(y2);
c1 = 1e-8;
y2 = reshape(y2,n1*n2,1);
x1k = reshape(x1k,n1*n2,1);
x2k = reshape(x2k,n1*n2,1);
x0 = y2+c1;
f = @(x)f1_NL(x,y2,x1k,x2k,c,gama,tau1,tau2,tau3);
gradf = @(x)gradf1_NL(x,y2,x1k,x2k,c,gama,tau1,tau2,tau3);
% termination tolerance
tol = 1e-6;

% maximum number of allowed iterations
maxiter = 100;

% minimum allowed perturbation
dxmin = 1e-2;

% step size
%alpha = 20;

% initialize gradient norm, optimization vector, iteration counter, perturbation
gnorm = inf; x = x0; niter = 0; dx = inf;
while and(gnorm>=tol, and(niter <= maxiter, dx >= dxmin))
    % calculate gradient:
    g = gradf(x);
    % take step:
    xnew = x - alpha*g;
    % check step
    if ~isfinite(xnew)
        display(['Number of iterations: ' num2str(niter)])
        error('x is inf or NaN')
    end
   
    % update termination metrics
    niter = niter + 1;
    dx = norm(xnew-x);
    x = xnew;
    
end
fopt = f(x);
niter = niter - 1;

x = reshape(x,n1,n2);
x2 = x;
% display
if ( display == true)

figure; imshow(x2,[]);
end

end