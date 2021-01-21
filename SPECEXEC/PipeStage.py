import numpy as np
import pandas as pd

class FetchUnit():

    def __init__(self, size=3):
        self.FB = ['']
        self.FBsize = size

    def fetch(self, inputStream):

        if len(self.FB) != self.FBsize:
            line = inputStream.readline()
            if line=='' and '' in self.FB:
                return
            self.FB.append(line)


class DecodeUnit():

    def __init__(self):
        self.DB = None
        self.DSB = None

    def decode(self, FB):
        
        if self.DSB is not None:
            return FB
        if FB[0]=='':
            FB.pop(0)
            return FB
        
        instruction = FB.pop(0)
        line = instruction.split()

        instruction = line[13]
        dest = int(line[4])
        R1 = int(line[2])
        R2 = int(line[3])
        imm = int(line[8])  

        self.DSB = {'op':instruction, 'src1':R1, 'src2':R2, 'dest':dest, 'imm':imm}
        return FB



class TOMExecuteUnit():

    def __init__(self, TomasuloHW, ISA):

        self.TOMUNIT = pd.read_csv(TomasuloHW,header=None).values
        self.OPTAG = pd.read_csv(ISA, header=None).values
        self.TOMTABLE = np.concatenate( [ [self.TOMUNIT[:,0]], -1*np.ones([8,len(self.TOMUNIT[:,0])], dtype=np.int32) ], axis=0).T
        self.TOMUNIT = { r[0]:r[1:] for r in self.TOMUNIT}
        self.OPTAG = { k:v for k,v in self.OPTAG }
        self.TOMTABLE[:,2] = False
        self.TOMTABLE[:,3] = ''
        self.REGFILE = ['']*64
        self.EB = None
        
    def execute(self, DB, clk):
        
        if DB is not None:
            if DB is not None:
                op = DB['op']
                src1 = DB['src1']
                src2 = DB['src2']    
                dest = DB['dest']
                imm = DB['imm']   
                tag = self.OPTAG[op]

                for r in self.TOMTABLE:
                    if tag in self.TOMUNIT[r[0]][1] and r[2]==False:
                        DB = None
                        r[1] = self.TOMUNIT[r[0]][0]
                        r[2], r[3] = True, op
                        r[4] = imm if src1==-1 else src1                    
                        r[5] = imm if src2==-1 else src2
                        if r[4]!=imm and self.REGFILE[src1]!='' :
                            r[7] = self.REGFILE[src1]
                        if r[5]!=imm and self.REGFILE[src2]!='' :
                            r[8] = self.REGFILE[src2]
                        if dest!=-1:
                            self.REGFILE[dest] = r[0]
                            r[6] = dest
                        break

        for ri in self.TOMTABLE:
            if ri[2]==True:
                if ri[7]==-1. and ri[8]==-1.:
                    ri[1]-=1
            if ri[1]==-1.:
                ri[2], ri[3] = False, ''
                for rj in self.TOMTABLE:
                    if rj[7]==ri[0]:
                        rj[7], rj[4] = -1., ri[6]
                    if rj[8]==ri[0]:
                        rj[8], rj[5] = -1., ri[6]
                self.REGFILE[int(ri[6])]=''
                self.EB = int(ri[6])
                ri[4:]=-1.

        return DB


class ExecuteUnit():

    def __init__(self, time=2):
        self.EXECTIME = time
        self.EXECBUSY = False
        self.STRT = 0
        self.EB = None
        self.WRITEREG = None
        self.ESB = None

    def execute(self, DB, clk):
        if (DB is not None) and (not self.EXECBUSY):
            print('Set New Exec')
            self.WRITEREG = DB
            DB = None
            self.STRT = clk
            self.EXECBUSY = True

        if clk-self.STRT == self.EXECTIME:
            self.STRT = 0
            self.EXECBUSY = False
            self.ESB = self.WRITEREG 

        return DB
