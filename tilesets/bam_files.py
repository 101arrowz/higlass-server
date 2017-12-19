import random
import numpy as np

def sample_reads(samfile, num_entries=256, entry_length=10000, 
        start_pos=None, 
        end_pos=None,
        chrom_order=None):
    '''
    Sample reads from the specified region, assuming that the chromosomes
    are ordered in some fashion. Returns an list of pysam reads

    Parameters:
    -----------
    samfile: pysam.AlignmentFile
        A pysam entry into an indexed bam file
    num_entries: int
        The number of reads to sample
    entry_length: int
        The number of base pairs to sample in this file
    start_pos: int
        The start position of the sampled region
    end_pos: int
        The end position of the sampled region
    chrom_order: ['chr1', 'chr2',...]
        A listing of chromosome names to use as the order

    Returns
    -------
    reads: [read1, read2...]
        The list of in the sampled regions
    '''

    total_length = sum(samfile.lengths)
    #print("tl:", total_length, np.cumsum(np.array(samfile.lengths)))
    
    if start_pos is None:
        start_pos = 1
    if end_pos is None:
        end_pos = total_length
    
    # limit the total length by the number of bases that we're going
    # to fetch
    poss = [int(i) for i in 
            np.linspace(start_pos, end_pos - entry_length, num_entries)]

    # if chromorder is not None...
    # specify the chromosome order for the fetched reads
    
    lengths = []
    cum_seq_lengths = np.cumsum(np.array(samfile.lengths))
    results = []

    for pos in poss:
        #print("pos1:", pos)
        #print('cum_seq_lengths', cum_seq_lengths)
        fnz = np.flatnonzero(cum_seq_lengths >= pos)

        if len(fnz) == 0:
            continue

        #print('fnz:', fnz)
        seq_num = fnz[0]
        seq_name = samfile.references[seq_num]
        #print("seq_name:", seq_name)
        cname = '{}'.format(seq_name)
        
        #print('pos:', pos)
        #print('cum_seq_lengths[seq_num]', cum_seq_lengths[seq_num])
        if seq_num > 0:
            pos = pos - cum_seq_lengths[seq_num-1]
        #print("seq_name:", seq_name, 'pos:', pos )
        
        reads = samfile.fetch(cname, pos, pos + entry_length)

        #print('reads:', reads)
        for read in reads:
            query_seq = read.query_sequence

            differences = []
            try:
                for counter, (qpos, rpos, ref_base) in enumerate(read.get_aligned_pairs(with_seq=True)):
                    # inferred from the pysam source code:
                    # https://github.com/pysam-developers/pysam/blob/3defba98911d99abf8c14a483e979431f069a9d2/pysam/libcalignedsegment.pyx
                    # and GitHub issue:
                    # https://github.com/pysam-developers/pysam/issues/163
                    #print('qpos, rpos, ref_base', qpos, rpos, ref_base)
                    if rpos is None:
                        differences += [(qpos, 'I')]
                    elif qpos is None:
                        differences += [(counter, 'D')]
                    elif ref_base.islower():
                        differences += [(qpos, query_seq[qpos])]
            except ValueError as ve:
                # probably lacked an MD string
                pass

            results += [ [
                    read.reference_id,
                    read.reference_start,
                    read.rlen,
                    differences
                    ]]

            '''
            print('read:', read)
            print("dir", dir(read))
            print(read.reference_id)
            print(read.reference_start)
            print(read.rlen)
            print(read.get_tag('MD'))
            print(read.get_reference_sequence())
            print(read.query_sequence)
            print(read.get_aligned_pairs(with_seq=True))
            '''


            # results += [len(list(reads))]
        
        #samfile.count_coverage(cname, pos, pos + entry_length)
        
    return results
