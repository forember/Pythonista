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

function dV = CupU_dHV (y)
  global CupU_Diff; global CUPU_H; global CUP_IR;
  dV = pi*(-CupU_Diff*y.*y/(CUPU_H*CUPU_H)+CUP_IR).^2;
endfunction
CupU_HV = quad("CupU_dHV", 0, CUPU_H);

function dV = CupL_dHV (y)
  global CUP_IR; global CUPL_IH;
  dV = pi*CUP_IR*CUP_IR*(1-y.*y/(CUPL_IH*CUPL_IH));
endfunction
CupL_HV = quad("CupL_dHV", 0, CUPL_IH);

Hold_Volume = CupU_HV + CupL_HV


Lip_GV = pi*pi*Lip_X*Lip_R*Lip_R;

function dV = CupU_dOV (y)
  global CupU_Diff; global CUPU_H; global Cup_OR;
  dV = pi*(-CupU_Diff*y.*y/(CUPU_H*CUPU_H)+Cup_OR).^2;
endfunction
CupU_GV = quad("CupU_dOV", 0, CUPU_H) - CupU_HV;

function dV = CupL_dOV (y)
  global Cup_OR; global CupL_OH;
  dV = pi*Cup_OR*Cup_OR*(1-y.*y/(CupL_OH*CupL_OH));
endfunction
CupL_Int_UB = CupL_OH - Stem_VR*Stem_OverH;
CupL_GV = quad("CupL_dOV", 0, CupL_Int_UB) - quad("CupL_dHV", 0, min(CupL_Int_UB, CUPL_IH));

function dV = Stem_dV (y)
  global Stem_Diff; global Stem_VR; global STEM_R;
  dV = pi*(Stem_Diff*y.*y/(Stem_VR*Stem_VR)+STEM_R).^2;
endfunction
Stem_V = quad("Stem_dV", -Stem_VR, (1+Stem_OverH)*Stem_VR);

function dV = Bead_dV (y)
  global Bead_Diff; global Bead_VR; global LOW_R;
  dV = pi*(Bead_Diff*sin(acos(y/Bead_VR))+LOW_R).^2;
endfunction
Bead_V = quad("Bead_dV", -Bead_VR, Bead_VR);

function dV = Low_dV (y)
  global Low_Diff; global LOW_H; global BASE_R;
  dV = pi*(Low_Diff*cos(asin(y/LOW_H-1))+BASE_R).^2;
endfunction
Low_V = quad("Low_dV", 0, LOW_H);

function dV = Base_dV (y)
  global Base_Diff; global Base_VR; global BASE_R;
  dV = pi*(Base_Diff*sin(acos(y/Base_VR))+BASE_R).^2;
endfunction
Base_V = quad("Base_dV", -Base_VR, Base_VR);

Glass_Volume = Lip_GV + CupU_GV + CupL_GV + Stem_V + Bead_V + Low_V + Base_V

Cup_Glass_Volume = Lip_GV + CupU_GV + CupL_GV
Bottom_Glass_Volume = Stem_V + Bead_V + Low_V + Base_V
Bottom_H = Stem_OverH*Stem_VR + STEM_H + BEAD_H + LOW_H + BASE_H

global PREC = 0.01;

a=1+Stem_OverH:-PREC:-1;
b=-pi:PREC:0;
c=0:PREC:1;
d=-1:PREC:1;
f=CupL_OInt:PREC:0;

Lx = Lip_R*cos(-b)+Lip_X; Ly = Lip_R*sin(-b)+Lip_Y;
AIx = -CupU_Diff*c.*c+CUP_IR; AIy = CUPU_H*c+Cup_Y;
AOx = -CupU_Diff*c.*c+Cup_OR; AOy = CUPU_H*c+Cup_Y;
BIx = CUP_IR*cos(b); BIy = CUPL_IH*sin(b)+Cup_Y;
BOx = Cup_OR*cos(f); BOy = CupL_OH*sin(f)+Cup_Y;
Cx = Stem_Diff*a.*a+STEM_R; Cy = Stem_VR*a+Stem_CY;
Dx = -Bead_Diff*sin(b)+LOW_R; Dy = Bead_VR*cos(b)+Bead_CY;
Ex = -Low_Diff*cos(b/2)+BASE_R; Ey = LOW_H*(sin(b/2)+1)+BASE_H;
Fx = -Base_Diff*sin(b)+BASE_R; Fy = Base_VR*cos(b)+Base_VR;
Gx = BASE_R*d; Gy = 0*d;

plot (...
      BOx, BOy, "linewidth", 2, ...
      -BOx, BOy, "linewidth", 2, ...
      ...
      AOx, AOy, "linewidth", 2, ...
      -AOx, AOy, "linewidth", 2, ...
      ...
      Lx, Ly, "linewidth", 2, ...
      -Lx, Ly, "linewidth", 2, ...
      ...
      AIx, AIy, "linewidth", 2, ...
      -AIx, AIy, "linewidth", 2, ...
      ...
      BIx, BIy, "linewidth", 2, ...
      ...
      Cx, Cy, "linewidth", 2, ...
      -Cx, Cy, "linewidth", 2, ...
      ...
      Dx, Dy, "linewidth", 2, ...
      -Dx, Dy, "linewidth", 2, ...
      ...
      Ex, Ey, "linewidth", 2, ...
      -Ex, Ey, "linewidth", 2, ...
      ...
      Fx, Fy, "linewidth", 2, ...
      -Fx, Fy, "linewidth", 2, ...
      Gx, Gy, "linewidth", 2 ...
      );
axis ("equal");
