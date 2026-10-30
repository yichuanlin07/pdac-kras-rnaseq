suppressPackageStartupMessages({library(edgeR);library(limma)})
args<-commandArgs(TRUE);root<-normalizePath(args[1]);src<-file.path(root,'sources')
read<-function(n)read.delim(file.path(src,n),check.names=FALSE,stringsAsFactors=FALSE)
x<-read('counts_raw.tsv');m<-read('samples.tsv');ids<-as.character(x[[1]]);x<-as.matrix(x[,-1]);rownames(x)<-ids
stopifnot(identical(colnames(x),m$sample_name))
p<-which(m$cell_line=='MiaPaca-2' & m$condition=='KRAS');x[,p[1]]<-rowSums(x[,p]);x<-x[,-p[2]];m<-m[-p[2],]

o<-rev(seq_len(ncol(x)));x<-x[,o];m<-m[o,]
m$condition<-factor(m$condition,levels=c('Control','KRAS'));m$cell_line<-factor(m$cell_line)
design<-model.matrix(~cell_line+condition,m);x<-x[rowSums(x>=10)>=2,]
d<-calcNormFactors(DGEList(x));v<-cpm(d,log=TRUE,prior.count=2)
sets<-list()
for(f in c('h.all.v2026.2.Hs.entrez.gmt','c2.cp.reactome.v2026.2.Hs.entrez.gmt'))for(line in readLines(file.path(src,f))){z<-strsplit(line,'\t')[[1]];sets[[z[1]]]<-unique(z[-c(1,2)])}
index<-ids2indices(sets,rownames(x));index<-index[lengths(index)>=15 & lengths(index)<=500]
coef<-which(colnames(design)=='conditionKRAS');contrast<-rep(0,ncol(design));contrast[coef]<- -1
backward<-camera(v,index,design,contrast=contrast,inter.gene.cor=NA,trend.var=TRUE,sort=FALSE,allow.neg.cor=FALSE)
old<-read.delim(file.path(root,'results/camera_full.tsv'),check.names=FALSE)
new<-backward[match(old$gene_set,rownames(backward)),]
forward<-camera(v,index,design,contrast=coef,inter.gene.cor=NA,trend.var=TRUE,sort=FALSE,allow.neg.cor=FALSE)
forward<-forward[match(old$gene_set,rownames(forward)),]
cat('Order maximum P difference:',max(abs(old$PValue-forward$PValue)),'\n')
cat('Contrast maximum P difference:',max(abs(forward$PValue-new$PValue)),'\n')
cat('Direction reversals:',sum(forward$Direction!=new$Direction),'of',nrow(new),'\n')
stopifnot(all(abs(old$PValue-new$PValue)<1e-10),all(old$Direction!=new$Direction))
writeLines(c('PASS: all 1172 CAMERA P values preserved after reversing sample order and contrast.',
             'PASS: all 1172 directions reverse with Control / KRAS.',
             paste('Maximum absolute P-value difference:',format(max(abs(old$PValue-new$PValue)),digits=12))),
           file.path(root,'results/contrast_verification.txt'))
cat('Contrast and observation-order verification passed.\n')
