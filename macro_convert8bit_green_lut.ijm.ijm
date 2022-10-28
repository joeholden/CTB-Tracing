save_dir = "C:/Users/Acer/Desktop/test_dir/38/"
dir = getDir('choose');
files = getFileList(dir);
for (m=0; m< files.length; m++) { 
		run("Bio-Formats (Windowless)", "open=[" + dir + files[m]+"]");
		title = getTitle();
		title_no_ext = File.nameWithoutExtension;
		run("Green");
		setOption("ScaleConversions", true);
		run("8-bit");
		saveAs("Tiff", save_dir + title_no_ext + ".tif");
		close();
}
