
#include "../intervaldb.h"
#include "maf2nclist.h"

int seqnameID_qsort_cmp(const void *void_a,const void *void_b)
{
  return strcmp(((SeqNameID_T *)void_a)->p,((SeqNameID_T *)void_b)->p);
}

int seqidmap_qsort_cmp(const void *void_a,const void *void_b)
{ /* SORT IN ORDER OF id */
  SeqIDMap *a=(SeqIDMap *)void_a,*b=(SeqIDMap *)void_b;
  return strcmp(a->id,b->id);
}



int findseqID(char seqName[],SeqIDMap seqidmap[],int r)
{
  int i,l=0,mid;
  while (l<r) { /* TRY FINDING IT USING BINARY SEARCH */
    mid=(l+r)/2;
    i=strcmp(seqidmap[mid].id,seqName);
    if (i==0) /* FOUND IT */
      return mid;
    else if (i<0) /* seqidmap[mid] < seqName */
      l=mid+1;
    else /* seqName < seqidmap[mid] */
      r=mid;
  }
  return -1;
}




int save_interval(IntervalMap *im,int start,int stop,int iseq,int istart,int istop)
{
  im->start=start;
  im->end=stop;
  im->target_id=iseq;
  im->target_start=istart;
  im->target_end=istop;
  im->sublist= -1; /* DEFAULT VALUE */
  return 1;
}


int readMAFrecord(IntervalMap im[],int n,SeqIDMap seqidmap[],int nseq,
		  int lpoStart,int *p_block_len,FILE *ifile,int maxseq,
		  long long linecode_count[],int *p_has_continuation)
{
  int i,start,seqStart,junk,iseq= -1,max_len=0,seqLength,newline=1,l,extend=0;
  unsigned char tmp[32768]; /* MUST USE UNSIGNED ARITHMETIC FOR linecode_count[] INDEXING! */
  char *p,seq[32768],prefix[8],seqName[64],oriFlag[8];
  if (p_has_continuation) /* DEFAULT: NO CONTINUATION */
    *p_has_continuation = 0;
  while ((p=fgets(tmp,32767,ifile))) {
    l=strlen(tmp);
    if (newline ) {
      if ('s'==tmp[0] && isspace(tmp[1])) { /* READ SEQUENCE ALIGNMENT LINE */
	if (7==sscanf(tmp,"%2s %63s %d %d %2s %d %s",prefix,seqName,&seqStart,&junk,
		      oriFlag,&seqLength,seq)) {
	  /* 	printf("%s,%d,%s,%d\n",seqName,seqStart,oriFlag,seqLength); */
	  iseq=findseqID(seqName,seqidmap,nseq); /* LOOK UP INDEX FOR SEQ */
	  if (iseq<0) 
	    fprintf(stderr," *** WARNING: Unknown sequence %s ignored...\n",seqName);
	  if (0==strcmp("-",oriFlag))
	    seqStart= -(seqLength-seqStart); /* CALCULATE NEGATIVE INDEX INDICATING REVERSE STRAND*/
	  extend=0; /* START OF A NEW LPO LINE */
	}
	else /* WRONG FORMAT??!? COMPLAIN TO THE USER */
	  fprintf(stderr," *** WARNING: Incorrectly formated alignment line ignored:\n%s\n",
		  tmp);
      }
      else if ('a'==tmp[0]) { /* START OF A NEW ALIGNMENT BLOCK */
	if (p_has_continuation) /* RETURN SIGNAL THAT THIS IS A NEW CONTINUATION */
	  *p_has_continuation = 1;
	break;
      }
      else if (linecode_count) { /* COUNT UNEXPECTED LINES OF DIFFERENT TYPES */
	linecode_count[tmp[0]]++;
	iseq= -1; /* DO NOT PROCESS THIS LINE AS SEQUENCE ALIGNMENT LINE! */
      }
    }

    if (tmp[l-1]=='\n' || tmp[l-1]=='\r') /* CHECK FOR START OF NEW LINE FOLLOWING...*/
      newline=1;
    else
      newline=0;

    if (iseq<0)  /* IGNORE UNKNOWN SEQUENCES */
      continue; 

/*     printf("\tALIGN: %s,%s,%d,%d,%s,%d,%s\n",prefix,seqName,seqStart,junk,oriFlag,junk,seq); */
    i=0;
    while (seq[i]) {
      while ('-'==seq[i]) i++; /* SKIP GAP REGIONS */
      if (seq[i]==0) break; /* END OF SEQUENCE */
      for (start=i;seq[i] && seq[i]!='-';i++); /* GET A SEQUENCE INTERVAL */
/*       printf("\t\t%d,%d\n",start,i);  */
      if (n>=maxseq) 
	return -1; /* ERROR: RAN OUT OF SPACE!!! */
      save_interval(im+n,lpoStart+extend+start,lpoStart+extend+i,
		    iseq,seqStart,seqStart+i-start);
      n++;
      seqStart += i-start;
    }
    if (i>max_len) /* RECORD MAXIMUM seq LENGTH */
      max_len = i;
    if (!newline) /* LINE EXCEEDS BUFFER SIZE; LPO MUST EXTEND TO NEXT LINE */
      extend+=i;
  }
/*   printf("readMAFrecord: %d hits\n",n); */
  if (p_block_len)
    *p_block_len = max_len;
  return n;
}





