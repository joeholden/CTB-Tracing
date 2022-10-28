title = getTitle();
roiManager("Add");
n = roiManager("count");
roiManager("Select", n-1);
if (n % 2 == 0){
	roiManager("Rename", "R_" + title);
}
else{
	roiManager("Rename", "L_" + title);
}
