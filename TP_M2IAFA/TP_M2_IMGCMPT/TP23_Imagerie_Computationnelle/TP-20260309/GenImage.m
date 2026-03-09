%% Sparse image

% Generation of a sparse image
N = 512;
M = 512;
sparse = 0.01;

i_sparse = zeros(N, M);
i_sparse = i_sparse(:);
n = length(i_sparse);
pos = randperm(n);
i_sparse(pos(1:round(n*sparse))) = 1;
i_sparse = reshape(i_sparse, N, M);

figure
imagesc(i_sparse); colormap gray;

%% piecewise-constant image 
N = 512;
M = 512;

image_tv = zeros(N, M);
image_tv(1:256,1:256) = .8;
image_tv(1:256, 256:512) = .6;
image_tv(256:384,1:512) = .4;
image_tv(384:512,1:100) = .7;
image_tv(384:512,100:512) = .8;

figure
imagesc(image_tv); colormap gray;