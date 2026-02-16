function x1 = FSR_xirm_NL(x1k,y1,xus,gradY,B,d,c,F2D,tau,tau10,display)
% Cette fonction résout analytiquement le problème 
% xirm = argmin_x ||SHx-yirm||^2 + ||Dx||^2 + || xus - (c1+c2*gradY+c3*xirm)+D||^2
% 
% Entrées : 
%    y1 : image IRM (observation) n1y*n2y
%    xus : Image Us apres le débruitage (à l'étape k) n1*n2
%    B : Filtre 2D pour le floutage de l'image IRM (H =F^hBF) 7*7
%    d : ratio de la super résolution (entier)
%    c1,c2 : coefs du polymone qui relie xus et xirm
%    alpha : c1 + c2*gradY
%    F2D: transformée de Fourier de la dérivé analytique 
%    tau : hyperparamètre => influence de la TV
%    tau10 : huperparamètre => influence de l'écho
%    a : affichage de la sortie (si a = 'true')
%
% Sortie : 
%    x1 : image super-résolue n1*n2
%
%
[n1y,n2y] = size(y1);
n = size(xus);

X = x1k-4*( c(2) + 2*c(3)*x1k + 3*c(4)*x1k.^2 +4*c(5)*x1k.^3 +  c(7)*gradY + 2*c(8)*gradY.*x1k + 3*c(9)*gradY.*x1k.^2 +...    
     c(11)*gradY.^2 + 2*c(12)*gradY.^2.*x1k + c(14)*gradY.^3).*(xus-Link(x1k,c)) ;
% yirm = SHxirm + n2 ...
STy = zeros(n);
STy(1:d:end,1:d:end)=y1;
[FB,FBC,F2B,~] = HXconv(STy,B,'Hx');

% Solution analytique
FR = FBC.*fft2(STy) + fft2(2*tau10*X);

l1 = FB.*FR./(F2D+100*tau10/tau);
FBR = BlockMM(n1y,n2y,d*d,n1y*n2y,l1);
invW = BlockMM(n1y,n2y,d*d,n1y*n2y,F2B./(F2D+100*tau10/tau));
invWBR = FBR./(invW + tau*4);


fun = @(block_struct) block_struct.data.*invWBR;
FCBinvWBR = blockproc(FBC,[n1y,n2y],fun);
FX = (FR-FCBinvWBR)./(F2D+100*tau10/tau)/tau;
x1 = real(ifft2(FX));

% display
if display == true
figure; imshow(x1,[]);
end
end


function x = BlockMM(nr,nc,Nb,m,x1)
myfun = @(block_struct) reshape(block_struct.data,m,1);
x1 = blockproc(x1,[nr nc],myfun);
x1 = reshape(x1,m,Nb);
x1 = sum(x1,2);
x = reshape(x1,nr,nc);
end
