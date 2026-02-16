function d=dtd(u)
d=zeros(size(u));
d(2:end-1) = 2*u(2:end-1)-u(1:end-2)-u(3:end);

d(1)=u(1)-u(2);
d(end) = u(end)-u(end-1);