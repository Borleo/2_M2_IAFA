close all
clear all
clc

addpath ./images;
addpath ./utils;

%% IMAGES creation
%Ground truth image (MR image : uterus/bladder/endometrial lesion)
load('images/init_mi256_2.mat');
irm_gt = init_mi256_2;  
n = size(irm_gt);

%Ground Truth US created by applying a polynomial
c = zeros(10,1); 
c(2) = 1;
c(3) = 1e-4;
c(4) = -1e-5;
c(5) = 1; 
c(6) = 1e-3;
c(7) = 1e-5;
us_gt = poly(irm_gt,c); 

% MRI observation
% blurring
irm1_blurred = imgaussfilt(irm_gt,4);
% decimation (d=1)
irm1_resized = irm1_blurred; %imresize(irm1_blurred,1/d);
% adding gaussian noise
sigma_noise = 0.02; 
irm = irm1_resized + sigma_noise*randn(size(irm1_resized));

% US Observation
gama = 0.21; %Log-Rayleigh noise parameter
us = us_gt + gama*log(raylrnd(1.1,n(1),n(2)));

%% Display images
figure; imshow(irm_gt,[]); title 'Ground truth MRI'
figure; imshow(us_gt,[]); title ' Ground truth US'
figure; imshow(irm,[]); title 'MRI observation';
figure; imshow(us,[]); title 'US observation'

% === Sauvegarde des figures dans le dossier images ===
outdir = fullfile(pwd, 'images');    % dossier "images" sous le répertoire courant
if ~exist(outdir, 'dir')
    mkdir(outdir);
end

saveas(1, fullfile(outdir, 'irm_gt.png'));
saveas(2, fullfile(outdir, 'us_gt.png'));
saveas(3, fullfile(outdir, 'irm.png'));
saveas(4, fullfile(outdir, 'us.png'));

%% PALM Fusion

estimate_c;
c = abs(cest);

ym = double(irm)./double(max(irm(:)));
yu = double(us)./double(max(us(:)));

net = denoisingNetwork('DnCNN');
xu0 = denoiseImage(yu,net); 

tau1 = 1e-5;
tau2 = 5e-1; 
tau3 = 2e-2;       
tau4 = 1e-5;   
[x2] = FusionPALM(ym,xu0,c,tau1, tau2, tau3, tau4, true);

figure; imshow(x2,[]); title('Fused image');
saveas(gcf, fullfile(outdir, 'fusion1.png'));

%% Pixel intensities on a vertical line of the image
%Interpretation : 
% MRI shows the change of pixel intensities between two structures, but fails to show the exact border.
%US shows the border (as a peak of intensities).
%Fused image shows both.
num_col = 265; % column of interest
% extracting the columns
col_us = yu(100:300,num_col);
col_irm = ym(100:300,num_col);
col_fusion = x2(100:300,num_col);

figure,
plot(100:300,(col_irm-min(col_irm))/(max(col_irm)-min(col_irm)),'k');
hold on;
plot(100:300,(col_us-min(col_us))/(max(col_us)-min(col_us)),'g');
hold on;
plot(100:300,(col_fusion-min(col_fusion))/(max(col_fusion)-min(col_fusion)),'r');
xlabel('pixels');
ylabel('Normalized pixel intensitiy');
legend('MRI','US','Fused'); 


% showing the selected column
yu(:,num_col) = yu(:,num_col) + 0.2;
figure;
imshow(yu,[]); 
title('selected column');
yu(:,num_col) = yu(:,num_col) - 0.2;


%% Functions
function x2 = poly(x1,c)

% x1 gradient
Jx = conv2(x1,[-1 1],'same');
Jy = conv2(x1,[-1 1]','same');
gradY = sqrt(Jx.^2+Jy.^2);

%Polynomial function
x2 = c(1) + c(2)*x1 + c(3)*x1.^2 + c(4)*x1.^3 + c(5)*gradY + c(6)*gradY.*x1 + c(7)*gradY.*x1.^2 + c(8)*gradY.^2 ...
    + c(9)*gradY.^2.*x1 +c(10)*gradY.^3;

end
