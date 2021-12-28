function coordSet = coordSetFinder(patternID)

patternLUT = csvread('C:\Users\adity\OneDrive\NCBS\Lab\Projects\EI_Dynamics\Analysis\eiDynamics\patternLUT.txt');
coordSet = nonzeros(patternLUT(patternID,2:end))';

end