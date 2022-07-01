import numpy as np
import math
import pylab as pl

from collections import namedtuple

class datafmt_error(Exception):
    pass



class adcarray:

    end_of_tracklet = int('0x10001000',0)

    
#Defining the initial variables for class    
    def __init__(self):
        self.data=np.zeros((16,144,30))
        self.clean_data=np.zeros((16,144,30))

        self.HC_header=0
        self.HC1_header=0
        self.ntb=30
        self.MCM_header=0

        self.line=-1
        self.sfp=0

        self.debug = 0
 
#Extracting next line of information       
    def get_dword(self,dic):
        '''
        Parameter: dic = Dictionary element
        Extracts next element in the dictionary
        '''
        self.line+=1
        if self.line >= dic['datablocks'][self.sfp]['raw'].size:
            raise datafmt_error()

        return dic['datablocks'][self.sfp]['raw'][self.line]


#Extracting the HC header
    def read_hc_header(self,dic):
        '''
        Parameters: rdr = Rawreader variable
        Function reads all Half chamber headers
        '''

        hc0 = self.get_dword(dic)

        self.HC_header=hc0
	
	#Extract information from HC header

        if self.debug > 5:
            print('HC_header: ',self.HC_header)

        self.major = (hc0 >> 24) & 0x7f 
        self.minor = (hc0 >> 17) & 0x7f 
        self.nhw   = (hc0 >> 14) & 0x7
        self.sm    = (hc0 >>  9) & 0x7
        self.layer = (hc0 >>  6) & 0x1f
        self.stack = (hc0 >>  3) & 0x3
        self.side  = (hc0 >>  2) & 0x1

        self.sidestr = 'A' if self.side==0 else 'B'

        
        hw=(int(hex(self.HC_header)[0:10],0) >> 14) & 0x7

        #Read additional header words
        if hw >= 1:
            hc1 = self.get_dword(dic)
            self.HC1_header=hc1

            ntb         = (hc1 >> 26) & 0x3f
            bc_counter  = (hc1 >> 10) & 0xffff
            pre_counter = (hc1 >>  6) & 0xF
            pre_phase   = (hc1 >>  2) & 0xF
            
            #print('HC1_header: ',self.HC1_header)

            self.ntb=(int(hex(self.HC1_header)[0:10],0)>>26)&0x3F
            for i in range(1,hw):
                check=self.get_dword(dic)


        if hw >= 2:
            hc2 = self.get_dword(dic)
        
        if hw >= 3:
            hc3 = self.get_dword(dic)

        if self.debug > 5:
            print ( "HC %02d_%d_%d%s: fmt %d.%d - %d TBs - %d %d hdr words" %
                    (self.sm,self.stack,self.layer,self.sidestr,
                     self.major,self.minor,
                     self.ntb, self.nhw, hw) )




    def extract_mcm_data(self,dic):

        ''' 
        Parameter:rdr = Rawreader variable
        Extracts MCM header and all the mcm data that follows under the header
        '''

        self.mcmhdr = self.get_dword(dic)
        self.MCM_header=self.mcmhdr

        if self.major & (1<<5):
            self.adcmask = self.get_dword(dic)
        else:
            self.adcmask = 0x01FFFFFC

        #print ("  MCM hdr:   0x%08x" % self.mcmhdr)
        #print ("  ADC mask:  0x%08x" %self.adcmask)

            
        #Cycle throught 21 channels per mcm
        for ch in range(0,21):
    
            if (self.adcmask & (1<<(ch+4))) == 0:
                continue

            if self.debug > 8:
                print ("  reading ADC %d (0x%08x)" % (ch, (1<<(ch+4))))
                
            #Cycle through number of words (timebin) associated with the mcm
            for i in range(0,adcarray.N_words(self.ntb)):
                
                dword=self.get_dword(dic)
                tb=i*3
                
                
                if ch>=0 and ch < 18:
                #Extract and save data in 3D array
                    self.read_dword(dword,tb,ch)












    def analyse_event(self,dic):
        '''
        Parameter: rdr = Rawreader variable
        Extracts all the data from event in file and reads into 3D data cube: self.data
        '''

        self.data=np.zeros((16,144,30))
        for sfp in [0,1]:
            self.sfp=sfp
            self.line=-1
            c=0
            while c!=2:
                line=self.get_dword(dic)
