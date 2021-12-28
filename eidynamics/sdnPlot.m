function sdnPlot(inTable,titleString)

idx = (inTable.numSquares ~=1)&(inTable.ExpectedP1 ~= inTable.P1)&(inTable.unit~='pA');
figure('units','normalized','outerposition',[0 0 1 1])
sgtitle(titleString)


subplot(3,3,1)
scatter(inTable.ExpectedP1(idx),inTable.P1(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,2)
scatter(inTable.ExpectedP2(idx),inTable.P2(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,3)
scatter(inTable.ExpectedP3(idx),inTable.P3(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,4)
scatter(inTable.ExpectedP4(idx),inTable.P4(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,5)
scatter(inTable.ExpectedP5(idx),inTable.P5(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,6)
scatter(inTable.ExpectedP6(idx),inTable.P6(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,7)
scatter(inTable.ExpectedP7(idx),inTable.P7(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,8)
scatter(inTable.ExpectedP8(idx),inTable.P8(idx),50,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')
% ylim([0 15])

subplot(3,3,9)
% scatter(inTable.ExpectedP1(idx),inTable.P1(idx),100,[0.05*ones(sum(idx),1) 0.25*ones(sum(idx),1) 0.05*inTable.numSquares(idx)],'filled')

% figure('units','normalized','outerposition',[0 0 1 1])

saveas(gcf,titleString,'png')
close
end