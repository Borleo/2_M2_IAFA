%function d=d1(u)
%
% Returns the derivative in the first direction
function d=d1(u)

d=zeros(size(u));
d(1:end-1)=u(2:end)-u(1:end-1);