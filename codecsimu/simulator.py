# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
##
## Description:
## Copyright 2024. All Rights Reserved.
## Author: Zhao Ming (zhaomingwork@qq.com)
##
import subprocess
import numpy as np
import soundfile
import random


class CodecsRule:
     def __init__(self, codecstype,codec_bitrates_list,codec_sample_rate):
          self.codecstype=codecstype
          self.codec_bitrates_list=codec_bitrates_list
          self.codec_sample_rate=codec_sample_rate
          

class CodecsRuleCheck:
     def __init__(self):
         self.all_rule_map={}
         mp3rule=CodecsRule("mp3",None,None)
         self.all_rule_map['mp3']=mp3rule
         opusrule=CodecsRule("ogg",['4.5k','5.5k','7.7k','9.5k','12.5k','16.0k','32.0k'],8000)
         self.all_rule_map['ogg']=opusrule
         gsmrule=CodecsRule("gsm",['13k'],8000)
         self.all_rule_map['gsm']=gsmrule
         
     def check_codecs(self,odectype,codec_bitrates,codec_sample_rate):
           if odectype in self.all_rule_map.keys():
               therule=self.all_rule_map[odectype]
               if  therule.codec_bitrates_list is not None and not codec_bitrates in therule.codec_bitrates_list:
                    raise RuntimeError('codec_bitrates ' +str(codec_bitrates) +' is not right, only support '+str(therule.codec_bitrates_list))
               if  therule.codec_sample_rate is not None and not str(codec_sample_rate).strip() == str(therule.codec_sample_rate).strip():
                    raise RuntimeError('codec_sample_rate ' +str(codec_sample_rate) +' is not right, only support '+str(therule.codec_sample_rate))
           return 
     
        
class CodecsCommnadGenerator:
    """CodecsCommnadGenerator.
    generate codecs commands for ffmpeg 
    """
    def __init__(self, codectype,codec_bitrates,out_sample_rate,codec_sample_rate='16000',enable_rule_check=False):
        """__init__.
        :param codectype: the codecs type used for simulation, such as 'mp3', 'g723_1'
        :param codec_bitrates: the bitrates of the codecs
        :param out_sample_rate: the signal sample rate for output, it will be single channel  pcm wav
        """
    
    
        self.codectype = codectype
        self.bitrates = codec_bitrates
        self.outsamplerate = out_sample_rate
        self.codec_sample_rate=codec_sample_rate
        self.theffmpegpath="ffmpeg"
        
        if enable_rule_check==True:
           thecheck=CodecsRuleCheck()
           thecheck.check_codecs(codectype,codec_bitrates,codec_sample_rate)
    
    
    def set_ffmpeg_path(self,ffmpeg_path):
        self.theffmpegpath=ffmpeg_path
    
    def ffmpeg_command_generator(self):
        """ffmpeg_command_generator.
        will return two commands, ffmpeg_wav_to_target,ffmpeg_target_to_outwav
        ffmpeg_wav_to_target,this commands use ffmpeg to transfer pcm wav data to simulated codecs type
        ffmpeg_target_to_outwav,this commands use ffmpeg to transfer simulated codecs back to pcm wav
        """
        if self.codectype=="mp3":
               codec="libmp3lame"
               ftype="mp3"
               codecsamplerate=self.codec_sample_rate
        if self.codectype=="g723_1":
               codec="g723_1"
               ftype="wav"
               codecsamplerate="8000"
        if self.codectype=="g722":
               codec="g722"
               ftype="wav"
               codecsamplerate="16000"
        if self.codectype=="gsm":
               codec="libgsm"
               ftype="gsm"
               codecsamplerate="8000"
        if self.codectype=="amr":
               codec="libopencore_amrnb"
               ftype="amr"
               codecsamplerate="8000"
        
        if self.codectype=="ogg":
               codec="libopus"
               ftype="ogg"
               codecsamplerate=self.codec_sample_rate
        ffmpeg_wav_to_target = [self.theffmpegpath, "-i", '-',  "-ab", self.bitrates, "-acodec", codec, "-ac", "1", "-ar", codecsamplerate,  "-f", ftype , "pipe:1"]
        ffmpeg_target_to_outwav = [self.theffmpegpath, "-i", '-',  "-acodec", "pcm_s16le", "-ac", "1", "-ar", self.outsamplerate,  "-f", "wav", "pipe:1"]
        return ffmpeg_wav_to_target,ffmpeg_target_to_outwav
        
