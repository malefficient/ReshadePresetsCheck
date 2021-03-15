import sys
import re
import os
from collections import OrderedDict

##JC:TODO:Rather than compare every referenced fname to the input_dir and flagging duplicates, compare all the shader to all the other shaders (regardless of ini file references)
##TODO: Add fun color outputs
##TODO Implement make clean; make install-ish functionality (cleaning / regenerating a 'real' reshade-shaders directory inside CEMU

def usage():
    print("Usage: %s ReShadeSettings.ini shader_dir"% (sys.argv[0]))
    print("Usage: Defaults: ReShade.ini ./reshade-shaders")
    sys.exit(0)

def parse_args():
    ret = {}
    ret['input_fname']="./ReShade.ini"
    ret['input_shaderdir']="./reshade-shaders"
                
    argc=len(sys.argv)
    if (argc >=4):
        usage()
    if (argc == 3):
        ret['input_shaderdir']=sys.argv[2]
    if (argc >= 2):
        ret['input_fname']=sys.argv[1]
    return ret
        
       

def find_shaders(path, targets):
    file_list = []
    duplicates_l=[]
    ok_l=[]
    missing_l=[]
    #Iterate target directory, saving paths, fnames as we go
    for root,d_names,f_names in os.walk(path):
        for f in f_names:
            file_list.append((root, f))

    for t in targets:
        ##Return all tuples in file_list where second element in tuple is t. I.e. ('./reshade-shaders/Shaders/', 'Tonemap.fx')
        C = [item for item in file_list
            if item[1] == t]
        #not enough
        if len(C) == 0:
            missing_l.append(t)
        ##to many 
        if len(C) > 1:
            ok_l.append(C[0]) #Return first instance
            duplicates_l.append(t)   
        #Just right
        if len(C) == 1:
            ok_l.append(C)
        
    return  ok_l, duplicates_l, missing_l

def main():
    Args = parse_args()
    targets_l=[]

    #Create a list of (unique) shader fnames referenced by input f
    m=re.compile('\[.*\]')
    file = open(Args['input_fname'])
    D=OrderedDict.fromkeys(re.findall(m,file.read()))
    for f in D.keys():
        targets_l.append(f[1:-1]) 

    #Iterate over shader_dir. Track how many shaders exist/dont exist/fname collisions
    ok_l, duplicates_l, missing_l = find_shaders(Args['input_shaderdir'], targets_l)

    print("%s: %s complete" % (sys.argv[0], Args['input_fname']))

    print("%03d/%03d shaders located" % ( (len(ok_l), len(targets_l))))
    print("%03d filename collisions" % ( len(duplicates_l)))
    print("%03d missing " % ( len(missing_l)))

    if len(missing_l) > 0:
        print("##Warning: %d shaders could not be found." % (len(missing_l)))
        print(missing_l)
    if len(duplicates_l) > 0:
        print("##Warning: %d filename collisions." % (len(duplicates_l)))
        print(duplicates_l)

    sys.exit(0)

#Execute only if invoked as a script. 
if __name__ == "__main__":
    main()
