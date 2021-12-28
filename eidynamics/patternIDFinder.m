function patternID = patternIDFinder(coordSet)

patternLUT = csvread('C:\Users\adity\OneDrive\NCBS\Lab\Projects\EI_Dynamics\Analysis\eiDynamics\patternLUT.txt');

coordRow = zeros(1,15);
coordRow(1:length(coordSet))=coordSet;

patternID = 0;

for i=1:size(patternLUT,1)
    if coordRow == patternLUT(i,2:end)
        patternID = i;
    end
end