#This code takes the output from pcb2gcode, as well as a probe file,
#and modifies the PCB-milling gcode to account for irrecularities in
#the copper-clad board.
#
#It's tailored for pcb2gcode output*, and is thus somewhat fragile.
#
#*assumes all milling lines are simply in the form Xnn.nnnn Ynn.nnnn
#*Assumes all lines starting with "G00 X" are moving to a new location to plunge,
#	and that the next line is the actual plunge line
#
#All other lines are simply passed through and printed as-is.

import math;
import numpy;

#===START STUFF TO EDIT===
#Nominal etching depth
BASE_DEPTH=-0.0025;

infilename = "/tmp/foo";				#Input file from pcb2gcode
outfilename = "/tmp/bar";				#output filename
probefilename = "/tmp/probepoints.dat";	#Depth-probe data file, from pcb-probe.ngc

#Probe {x,y} {center,count,step} values
cx = -0.1;
npx = 3;
pxstep = 0.1;
cy = 0.0;
npy = 3;
pystep = 0.1
#===END STUFF TO EDIT===


#Calculate offsets of pure coordinates to help create matrix indices
xoffset = cx - (npx-1)*pxstep/2.0
yoffset = cy - (npy-1)*pystep/2.0

#Helper functions- converts a raw x or y coordinate into a z-depth matrix index
def x2idx(x):
	return (x-xoffset)/pxstep;

def y2idx(y):
	return (y-yoffset)/pystep;

#Open relevant files
infile = open(infilename,"r");
outfile = open(outfilename,"w");
probefile = open(probefilename,"r");

#Read probe data
probedata = None;

#Make an empty matrix to store data
probedata = [[0 for foo in xrange(npy)] for bar in xrange(npx)];

#Read the data in
for LINE in probefile:
	x,y,z,trash = LINE.split(None, 3);
	probedata[int((float(x)-xoffset)/pxstep)][int((float(y)-yoffset)/pystep)] = float(z);

#Modify GCode
modplunge = 0;
x = 0;
y = 0;

for LINE in infile:
	#print LINE,
	#We're modifying a plunge line
	if modplunge == 1:
		#If this line seems to not be what we're expecting, abort
		if (not "G01 " in LINE) or (not "Z" in LINE):
			print "Line \"" + LINE + "\" doesn't seem to be the plunge we're expecting"
			exit(-1);
		modplunge = 0;
		z = LINE.split(" ");
		#Assume everything is going to ~BASE_DEPTH
		#depth = z[1].strip("Z");
		feed = z[2];
		depth = float(depth);
		xidx = x2idx(x)
		yidx = y2idx(y)
		xmin = numpy.clip(int(math.floor(xidx)), 0, npx-1)
		xmax = numpy.clip(int(math.ceil(xidx)), 0, npx-1)
		ymin = numpy.clip(int(math.floor(yidx)), 0, npy-1)
		ymax = numpy.clip(int(math.ceil(yidx)), 0, npy-1)
		#interpolate along Y
		frac = ymax - y;
		#print str(frac) + " towards y=" + str(ymin) + "; y=" + str(y)
		d1 = probedata[xmin][ymin] * frac + probedata[xmin][ymax] * (1 - frac);
		d2 = probedata[xmax][ymin] * frac + probedata[xmax][ymax] * (1 - frac);

		#interpolate along X
		frac = xmax - x;
		#print str(frac) + " towards x=" + str(xmin) + "; x=" + str(x)
		depthadjust = frac * d1 + (1-frac) * d2;
		depth = BASE_DEPTH + depthadjust
		print "depth=" + str(depth) + ", adjusted by " + str(depthadjust)

		LINE = "G01 Z"+str("%.5f"%numpy.around(depth,decimals=5))+" "+feed+" ( plunge. )\n";		
	
	#Getting ready for a plunge
	#Set the x and y variables, to know where to read the Z offset from		
	elif "G00 X" in LINE:
		modplunge = 1;
		XY = LINE.split(" ");
		x = (float(XY[1].strip("X")) - xoffset)/pxstep;
		y = (float(XY[2].strip("Y")) - yoffset)/pystep;

	#Modifying a milling line
	elif LINE[0] == "X":
		x,y = LINE.split();
		x = float(x.strip("X"));
		y = float(y.strip("Y"));
		xidx = x2idx(x)
		yidx = y2idx(y)
		xmin = numpy.clip(int(math.floor(xidx)), 0, npx-1)
		xmax = numpy.clip(int(math.ceil(xidx)), 0, npx-1)
		ymin = numpy.clip(int(math.floor(yidx)), 0, npy-1)
		ymax = numpy.clip(int(math.ceil(yidx)), 0, npy-1)
		#interpolate along Y
		frac = (ymax*pystep - y) / pystep;
		d1 = probedata[xmin][ymin] * frac + probedata[xmin][ymax] * (1 - frac);
		d2 = probedata[xmax][ymin] * frac + probedata[xmax][ymax] * (1 - frac);

		#interpolate along X
		frac = (xmax*pxstep - x) / pxstep;
		depth = BASE_DEPTH + frac * d1 + (1-frac) * d2;

		LINE = LINE.strip("\n") + " Z"+str("%.5f"%numpy.around(depth,decimals=5))+"\n";

	outfile.write(LINE);

infile.close();
outfile.close();

