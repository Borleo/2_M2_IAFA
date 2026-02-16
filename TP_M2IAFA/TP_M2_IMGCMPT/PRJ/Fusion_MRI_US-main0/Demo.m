%**************************************************************************
% Author: Oumaima El Mansouri (2019 Oct.)
% University of Toulouse, IRIT/INP-ENSEEIHT
% Email: oumaima.el-mansouri@irit.fr
% ---------------------------------------------------------------------
% Copyright (2020): Oumaima El Mansouri, Fabien Vidal, Adrian~Basarab, Denis Kouamé, Jean-Yves Tourneret.
% 
% Permission to use, copy, modify, and distribute this software for
% any purpose without fee is hereby granted, provided that this entire
% notice is included in all copies of any software which is or includes
% a copy or modification of this software and in all copies of the
% supporting documentation for such software.
% This software is being provided "as is", without any express or
% implied warranty.  In particular, the authors do not make any
% representation or warranty of any kind concerning the merchantability
% of this software or its fitness for any particular purpose."
% ---------------------------------------------------------------------
% 
% This set of MATLAB files contain an implementation of the algorithms
% described in the following paper (Without backtracking step):
% 
% [1] EL MANSOURI, Oumaima, VIDAL, Fabien, BASARAB, Adrian, et al. Fusion of magnetic resonance and ultrasound images 
% for endometriosis detection. IEEE Transactions on Image Processing, 2020, vol. 29, p. 5324-5335.
%
% ---------------------------------------------------------------------
%************************************************************************** 
%%
close all
clear all
clc

addpath ./utils;
addpath ./images;

%% Load or read images
% if needed resize MRI and US images (Nus = d*Nmri), in this example d = 6
% (d is an integer)
load('images/Data2/irm.mat'); %MRI image
load('images/Data2/us.mat');% US image

% Compute the polynomial coefficients
estimate_c;
output_args = cest;
c = abs(output_args);

%% Image normalization
%linear normalization
ym = double(irm)./double(max(irm(:)));
yu = double(us)./double(max(us(:)));

%% Display observations

figure; imshow(irm,[]);
figure; imshow(us,[]);

%% Initialization of PALM

d=6; %MRI and US must have the same size
xm0 = imresize(ym,d,'bicubic'); %MRI bicubic interpolation

net = denoisingNetwork('DnCNN');
xu0 = denoiseImage(yu,net); %US denoising

%% Regularization parameters
% Tune these parameters for PALM convergence
tau1 = 1e-12;
tau2 =1e-4;
tau3 = 2e-4;
tau4 = 1e-4;

%% Fusion of MRI and US images

[x2] =FusionPALM(ym,xu0,c,tau1, tau2, tau3, tau4, true);

%% Compute metrics
%TO DO

%% PALM algorithm for MRI and US fusion 
function [x2] = FusionPALM(y1,y2,c,tau1, tau2, tau3, tau4, plot_fused_image)
[n1,n2] = size(y2);
B = fspecial('gaussian',5,4); % Blur modelisation, tune these parameters
%[FB,FBC,F2B,~] = HXconv(y2,B,'Hx');
yint = imresize(y1,6,'bicubic'); % MRI super-resolution
%compute MRI gradient
Jx = conv2(yint,[-1 1],'same');
Jy = conv2(yint,[-1 1]','same');
gradY = sqrt(Jx.^2+Jy.^2);


%% parameters
m_iteration = 10;
gamma = 1e-3;
% define the difference operator kernel
dh = zeros(n1,n2);
dh(1,1) = 1;
dh(1,2) = -1;
dv = zeros(n1,n2);
dv(1,1) = 1;
dv(2,1) = -1;
% compute FFTs for filtering
FDH = fft2(dh);
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
d=6;
x2 = y2+c1;
x1 = yint;


for i = 1:m_iteration
    
    %%%%%%%%%%%%%%%%%%%%%%%%%% update Xirm %%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    x1 = FSR_xirm_NL(x1,y1,x2,gradY,B,d,c,F2D,tau,tau10,false);
    
    %%%%%%%%%%%%%%%%%%%%%%%%%% update Xus %%%%%%%%%%%%%%%%%%%%%%%%%%%
    
    x2 = Descente_grad_xus_NL(y2,x1,x2,c,gamma,tau1,tau2,tau3,false,0.2);
    
end
if plot_fused_image
    figure; imshow(x2,[]);
end

end

