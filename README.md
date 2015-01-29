# cnc-pcb-depth-probe
Project to improve the results of milling PCBs

Milling PCBs is kind of a pain. You (or at least I) use conical bits to isolate the traces and, as such, variations in 
the milling depth will cause variations in the isolation path width. At the same time, copper-clad board is bloody hard 
to hold flat. Not only is the board itself not perfectly planar, but clamping it down invariably results in it bowing 
outward away from the clamps. Put these two things together, and you have a recipe for poor results.

This project tackles the issue on two fronts. First, it provides gcode to depth-probe a copper-clad board, giving you 
hard values of the height of the milling surface at different points. Second, it provides a Python script to apply those 
data points to a PCB milling gcode file (assuming it was generated with pcb2gcode, that is). By compensating the milling 
depth for the imperfections in the board and clamping, it becomes possible to mill much more consistent traces.

My workflow looks like:

-Lay out PCB in KiCad
-Export to gerber
-Use pcb2gcode to convert to gcode
-Clamp down copper-clad board on CNC mill
-Modify pcb-probe.ngc to configure the probing
-Run pcb-probe.ngc to get depth data
-Modify patch-gcode.py with the appropriate filenames and whatnot
-Run patch-gcode.py to depth-compensate my gcode
-Run new gcode to etch PCB


This works for using LinuxCNC as your CNC controller- it should (mostly) work elsewhere, though I haven't tested.
