%% Input images

%compute the norms
y1=irm;
y2 = us./norm(us);

%y2 =us;
[n1,n2] = size(y2);

%resize the image to be 6 times bigger using bicubic
yint = y1;  %imresize(y1,6,'bicubic');

%YOUSSRA - denoise US image
%net = denoisingNetwork('DnCNN');
%y2 = denoiseImage(y2,net); %US denoising

%compute gradient
Jx = conv2(yint,[-1 1],'same');
Jy = conv2(yint,[-1 1]','same');
gradY = sqrt(Jx.^2+Jy.^2); 

% Image vectorization
yi = reshape(yint,n1*n2,1);
yu = reshape(y2,n1*n2,1);
dyi =reshape(gradY,n1*n2,1);

% Compute matrice A
A = [ones(n1*n2,1) yi yi.^2 yi.^3 yi.^4 dyi dyi.*yi dyi.*yi.^2 dyi.*yi.^3 dyi.^2 dyi.^2.*yi ...
      dyi.^2.*yi.^2 dyi.^3 dyi.^3.*yi dyi.^4]; 
%A = [ones(n1*n2,1) yi yi.^2 yi.^3 dyi dyi.*yi dyi.*yi.^2 dyi.^2 dyi.^2.*yi ...
     % dyi.^3  ]; 
%% Pseudo inverse
%TO DO: one can add a regularization for the estimation of the polynomial
%coefficients
cest = pinv(A)*yu;  %%resultat


%% Compute xu = f(ym)
xu = A*cest;
xu = reshape(xu,n1,n2);

% % Display the result (uncomment to display)
%   figure;  imagesc(y2); colormap 'gray'
%   title('y_{us}');
% 
%   figure; imagesc(yu); colormap 'gray'
%   title('yu = normalized us image')
%  
%    figure; imagesc(yint); colormap 'gray'
%   title('yint = resize irm 6')
% 
%   figure; imagesc(yi); colormap 'gray'
%   title('yi = reshape(yint,600*600,1)')
%    
%   figure;  imagesc(xu); colormap 'gray'
%   title('\Phi(y_{irm})');
%   figure; imagesc(y1);colormap 'gray'
%   title('y_{irm}');
