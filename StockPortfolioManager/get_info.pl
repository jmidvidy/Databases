#!/usr/bin/perl

use Getopt::Long;
use Time::ParseDate;
use FileHandle;

use stock_data_access;

BEGIN {    # this just means it runs before anything else
    $ENV{PORTF_DBMS}="oracle";
    $ENV{PORTF_DB}="cs339";
    $ENV{PORTF_DBUSER}="jam658";
    $ENV{PORTF_DBPASS}="z0xM6lllV";

    unless ($ENV{BEGIN_BLOCK}) {
	use Cwd;
	$ENV{ORACLE_BASE}="/raid/oracle11g/app/oracle/product/11.2.0.1.0";
	$ENV{ORACLE_HOME}=$ENV{ORACLE_BASE}."/db_1";
	$ENV{ORACLE_SID}="CS339";
	$ENV{LD_LIBRARY_PATH}=$ENV{ORACLE_HOME}."/lib";
	$ENV{BEGIN_BLOCK} = 1;
	exec 'env',cwd().'/'.$0,@ARGV;
    }
};


$close=1;

$field='close';

&GetOptions("field=s" => \$field,
	    "from=s" => \$from,
	    "to=s" => \$to);

if (defined $from) { $from=parsedate($from);}
if (defined $to) { $to=parsedate($to); }


$#ARGV>=0 or die "usage: get_info.pl [--field=field] [--from=time] [--to=time] SYMBOL+\n";

print join("\t","symbol","field","num","mean","std","min","max","cov"),"\n";

while ($symbol=shift) {
  $sql = "select count($field), avg($field), stddev($field), min($field), max($field)  from ".GetStockPrefix()."StocksDaily where symbol='$symbol'";
  $sql.= " and timestamp>=$from" if $from;
  $sql.= " and timestamp<=$to" if $to;

  ($n,$mean,$std,$min,$max) = ExecStockSQL("ROW",$sql);

  print join("\t",$symbol,$field, $n, $mean, $std, $min, $max, $std/$mean),"\n";
  
}
