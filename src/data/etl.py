import pandas as pd
import glob
import os
import itertools

from preprocess import isolate_vpn
from preprocess import unpack
from preprocess import packet_data


def etl(source_dir, out_dir):
    
    if not os.path.exists(source_dir):
        print('Using symlink')
        #need to figure out why python os.symlink didn't work but ln -s worked
        symlink_dir = "/teams/DSC180A_FA20_A00/b05vpnxray/GoodData"

        os.symlink(symlink_dir, source_dir)  
        
    if 'test' in source_dir:
        print('Using Testing Data')
        file_lst = glob.glob(source_dir + '*')
    else:
        os.system('ln -s /teams/DSC180A_FA20_A00/b05vpnxray/GoodData /data/raw')
        #Symlinking data from GoodData directory
        print('Symlinking data from GoodData directory') 
        datafiles = glob.glob('data/raw/GoodData/*')
        file_lst = [l for l in datafiles if 'novpn' not in l]

    #remove files
    for f in glob.glob(os.path.join(out_dir, '*')):
        os.remove(f)

    for filename in file_lst:
        df = pd.read_csv(filename)
        df = isolate_vpn(df)
        df = df.apply(packet_data, axis=1)
        df = pd.DataFrame(df.sum(), columns = ['time','size','dir']).astype(int)
        df = df.sort_values('time')
        df['dt_time'] = pd.to_timedelta(df.time - df.time[0], 'ms')
        df = df.set_index('dt_time')
        #print(df)



        filename = os.path.basename(filename)
        df.to_csv(os.path.join(out_dir, 'preprocessed-'+filename))