#!/usr/bin/env python
import os
import argparse
from Bio import SeqIO


GROUPHOME = os.environ['GROUPHOME']

def main():
    #python ../inversionfix.py -r 4-0010.rdiff -v 4-0010-temp.vcf -q 4-0010.qdiff -f $GROUPHOME/data/genomes/4-0010.fasta -t 4-0010-temp.fasta
    parser = argparse.ArgumentParser(description='finds inversions and adds them to vcf output of biodiff',
                                     epilog='Runs nucmer and show-diff on fasta files to find inversions')
    parser.add_argument('-r', '--rdiff', help='dnadiff output, reference coordinates', default='out.rdiff')
    parser.add_argument('-q', '--qdiff', help='dnadiff output, query coordinates', default='out.qdiff')
    parser.add_argument('-v', '--vcf', help='temp vcf file', default='out-temp.vcf')
    parser.add_argument('-f', '--qfasta', help='query fasta file')
    parser.add_argument('-t', '--tfasta', help='temp fasta file', default='out-temp.fasta')
    args = parser.parse_args()

    #chromname = 'snps_indels|NC_001416.1|'
    chromname = '1'
    # parse args.rdiff and make args.vcf with just the inversions, translocations, etc. in vcf format (no header)
    # which biodiff will eventually combine with its own vcf from the other differences it finds
    vcflines = []
    with open(args.rdiff) as rfile:
        line2inv = False  # dnadiff records inversions in 2 lines. first occurrence is start, 2nd is end.
        invstart = 0
        for line in rfile:
            cleanline = line.strip('\n')
            rdiff = cleanline.split('\t')
            # rdiff[2] is genome position, rdiff[1] is variation type (GAP, INV, etc)
            if rdiff[1] == 'INV' and not line2inv:
                vcfstring = chromname + '\t' + rdiff[2] + '\t.\tN\tINV\t.\tPASS\t'
                line2inv = True
                invstart = int(rdiff[2])
            elif rdiff[1] == 'INV':
                vcfstring += 'SVLEN=' + str(int(rdiff[2])-invstart) + ';SVTYPE=INV\n'
                vcflines.append(vcfstring)
                line2inv = False
    with open(args.vcf, 'w') as vfile:
        for line in vcflines:
            vfile.write(line)

    # parse args.qdiff to get inversions in querry coordinates
    # parse args.qfasta to get fasta of querry sequence,
    # undo the inversions found in args.qdiff
    # output noninverted fasta to args.tfasta, which biodiff will then use
    inversions = []  # stores locations of inversions in querry sequence
    translocations = []
    breaks = []
    with open(args.qdiff) as qfile:
        line2inv = False  # dnadiff records inversions in 2 lines. first occurrence is start, 2nd is end.
        for line in qfile:
            cleanline = line.strip('\n')
            qdiff = cleanline.split('\t')
            if qdiff[1] == 'INV' and not line2inv:  # INV ifo in 2 lines. first line has Start, 2nd has End
                vardict = dict(Start=int(qdiff[2]))
                inversions.append(vardict)
                line2inv = True
            elif qdiff[1] == 'INV':
                inversions[-1]['End'] = int(qdiff[2])
                line2inv = False

    qrecord = SeqIO.parse(args.qfasta, 'fasta').next()  # read in the fasta file, should read only the first contig
    qseq = qrecord.seq  # get the sequence of the querry genome
    fixedrecord = qrecord
    for invdict in inversions:
        before = qseq[0:invdict['Start']]
        fixedinv = qseq[invdict['Start']:invdict['End']].reverse_complement()
        after = qseq[invdict['End']:]
        qseq = before + fixedinv + after

    # next fix translocations

    # write out temp fasta
    fixedrecord.seq = qseq
    SeqIO.write(fixedrecord, args.tfasta, 'fasta')

if __name__ == '__main__':
    main()

