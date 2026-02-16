function [x2] = FusionPALM(y1,y2,c,tau1, tau2, tau3, tau4, plot_fused_image)
[n1,n2] = size(y2);
 B = fspecial('gaussian',5,4);
%[FB,FBC,F2B,~] = HXconv(y2,B,'Hx');
 yint = imresize(y1,6,'bicubic');
 Jx = conv2(yint,[-1 1],'same');
 Jy = conv2(yint,[-1 1]','same');
 gradY = sqrt(Jx.^2+Jy.^2);
 m_iteration = 10;
 gama = 1e-3;
 %% parameters 

% define the difference operator kernel
dh = zeros(n1,n2);
dh(1,1) = 1;
dh(1,2) = -1;
dv = zeros(n1,n2);
dv(1,1) = 1;
dv(2,1) = -1;
% compute FFTs for filtering
FDH = fft2(dh);
FDHC = conj(FDH);
F2DH = abs(FDH).^2;
FDV = fft2(dv);
FDV = conj(FDV);
F2DV = abs(FDV).^2;
c1 = 1e-8;                                                                                           
F2D = F2DH + F2DV +c1;

%% Réglages
taup = 1;
tau = taup;%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% paramètre IRM (influence TV) %%%%%%%%%%%%%%%%%%%%%%%%%
tau10 = tau1 ;        %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% paramètre IRM (influence echo) %%%%%%%%%%%%%%%%%%%%%%%%%
tau1 = tau2;       %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% paramètre US (influence observation) %%%%%%%%%%%%%%%%%%%%%%%%%
tau2 = tau3;       %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% paramètre US (influence TV) %%%%%%%%%%%%%%%%%%%%%%%%%
tau3 = tau4;       %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% paramètre US (influence IRM) %%%%%%%%%%%%%%%%%%%%%%%%%
%a = 0.02;
%b =5e-1;
%% PALM
%stoppingrule = 1;
%tolA = 1e-4;
%maxiter = 30;
d=6;
x2 = y2+c1;
x1 = yint;

    
for i = 1:m_iteration
    
   %%%%%%%%%%%%%%%%%%%%%%%%%% update Xirm %%%%%%%%%%%%%%%%%%%%%%%%%%%
  
   x1 = FSR_xirm_NL(x1,y1,x2,gradY,B,d,c,F2D,tau,tau10,'false');
   
   %%%%%%%%%%%%%%%%%%%%%%%%%% update Xus %%%%%%%%%%%%%%%%%%%%%%%%%%%
   
   
   x2 = Descente_grad_xus_NL(y2,x1,x2,c,gama,tau1,tau2,tau3,'false',0.2);
   
end
if plot_fused_image 
    figure; imshow(x2,[]);
end

end

