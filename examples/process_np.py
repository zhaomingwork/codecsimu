# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
##
## Description:
## Copyright 2024. All Rights Reserved.
## Author: Zhao Ming (zhaomingwork@qq.com)
##

import numpy as np
import torch
 
import codecsimu
import argparse

import soundfile 

 


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, help='File to procecss', default='test.wav')
    parser.add_argument('--output_file', type=str, help='Output file', default='out.wav')
    parser.add_argument('--codecs_bitrates', type=str, help='Output file', default='6.3k')
    
    parser.add_argument('--codecs_type', type=str, help='Output file', default='g723_1')
    parser.add_argument('--out_samplerate', type=str, help='Size of a time dropout sequence', default='16000')

    args = parser.parse_args()
    
 
 

    return args

if __name__ == '__main__':
    args = get_args()
    
    democodecs=codecsimu.CodecsCommnadGenerator(args.codecs_type,args.codecs_bitrates,args.out_samplerate,codec_sample_rate='8000')
    
    democodecs.set_ffmpeg_path("/tools/ffmpeg/ffmpeg-git-20220422-amd64-static/ffmpeg")
    demosimu=codecsimu.SimuCodector(democodecs)
    
    pcmdata,rate=soundfile.read(args.input_file)
    in_info={"type":"numpy","data":pcmdata}
    out_info={"type":"numpy"}
    
    theout=demosimu(in_info,out_info)
    
    soundfile.write("numpyout.wav",theout,16000)
    
    print("pcmdata shape",pcmdata.shape,"out shape",theout.shape)
    
     
    
    
 
