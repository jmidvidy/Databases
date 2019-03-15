#!/usr/bin/perl -w

#$#ARGV==6 or die "usage: test.pl \"reference implementation command line\" \"your implementation command line\" keysize valsize seed num maxerrs\n";

($refcmd,$testcmd,$keysize,$valsize,$maxerrs)=@ARGV;

system "$refcmd < my_TEST.input > my_TEST.refout";

system "$testcmd < my_TEST.input > my_TEST.yourout";

system "compare.pl my_TEST.input my_TEST.refout my_TEST.yourout $maxerrs";
