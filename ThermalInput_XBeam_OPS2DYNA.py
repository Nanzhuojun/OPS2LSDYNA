# This python is writen by NAN Zhuojun (zhuojun.nan@connect.polyu.hk) & DAI Xu (xu.dai@burohappold.com) to create Thermal input LS-DYNA Keyword File
# OPS2DYNA: convert from .out (OpenSEES output) to .key (LS-DYNA input)
# This case is the baseline scenario based on the BST/FRS 1993 Fire Test Series
# This script is used for XBeam

import glob
import numpy as np
import pandas as pd
import re

# np print options and pd display options
np.set_printoptions(threshold=np.inf)
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('max_colwidth', None)
#pd.set_option('display.precision', 4)

# Setup constants
start_Time = 0.0 # Time for starting simulation, default "0.0"
initial_Temperature = 20  # ambient temperature, default 20 Celsius
data_string_length = 6  # length of the input string (not including "."), i.e. "20.0000"
off_set_Time = 4  # offset of time, used in LS-DYNA simulation, waiting for the model to be stable

# To create a new file for LS-DYNA thermal input .key file
f = open('Thermal_XBeam_DefineCurve.key', 'w+')
f.write('*KEYWORD\n'
        '$> LS-DYNA version: R9.0\n'
        '$> \n'
        '$> end_saved_comments\n'
        '$\n'
        '$\n'
        '$ ============\n'
        '$ DEFINE cards\n'
        '$ ============\n'
        '$\n')

# Read through all OpenSees generated .out files in the directory, then loop over
for XBeam_HT in glob.glob('HT_SIFXBeam_*_1_1.out'):
    XBeam_HT_name = str(XBeam_HT) # convert to string

    # print(XBeam_HT_name) # for debug and check

    XBeamNum = re.findall(r'm_(.+?)_', XBeam_HT_name) # find out the number of XBeam, predefined

    for XBeamNum in XBeamNum: # convert the format of XBeamNum
        print("XBeam"+XBeamNum) # The number of XBeam, i.e. XBeam1, XBeam2 ..., for debug and checking the convert process
        NodeTempCurve_Num_First_array = np.arange(1086, 1220, 15) # Define the number of first Temperature history curve for each XBeam, predefined as shown in illustration
        NodeTempCurve_Num_First = NodeTempCurve_Num_First_array[int(XBeamNum)-1] # The number of first Temperature history curve for each XBeam (i.e. temperature curve at Node1) selected according to the number of XBeam

        print("The number of temperature history curve at Node1 of XBeam"+XBeamNum+": "+str(NodeTempCurve_Num_First)) # for debug and checking the convert process


    # Use numpy to load the data contained in the .out file
    nd_Array_Data = np.loadtxt(XBeam_HT)

    # Offset of time with 4s
    # columns= ['Time', 'Node1', 'Node2', 'Node3', 'Node4', 'Node5', 'Node6', 'Node7', 'Node8', 'Node9', 'Node10', 'Node11', 'Node12', 'Node13', 'Node14', 'Node15']
    Time_0_Temp = pd.DataFrame([[0.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]]) # add ambient Temp (20C) at Time 0s
    Time_4_Temp = pd.DataFrame([[4.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0, 20.0]]) # add ambient Temp (20C) at Time 4s
    XBeamTemp_or = pd.DataFrame(nd_Array_Data) # original XBeamHT Temperature of OpenSEES output
    XBeamTemp_or.iloc[:, 0] = np.arange(4.01, 26.49, 0.01) # reset time
    Time_0_4_Temp = Time_0_Temp.append(Time_4_Temp, ignore_index = True)
    XBeamTemp = Time_0_4_Temp.append(XBeamTemp_or, ignore_index = True) # combine ambient Temp into original SlabHT Temperature of OpenSEES output

    XBeamTemp.insert(loc=16, column='Tag1', value=[' '*12 for i in range(XBeamTemp.shape[0])]) # reset XBeamTemp array with Tag1 column '            '(i.e. spacing), prepare for next step to make sure the format of output
    XBeamTemp.insert(loc=17, column='Tag2', value=[' '*8 for i in range(XBeamTemp.shape[0])])  # reset XBeamTemp array with Tag2 column '         '(i.e. spacing), prepare for next step to make sure the format of output

   # print(XBeamTemp)

    NodeNum_Lis = [1, 2, 3, 4, 5, 8, 13]

    for i in NodeNum_Lis: # Node Temperature columns in XBeamTemp array, loop inside for each XBeam (i.e. Nodes in the XBeam)
        # this range could be change with different node in the cross-section
        NodeTemp = XBeamTemp.iloc[:, [16, 0, 17, i]] # prepared the columns (Tag1, Tag2) in SlabTemp is used here, format of output "           Time          NodeTemperature"
        NodeTemp = NodeTemp.to_string(index=False, header=False)  # output without index and header

        NodeNum = 'Node_' + str(i)
        NodeTempCurve_Num = str(NodeTempCurve_Num_First + i - 1) # Define the number of Temperature history curve for each node (based on different XBeam number)

        f.write('$\n'
                '$\n'
                '*DEFINE_CURVE_TITLE\n' +
                XBeam_HT_name + NodeNum  + '\n'
                '$:\n'
                '$: Cross-reference summary for Load-curve ' + NodeTempCurve_Num + '\n'
                '$: -----------------------------------------------\n'
                '$:\n'
                '$: Load thermal variable beam ' + str(int(XBeamNum) + 10) + ' : Temperature vs time\n'
                '$: X axis : Time                       (Units: Time)\n'
                '$: Y axis : Temperature                (Units: Temperature)\n'
                '$:\n'
                '$: Load thermal variable beam ' + str(int(XBeamNum) + 10) + ' : Temperature vs time\n'
                '$: X axis : Time                       (Units: Time)\n'
                '$: Y axis : Temperature                (Units: Temperature)\n'
                '$:\n'                                                            
                '$: Usage: Transient analysis\n'
                '$:\n'
                '$\n'
                '$ X axis :\n'
                '$ Y axis :\n'
                '$ Label : ' + XBeam_HT_name + NodeNum  + '\n'
                '$\n'
                '      ' + NodeTempCurve_Num + '         0       1.0       1.0       0.0       0.0         0         0\n')

        f.writelines(NodeTemp) # write node temperature history line by line for each node
        f.write('\n')

print('Thermal data converting finished! (OPS TO LS-DNA)')
f.close()

        #print(NodeTemp)
