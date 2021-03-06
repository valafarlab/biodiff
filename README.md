% BIODIFF(1) 0.2
% Afif Elghraoui <aelghraoui@sdsu.edu>
% February 2017

[![install with bioconda](https://img.shields.io/badge/install%20with-bioconda-brightgreen.svg?style=flat-square)](http://bioconda.github.io/recipes/biodiff/README.html)

# NAME

biodiff - exact comparison of biological sequences

# SYNOPSIS

**biodiff** *reference.fasta* *query.fasta* > *out.vcf*

# DESCRIPTION

**biodiff** is a variant caller that determines the exact differences between two biological sequences.
It can operate on DNA and protein sequences, as long as they are in fasta format.
The sequences to be compared must have the same fasta header (up to the first whitespace).
If the reference and query each have only one sequence, however, the header need not match and the comparison will be done, but a warning will be emitted.
Output is in the Variant Call Format.

**biodiff** uses **diff**(1), an implementation of Myer's algorithm to find longest common substrings and determine the minimal difference between the sequences.
It is especially useful for exact genome comparison, as standard genome comparison tools are often vague regarding the positions of large insertions and deletions.
It can be helpful to first get an accurate picture of the plain insertions and deletions that differentiate two sequences, before trying to decide whether they represent translocations, tandem copy number variation, or anything else.

# EXAMPLES

## Quick evaluation
You might want to quickly see the difference between two revisions of an NCBI reference sequence.

~~~
biodiff NC_123456.1.fasta NC_123456.2.fasta
~~~

The output goes to your terminal.

## Protein Sequence Comparison

It works the same way with amino acid sequences:

~~~
biodiff wild-type.faa mutant.faa
~~~

## Comparison of variants between samples
You will typically want to normalize and left-align variants, especially when comparing variants between different samples, as variants within repetitive sequences can be accurately represented in multiple ways and falsely appear to be different.

~~~
for query in query1 query2
do
	biodiff reference.fasta $query.fasta | bcftools norm --fasta-ref reference.fasta - > $query.vcf
	bgzip $query.vcf && tabix -p vcf $query.vcf.gz
done

bcftools isec query1.vcf.gz query2.vcf.gz
~~~

# BUGS

**biodiff** currently does not properly handle in-place inversions.

Please report issues at
https://gitlab.com/LPCDRP/biodiff/issues

# SEE ALSO

**bcftools**(1)
**dnadiff**(1)
**Assemblytics**(1)
