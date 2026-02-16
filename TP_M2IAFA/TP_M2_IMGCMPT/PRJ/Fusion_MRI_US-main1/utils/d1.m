%function d=d1(u)
%
% Returns the derivative in the first direction
%yelbenni : Exemple d1([1,4,5]) serait [3,1,0]
function d=d1(u)

d=zeros(size(u));
d(1:end-1)=u(2:end)-u(1:end-1);