#                print(hex(line))

                if line == adcarray.end_of_tracklet:
                    c+=1


        #Read HC_header:

            self.read_hc_header(dic)


        #Cycle

            for rob in range(0,3):
                #Cycle through mcm's on read_ou_board
                for mcm in range(0,16):
                    self.extract_mcm_data(dic)

                    #print(self.pos_ex())


	#Takes dword and reads information into a 3D cube
    def read_dword(self,dword,tb,ch):
        '''
        Extract information from dword, and read it into the 3D data cube
        Parameters:
                dword=MCM_data dword
                tb=time_bin the dword is associated with
                ch=channel from where the data comes from
        writes: self.data 3D cube
        '''
        #Find position
        col,row=self.pos()

        #print(col,row)

        #from dword, write into self.data
        self.data[row][col*18+ch][tb+2]=(dword>>22)& 0x3ff
        self.data[row][col*18+ch][tb+1]=(dword>>12)& 0x3ff
        self.data[row][col*18+ch][tb]=(dword>>2)& 0x3ff


#        print(self.pos(),col*18+ch)





    def get_adc(self,row,col,ch,tb):

        '''
        Works on a 12x144xtb 3D data cube:
                row: dimension 0-11 (y-direction of adc)
                col: dimension 0-7 (x-direction of adc)
                ch: channel number of adc
                tb:  # of timebin
        returns value in data cube
        '''

        return self.data[row][col*18+ch][tb]


#Extract position form MCM_header
    def pos_ex(self):

        '''
        Extracts read_out_board and adc position from mcm_header
        returns: read_out_board,MCM_position
        '''

        ROB=(int(hex(self.MCM_header),0)>>28) & 0x7
        MCMpos=(int(hex(self.MCM_header),0)>>24) & 0xF

        return ROB,MCMpos

#X-coordinate
    def xc(self,ROB,MCMpos):

        '''
        Parameters: ROB = read_out_board
                MCMpos = MCM_position
        Returns x-coordinate of position on the trd board
        '''

        return 7-(4*(ROB%2) + MCMpos%4)

#Y-coordinate
    def yc(self,ROB,MCMpos):

        '''
        Parameters: ROB = read_out_board
                MCMpos = MCM_position
        Returns y-coordinate of position on the trd board
        '''
        
        return 4*(math.floor(ROB/2)) + math.floor(MCMpos/4)


#Covert Readout board and ADC to X/Y-pos
    def conv(self,ROB,MCMpos):
        '''
        Converts read_out_board and mcm to x and y positions
        Parameters:        
                    ROB=Read_ot_board
                    MCMpos=mcm position
        returns: x,y position
        '''
        col=self.xc(ROB,MCMpos)
        row=self.yc(ROB,MCMpos)
        
        return col,row    #(x,y)

#Find position on board
    def pos(self):
        '''
        Finds x,y position from MCM_header
        returns x,y coordinates
        '''
        ROB,MCMpos = self.pos_ex()
        #x,y = self.conv(ROB,MCMpos)
        #print("%02d:%02d -> %02d/%03d     MCM hdr: %08x" % (ROB,MCMpos,x,y,self.MCM_header))
        return self.conv(ROB,MCMpos)

#Find Number of words from Number of timebins
    def N_words(Nt):
        '''
        Calculates the number of dwords, given the number of time_bins
        Parameter: Nt = Number of time_bins
        '''
        return math.floor((Nt-1)/3) + 1




    def reset(self):
        '''
        Resets initial varaiables associated with the adcarray data
        '''

        self.data=np.zeros((16,144,30))

        self.HC_header=0
        self.HC1_header=0
        self.ntb=0
        self.MCM_header=0

Footer
© 2022
