import sys
from numba import jit, cuda
from allennlp.commands.elmo import ElmoEmbedder
#elmo = ElmoEmbedder(
#    options_file='./elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json',
#    weight_file='./elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5'
#)
#s1=['I','have','books']
#v1=elmo.embed_sentence(s1)
#print(v1[2])
#print(v1[2].mean(axis=0))
#print(v1[2].max(axis=0))

def get_elmo_avg_max_pooling(br_fin, avgp_fout, maxp_fout,cudaD):
    avgL=[]
    maxL=[]

    elmo = ElmoEmbedder(options_file='./elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json', weight_file='./elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5',cuda_device=cudaD)
    for br in br_fin.readlines():
        if(len(br.strip("\n").strip().split(" "))<=1):continue
        bid, text=br.strip("\n").strip().split(" ",1)
        text=text.split(" ")
        #elmo = ElmoEmbedder(options_file='./elmo_2x4096_512_2048cnn_2xhighway_5.5B_options.json', weight_file='./elmo_2x4096_512_2048cnn_2xhighway_5.5B_weights.hdf5',cuda_device=cudaD)
        v1=elmo.embed_sentence(text)
        avgv=v1[2].mean(axis=0)
        maxv=v1[2].max(axis=0)

        avgv = ['{:.7f}'.format(i) for i in avgv.tolist()]
        maxv = ['{:.7f}'.format(i) for i in maxv.tolist()]
        avgv=str(bid) + "," + " ".join(list(map(str, avgv)))
        maxv=str(bid) + "," + " ".join(list(map(str, maxv)))
        avgL.append(avgv)
        maxL.append(maxv)

    avgp_fout.write("\n".join(avgL)+"\n")
    maxp_fout.write("\n".join(maxL)+"\n")

if __name__ == '__main__':
    brFin = sys.argv[1] #format:bid, token1 token2 ... tokenN
    avgpFout = sys.argv[2] #the average pooling output file
    maxpFout = sys.argv[3] #the max pooling output file
    cudaD = int(sys.argv[4])
    get_elmo_avg_max_pooling(open(brFin,'r'), open(avgpFout,'w'), open(maxpFout,'w'),cudaD)
