#!/usr/bin/env perl


#Use: script.pl file.fasta [length] > output.fasta  

use strict;
use warnings;
use Bio::SeqIO;

my $file = $ARGV[0];
my $len = $ARGV[1];

my $inseq = Bio::SeqIO->new(
	-file => "<$file",
	-format => "fasta",
);

my $outseq = Bio::SeqIO->new(
	-fh     => \*STDOUT,
	-format => "fasta",
);

while( my $seqref = $inseq->next_seq){
	my $seq = $seqref->seq();
        if (length($seq) >= $len){
		$outseq->write_seq($seqref);
		}
}







