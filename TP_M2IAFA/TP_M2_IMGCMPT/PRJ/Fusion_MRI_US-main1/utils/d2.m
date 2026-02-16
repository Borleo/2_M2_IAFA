%function d=d2(u)
%
% Returns the derivative in the second direction
function d=d2(u)

d=zeros(size(u));
d(1:end-1)=u(2:end)-u(1:end-1);
