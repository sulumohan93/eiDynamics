function outTable = sdnExpected(inTable)

rows = size(inTable,1);
outTable = inTable;
outTable.ExpectedP1 = zeros(size(inTable,1),1);
outTable.ExpectedP2 = zeros(size(inTable,1),1);
outTable.ExpectedP3 = zeros(size(inTable,1),1);
outTable.ExpectedP4 = zeros(size(inTable,1),1);
outTable.ExpectedP5 = zeros(size(inTable,1),1);
outTable.ExpectedP6 = zeros(size(inTable,1),1);
outTable.ExpectedP7 = zeros(size(inTable,1),1);
outTable.ExpectedP8 = zeros(size(inTable,1),1);

for row = 1:rows
    if inTable.numSquares(row) ~= 1
        patternID = inTable.PatternID(row);
        outTable.ExpectedP1(row) = expectedFinder(patternID,'P1');
        outTable.ExpectedP2(row) = expectedFinder(patternID,'P2');
        outTable.ExpectedP3(row) = expectedFinder(patternID,'P3');
        outTable.ExpectedP4(row) = expectedFinder(patternID,'P4');
        outTable.ExpectedP5(row) = expectedFinder(patternID,'P5');
        outTable.ExpectedP6(row) = expectedFinder(patternID,'P6');
        outTable.ExpectedP7(row) = expectedFinder(patternID,'P7');
        outTable.ExpectedP8(row) = expectedFinder(patternID,'P8');
    else
        outTable.ExpectedP1(row) = outTable.P1(row);
        outTable.ExpectedP2(row) = outTable.P2(row);
        outTable.ExpectedP3(row) = outTable.P3(row);
        outTable.ExpectedP4(row) = outTable.P4(row);
        outTable.ExpectedP5(row) = outTable.P5(row);
        outTable.ExpectedP6(row) = outTable.P6(row);
        outTable.ExpectedP7(row) = outTable.P7(row);
        outTable.ExpectedP8(row) = outTable.P8(row);
    end
    
end

function expectedVal = expectedFinder(patternID,col)

    coordSet = coordSetFinder(patternID);
    expectedVal = 0;

    for i=1:length(coordSet)
        coord_temp = coordSet(i);
        patternID_temp = patternIDFinder(coord_temp);
        idx = ((inTable.numSquares ==1) & (inTable.PatternID == patternID_temp));
        P_temp = inTable(idx,col);
        P_temp = mean(table2array(P_temp));
        expectedVal = expectedVal + P_temp;
    end
end

end
