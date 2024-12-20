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

 

 


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, help='File to procecss', default='test.wav')
    parser.add_argument('--output_file', type=str, help='Output file', default='out.wav')
    parser.add_argument('--codecs_bitrates', type=str, help='Output file', default='13k') #  6.3k   13k 4.5k
    
    parser.add_argument('--codecs_type', type=str, help='Output file', default='amr')   # g723_1  gsm ogg
    parser.add_argument('--out_samplerate', type=str, help='Size of a time dropout sequence', default='16000')

    args = parser.parse_args()
    
 
 

    return args

if __name__ == '__main__':
    args = get_args()
    
    democodecs=codecsimu.CodecsCommnadGenerator(args.codecs_type,args.codecs_bitrates,args.out_samplerate,codec_sample_rate='8000',enable_rule_check=True)
    
    democodecs.set_ffmpeg_path("/tools/ffmpeg/ffmpeg-git-20220422-amd64-static/ffmpeg")
    #democodecs.set_ffmpeg_path("/tools/ffmpeg/ffmpeg20220614/ffmpeg-4.2.1/ffmpeg")
    
    demosimu=codecsimu.SimuCodector(democodecs)
     
    in_info={"type":"file","path":args.input_file}
    out_info={"type":"file","path":args.output_file}
    theout=demosimu(in_info,out_info)
     
    
    
 