#ifdef SOURCE_EXCLUDED
/* OLD, PRE-UNION VERSION */

int findseqname(char seqName[],SeqNameID_T seqnames[],int nseq0,int *p_nseq1,
		int maxseq)
{
  int i,l=0,r,mid;
  r=nseq0;
  while (l<r) { /* TRY FINDING IT USING BINARY SEARCH */
    mid=(l+r)/2;
    i=strcmp(seqnames[mid].p,seqName);
    if (i==0) /* FOUND IT */
      return seqnames[mid].id;
    else if (i<0) /* seqnames[mid] < seqName */
      l=mid+1;
    else /* seqName < seqnames[mid] */
      r=mid;
  }
  for (i=nseq0;i< *p_nseq1;i++) /* TRY FINDING IT IN UNSORTED ADDENDUM*/
    if (0==strcmp(seqnames[i].p,seqName))
      return seqnames[i].id;
  if (*p_nseq1 >= maxseq)
    return -1; /* ERROR: RAN OUT OF SPACE!!! */
  seqnames[*p_nseq1].p=malloc(strlen(seqName)+1); /* CREATE A NEW ENTRY HERE */
  strcpy(seqnames[*p_nseq1].p,seqName);
  seqnames[*p_nseq1].id = *p_nseq1;
  return (*p_nseq1)++;
}


void free_seqnames(SeqNameID_T seqnames[],int n)
{
  int i;
  for (i=0;i<n;i++) {
    free(seqnames[i].p);
    seqnames[i].p=NULL;
  }
}



int readMAFrecord(IntervalMap im[],int n,SeqNameID_T seqnames[],int nseq0,int *p_nseq1,
		  int lpoStart,int *p_block_len,FILE *ifile,int maxseq)
{
  int i,start,seqStart,rev,junk,iseq,max_len=0,seqLength;
  char *p,tmp[32768],seq[32768],prefix[8],seqName[64],oriFlag[8];
  for (p=fgets(tmp,32767,ifile);
       p && 7==sscanf(tmp,"%2s %s %d %d %2s %d %s",prefix,seqName,&seqStart,&junk,
		      oriFlag,&seqLength,seq) && 's'==prefix[0] && '\0'==prefix[1];
       p=fgets(tmp,32767,ifile)) {
/*     printf("\tALIGN: %s,%s,%d,%d,%s,%d,%s\n",prefix,seqName,seqStart,junk,oriFlag,junk,seq); */
    iseq=findseqname(seqName,seqnames,nseq0,p_nseq1,maxseq); /* LOOK UP INDEX FOR SEQ */
    if (iseq<0) return -1;  /* ERROR: RAN OUT OF SPACE!!! */
    if (0==strcmp("-",oriFlag))
      seqStart= -(seqLength-seqStart); /* CALCULATE NEGATIVE INDEX INDICATING REVERSE STRAND*/
    i=0;
    while (seq[i]) {
      while ('-'==seq[i]) i++; /* SKIP GAP REGIONS */
      if (seq[i]==0) break; /* END OF SEQUENCE */
      for (start=i;seq[i] && seq[i]!='-';i++); /* GET A SEQUENCE INTERVAL */
/*       printf("\t\t%d,%d\n",start,i); */
      if (n>=maxseq) return -1; /* ERROR: RAN OUT OF SPACE!!! */
      save_interval(im+n,lpoStart+start,lpoStart+i,iseq,seqStart,seqStart+i-start);
      n++;
      seqStart += i-start;
    }
    if (i>max_len) /* RECORD MAXIMUM seq LENGTH */
      max_len = i;
  }
/*   printf("readMAFrecord: %d hits\n",n); */
  if (p_block_len)
    *p_block_len = max_len;
  return n;
}
#endif
