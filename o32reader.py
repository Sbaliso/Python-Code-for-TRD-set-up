import numpy 
import re
from datetime import datetime


#Define Class
class o32reader:

    #Initial state variables:
    def __init__(self,file_name):

        self.filename = file_name
        
        self.line_number=0
        self.linebuf = None

        self.HC_header=0

        self.ev_timestamp = None
        self.blk_sfp = None
        self.blk_size = None
        self.blk_unread = 0

    #Open file
    def __iter__(self):
        self.infile=open(self.filename, 'r')
        return self

    #Create dictionary    
    def __next__(self):

        rawevent = {}
        rawevent['datablocks'] = ()
        

        line = self.read_line()
        if not line:
            raise StopIteration
        
        if line != '# EVENT':
            #print ("Event not found: '%s'", self.lastline)
            raise Exception('file format', 'invalid file format')


        m = re.search('# *format version: *(.*)', self.read_line())

        if m.group(1) == '1.0':
            hdrfields = ('time stamp', 'data blocks')
        else:
            raise Exception('file format', 'unknown format version')
            

        for h in hdrfields:

            if h == 'time stamp':
                m = re.search('# *time stamp: *(.*)', self.read_line())
                
                rawevent['timestamp'] = datetime.strptime( m.group(1),
                                                           '%Y-%m-%dT%H:%M:%S.%f')

            elif h == 'data blocks':
                m = re.search('# *data blocks: *(.*)', self.read_line())
                nblk = int(m.group(1))

            else:
                raise Exception('FATAL', 'unknown header field')


        for i in range(nblk):

            blkdata = {}
            
            if self.read_line() != '## DATA SEGMENT':
                raise Exception('file format', 'invalid file format') 

            

            m = re.match('## *sfp: *(.*)', self.read_line())
            blkdata['sfp'] = int(m.group(1))

            m = re.search('## *size: *(.*)', self.read_line())
            blkdata['size'] = int(m.group(1))

            
            rawdata = numpy.zeros(blkdata['size'], dtype=numpy.uint32)
            for i in range(blkdata['size']):
                rawdata[i] = numpy.uint32(int(self.read_line(),0))


            blkdata['raw'] = rawdata

            rawevent['datablocks'] += (blkdata,)


        return rawevent



    def read_line(self):
        if self.linebuf is not None:
            tmp = self.linebuf
            self.linebuf = None
            return tmp
        else:
            self.line_number+=1
            self.lastline = self.infile.readline().rstrip()
            return self.lastline
        
Footer
