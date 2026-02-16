function f = f1_NL(x,y2,x1k,x2k,c,gama,tau1,tau2,tau3)
X= x2k-4*(x2k -Link(x1k,c));
f =tau1*sum(sum(gama*exp(y2-x)-(y2-x))) + tau2/2*(norm(d1(x))^2) + tau3*norm(x-X);

end