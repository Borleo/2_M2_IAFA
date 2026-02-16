function x2 = Link(x1,c)

% x1 gradient
Jx = conv2(x1,[-1 1],'same');
Jy = conv2(x1,[-1 1]','same');
gradY = sqrt(Jx.^2+Jy.^2);

%Polynomial function
x2 = c(1) + c(2)*x1 + c(3)*x1.^2 + c(4)*x1.^3 + c(5)*x1.^4 +...
    c(6)*gradY + c(7)*gradY.*x1 + c(8)*gradY.*x1.^2 + c(9)*gradY.*x1.^3 ...
    + c(10)*gradY.^2 + c(11)*gradY.^2.*x1 + c(12)*gradY.^2.*x1.^2  ...
    + c(13)*gradY.^3 + + c(14)*gradY.^3.*x1...
    + c(15)*gradY.^4;

end

