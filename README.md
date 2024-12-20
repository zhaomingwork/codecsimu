codecsimu use ffmpeg to simulate different audio codec process for train robust speech recognition model, especiallly for telephone 8k senario. 
the codecs include:
1. mp3
2. g132.1
3. ogg
4. gsm
5. g722
6. amr


Requirements
Linux or MacOS
pytorch >= 1.7
torchaudio >= 0.7
ffmpeg-4.4


Usage: see examples
    democodecs=codecsimu.CodecsCommnadGenerator(args.codecs_type,args.codecs_bitrates,args.out_samplerate,codec_sample_rate='8000')
    
    democodecs.set_ffmpeg_path("/tools/ffmpeg/ffmpeg-git-20220422-amd64-static/ffmpeg")
    demosimu=codecsimu.SimuCodector(democodecs)
     
    in_info={"type":"file","path":args.input_file}
    out_info={"type":"file","path":args.output_file}
    theout=demosimu(in_info,out_info)
	

 

License
MIT licensed
