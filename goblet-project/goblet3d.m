global CUP_GW = 0.2;
global OPEN_IR = 2.3;
global CUPU_H = 6.6;
global CUP_IR = 3.3;
global CUPL_IH = 3.3;
global STEM_R = 0.25;
global STEM_H = 2;
global BEAD_R = 0.7;
global BEAD_H = 0.4;
global LOW_R = 0.5;
global LOW_H = 2;
global BASE_MR = 2.4;
global BASE_R = 2.3;
global BASE_H = 0.2;

global CupU_Diff = CUP_IR - OPEN_IR;
global Cup_OR = CUP_IR + CUP_GW;
global CupL_OH = CUPL_IH + CUP_GW;
global Cup_Y = BASE_H + LOW_H + BEAD_H + STEM_H + CupL_OH;
global Lip_R = CUP_GW / 2;
global Lip_X = OPEN_IR + Lip_R;
global Lip_Y = Cup_Y + CUPU_H;
global Stem_Diff = LOW_R - STEM_R;
global Stem_VR = STEM_H / 2;
global Stem_CY = BASE_H + LOW_H + BEAD_H + Stem_VR;
global Bead_Diff = BEAD_R - LOW_R;
global Bead_VR = BEAD_H / 2;
global Bead_CY = BASE_H + LOW_H + Bead_VR;
global Low_Diff = BASE_R - LOW_R;
global Base_Diff = BASE_MR - BASE_R;
global Base_VR = BASE_H / 2;

function z = Stem_OverX_Sys(ab)
  global Cup_OR; global Stem_Diff; global STEM_R;
  global CupL_OH; global Cup_Y; global Stem_VR; global Stem_CY;
  z = zeros (2, 1);
  z(1) = Cup_OR*cos(ab(2)) - (Stem_Diff*ab(1)*ab(1)+STEM_R);
  z(2) = CupL_OH*sin(ab(2))+Cup_Y - (Stem_VR*ab(1)+Stem_CY);
endfunction
[ ab, z, info ] = fsolve (@Stem_OverX_Sys, [1; -pi/2]);
global Stem_OverH = ab(1) - 1;
global CupL_OInt = ab(2);

global PREC = 0.1;

a=1+Stem_OverH:-PREC:-1;
b=-pi:PREC:0;
br=0:-PREC:-pi;
c=0:PREC:1;
cr=1:-PREC:0;
d=-1:PREC:1;
fr=0:-PREC:CupL_OInt;

Lx = Lip_R*cos(-b)+Lip_X; Ly = Lip_R*sin(-b)+Lip_Y;
AIx = -CupU_Diff*c.*c+CUP_IR; AIy = CUPU_H*c+Cup_Y;
AOx = -CupU_Diff*cr.*cr+Cup_OR; AOy = CUPU_H*cr+Cup_Y;
BIx = CUP_IR*cos(b/2); BIy = CUPL_IH*sin(b/2)+Cup_Y;
BOx = Cup_OR*cos(fr); BOy = CupL_OH*sin(fr)+Cup_Y;
Cx = Stem_Diff*a.*a+STEM_R; Cy = Stem_VR*a+Stem_CY;
Dx = -Bead_Diff*sin(b)+LOW_R; Dy = Bead_VR*cos(b)+Bead_CY;
Ex = -Low_Diff*cos(br/2)+BASE_R; Ey = LOW_H*(sin(br/2)+1)+BASE_H;
Fx = -Base_Diff*sin(b)+BASE_R; Fy = Base_VR*cos(b)+Base_VR;
Gx = BASE_R*(d+1)/2; Gy = 0*d;

# Generate mesh
Rr = [ BIx AIx Lx AOx BOx Cx Dx Ex Fx Gx ];
Zr = [ BIy AIy Ly AOy BOy Cy Dy Ey Fy Gy ];
t = (0:PREC:2*pi+PREC)';
Z = repmat (Zr, size (t)(1), 1);
X = [ ];
Y = [ ];
for r = Rr
  Xcol = r * cos(t);
  Ycol = r * sin(t);
  X = [ X Xcol ];
  Y = [ Y Ycol ];
endfor

# Display mesh
surf (X, Y, Z);
axis ("equal")
