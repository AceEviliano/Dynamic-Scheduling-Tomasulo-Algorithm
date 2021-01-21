import pandas as pd
import numpy as np
from PipeStage import FetchUnit, DecodeUnit, ExecuteUnit, TOMExecuteUnit

class Clock():
    
    def __init__(self):
        self.clock=0
    
    def clocktick(self):
        self.clock+=1

    def reset(self):
        self.clock=0


class Pipeline():
    
    """
    Pipeline class sets up the 4 pipeline units:
    Fetch, Decode, Execute and Write Back.

    The Write Back unit unlike other stages is hard implemented
    into the pipeline class, this can be later changed to include
    a pieline stage. It also holds the clock for every pipeline. 
    The clock in the pipeline can be used for synchronization of 
    pipeline stages.
    """

    def __init__(self, FU, DU, EU):
        
        """
        Takes in Fetch, Decode and Execute Units of the pipeline for
        initializing the pipeline.
        """

        self.Fetch = FU
        self.Decode = DU
        self.Execute = EU
        self.clock = Clock()
        self.END = False

    def update(self):
        """
        Method updates the current state buffers with contents of the 
        buffer at previous cycle.
        """
        
        if self.Decode.DB is None:
            self.Decode.DB = self.Decode.DSB
            self.Decode.DSB = None

    def fetch(self, inputstream):
        self.Fetch.fetch(inputstream)

    def decode(self):
        self.Fetch.FB = self.Decode.decode(self.Fetch.FB)

    def execute(self):
        self.Decode.DB = self.Execute.execute(self.Decode.DB, self.clock.clock)

    def write(self):

        if len(self.Fetch.FB) == 0:
            if self.Decode.DB is None and self.Decode.DSB is None:

                if isinstance(self.Execute, TOMExecuteUnit):
                    if not np.any(self.Execute.TOMTABLE[:,2]):
                        self.END=True

                if isinstance(self.Execute, ExecuteUnit):
                    self.END=True

    def showTrace(self):
        
        print()      
        print(f'(Clock {self.clock.clock})'+'='*50)

        print('\nFetch Buffer :\n')
        for line in self.Fetch.FB:
            print(line)

        print('-'*60)

        print('\nBuffer State :\n')
        print(self.Decode.DSB)

        print('-'*60)

        if isinstance(self.Execute, TOMExecuteUnit):
            print('\nTomasulo Table\n')
            print(self.Execute.TOMTABLE)
            print('\nRegister Allocation\n')
            print(self.Execute.REGFILE)

        elif isinstance(self.Execute, ExecuteUnit):
            print('\nExecute Buffer:\n')
            print(self.Execute.EB)

        print('-'*60)

        if len(self.Fetch.FB) == 0:
            print('write verified FB none')
            if self.Decode.DB is None and self.Decode.DSB is None:
                print('write verified DB and DSB none')

                if isinstance(self.Execute, TOMExecuteUnit):
                    if not np.any(self.Execute.TOMTABLE[:,2]):
                        print('write verified FunctionalUnits none')

                if isinstance(self.Execute, ExecuteUnit):
                    print('write verified FunctionalUnits none')
                    

        print("="*60)
        print()      