REGISTER /usr/local/pig/contrib/piggybank/java/piggybank.jar;
DEFINE Over org.apache.pig.piggybank.evaluation.Over();
DEFINE Stitch org.apache.pig.piggybank.evaluation.Stitch();

A = load 'NLDAS-data/tdata/temp*.txt' as (gid,dt,temp);
# Or try this Pig/Hadoop globbing: A = load 'NLDAS-data/tdata/temp201206010{000,100}.txt' as (gid,dt,temp);
  
B= GROUP A BY gid;

C= FOREACH B GENERATE group, count(A) as cnt;
C = FOREACH B {
  GENERATE group, MAX(A.temp) as maxtemp;
}
C= FOREACH B {
  C1 = ORDER A BY dt;
  GENERATE FLATTEN(Stitch(C1,Over(C1.temp,'lag',1,0,1)));
}

