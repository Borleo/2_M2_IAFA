close all
clear all
clc

addpath ./utils;
addpath ./images;

%% Read images
%Groud truth MRI
irm1_gt = double(imread('images/irm_simu.PNG')); 
irm1_gt = irm1_gt(:,:,1); 
irm1_gt = irm1_gt/max(irm1_gt(:)); 

%Ground Truth US created by applying a polynomial
c = zeros(10,1);
c(2) = 1;
c(3) = 1e-4;
c(4) = -1e-5;
c(5) = 1; 
c(6) = 1e-3;
c(7) = 1e-5;
us1_gt = Link_poly(irm1_gt,c); % Ground truth US image created by a polynomial 

figure; 
imshow(irm1_gt,[]); colormap gray;
title('MRI GT');
figure; 
imshow(us1_gt,[]); colormap gray;
title('US GT');
%% Creation of the observed images

%% 1. Images GT (avant bruit)
outdir = fullfile(pwd, 'images');
if ~exist(outdir, 'dir')
    mkdir(outdir);
end

saveas(1, fullfile(outdir, 'irm1_gt.png'));
saveas(2, fullfile(outdir, 'us1_gt.png'));

% MRI observed image
% blurring
irm1_blurred = imgaussfilt(irm1_gt,4);
% decimation (d=1)
irm1_resized = irm1_blurred; %imresize(irm1_blurred,1/d);
% adding gaussian noise
sigma_noise = 0.026;
irm1 = irm1_resized + sigma_noise*randn(size(irm1_resized));


figure; 
imshow(irm1,[]); colormap gray;
title('MRI observation');

%% 2. Images observées (après bruit)
saveas(3, fullfile(outdir, 'irm1_obs.png'));

% US observed image
[n11,n21] = size(irm1_gt);
gamma1 = 0.09; % log-rayleigh noise parameter
us1 = us1_gt + gamma1*log(raylrnd(1,n11,n21)); % adding log-rayleigh noise

%% 2. Images observées (après bruit)
figure; 
imshow(us1,[]); colormap gray;
title('US observation');

%% 2. Images observées (après bruit)
saveas(4, fullfile(outdir, 'us1_obs.png'));

%% Fusion of the observed US and MRI
irm = irm1;
us = us1;
estimate_c; 

output_args = cest;
c = abs(output_args);

ym = double(irm)./double(max(irm(:)));
yu = double(us)./double(max(us(:)));

net = denoisingNetwork('DnCNN');
xu0 = denoiseImage(yu,net); 

tau1 = 1e-12; 
tau2 =3e-6; 
tau3 = 2e-6; 
tau4 = 1e-5;
[x2] = FusionPALM(ym,xu0,c,tau1, tau2, tau3, tau4, true);
%% l'image fusionnée 

figure; imshow(x2,[]); colormap gray;
title('Fused image');
saveas(gcf, fullfile(outdir, 'fusion2.png'));

%% Functions
function x2 = Link_poly(x1,c)
% x1 gradient
Jx = conv2(x1,[-1 1],'same');
Jy = conv2(x1,[-1 1]','same');
gradY = sqrt(Jx.^2+Jy.^2);

%Polynomial function
x2 = c(1) + c(2)*x1 + c(3)*x1.^2 + c(4)*x1.^3 +...
    c(5)*gradY + c(6)*gradY.*x1 + c(7)*gradY.*x1.^2 ...
    + c(8)*gradY.^2 + c(9)*gradY.^2.*x1 +  ...
    + c(10)*gradY.^3;

end