class SimuCodector:
    def __init__(self,codecscom):
       
        self.codecscom=codecscom
        self.fmpeg_wav_to_target,self.ffmpeg_target_to_outwav=self.codecscom.ffmpeg_command_generator()
        
    
 
    
    def genHeader(self,sampleRate, bitsPerSample, channels, samples):
        datasize = len(samples) * channels * bitsPerSample // 8
        o = bytes("RIFF",'ascii')                                                
        o += (datasize + 36).to_bytes(4,'little')                                
        o += bytes("WAVE",'ascii')                                               
        o += bytes("fmt ",'ascii')                                               
        o += (16).to_bytes(4,'little')                                           
        o += (1).to_bytes(2,'little')                                            
        o += (channels).to_bytes(2,'little')                                     
        o += (sampleRate).to_bytes(4,'little')                                  
        o += (sampleRate * channels * bitsPerSample // 8).to_bytes(4,'little')  
        o += (channels * bitsPerSample // 8).to_bytes(2,'little')               
        o += (bitsPerSample).to_bytes(2,'little')                               
        o += bytes("data",'ascii')                                              
        o += (datasize).to_bytes(4,'little')                                   
        return o
    def numpy2wavbuf(self,numpydata):
        filepcm = np.int16(numpydata/np.max(np.abs(numpydata)) * 32767)
        filepcm=b''.join(filepcm)
        wavhead=self.genHeader(16000, 16, 1, filepcm)
        filebuf=wavhead+filepcm
        return filebuf
        
    def pcm2numpy(self,byte):
        #skip the wav head 44 bytes
        sig=np.frombuffer(byte[44:],dtype=np.int16)
        signal = np.asarray(sig)
        signal= signal.astype(np.float32) / 32768
        return signal
        
    def __call__(self, in_info, out_info=None):
        """__call__.
        :param in_info: input data information. it is a dict type witch has two keys, one is 'type' that would be set to 'file' or 'numpy' 
        
        :param out_info: output data information. it is a dict type witch has two keys, one is 'type' that would be set to 'file' or 'numpy' 
        returns: pcm wav in numpy float type. when out_info set to file type, it will write the single channel  pcm wav file to set path
        """
        if not 'type' in in_info:
            raise RuntimeError('in_info miss the key of type')
        
        if in_info['type']=="file":
              with open(in_info['path'],"rb") as file:
                  filebuf=file.read()[:]
        elif in_info['type']=="numpy":
 
             filebuf=self.numpy2wavbuf(in_info['data'])
    
            
        
        pipe_to = subprocess.Popen(self.fmpeg_wav_to_target,
                       stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
        codecoutbuf, err = pipe_to.communicate(filebuf)
        if str(err).find("Error")>=0 or str(err).find("Unknown")>=0 or str(err).find("Invalid")>=0:
            print("codecoutbuf err",err)
            print("execute cmd ",self.fmpeg_wav_to_target)
        pipe_out = subprocess.Popen(self.ffmpeg_target_to_outwav,
                       stdin=subprocess.PIPE,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)

 
        out_buf, err = pipe_out.communicate(codecoutbuf)
        if str(err).find("Error")>=0 or str(err).find("Unknown")>=0 or str(err).find("Invalid")>=0:
            print("out_buf err",err)
            print("execute cmd ",self.ffmpeg_target_to_outwav)
        if not out_info is None and out_info['type']=="file":
             with open(out_info['path'],"wb") as file:
                   file.write(out_buf)
        
        out_buf=self.pcm2numpy(out_buf)
        
        return out_buf
