suppressPackageStartupMessages({library(edgeR); library(limma)})
args <- commandArgs(TRUE)
stopifnot(length(args)==1L)
root <- normalizePath(args[1]); src <- file.path(root,'sources')
out <- file.path(root,'results')
if(dir.exists(out)) stop('Results already exist; use a fresh output directory.')
dir.create(out, recursive=TRUE)
read <- function(f) read.delim(file.path(src,f),check.names=FALSE,stringsAsFactors=FALSE)
write <- function(x,f) write.table(x,file.path(out,f),sep='\t',quote=FALSE,row.names=FALSE,na='NA')
raw <- read('counts_raw.tsv'); meta <- read('samples.tsv'); annotation <- read('annotation.tsv')
counts <- as.matrix(raw[,-1]); rownames(counts)<-as.character(raw$ENTREZID)
stopifnot(identical(colnames(counts),meta$sample_name),!anyDuplicated(rownames(counts)),
          !anyDuplicated(meta$sample_name),all(is.finite(counts)),all(counts>=0),
          all(counts==floor(counts)),all(colSums(counts)==meta$assigned_counts),
          sum(counts[,'KRAS_siRNA_M1'])==37657740)
sets <- list(); collection <- character(); descriptions <- character()
for(item in list(c('Hallmark','h.all.v2026.2.Hs.entrez.gmt'),c('Reactome','c2.cp.reactome.v2026.2.Hs.entrez.gmt'))){
 for(line in readLines(file.path(src,item[2]))){
  z<-strsplit(line,'\t')[[1]]; stopifnot(length(z)>2,grepl('^(HALLMARK|REACTOME)_',z[1]))
  sets[[z[1]]]<-unique(z[-c(1,2)]); collection[z[1]]<-item[1]; descriptions[z[1]]<-z[2]
 }
}
ann_idx<-match(rownames(counts),as.character(annotation$ENTREZID))
stopifnot(!anyNA(ann_idx))
symbols<-setNames(annotation$SYMBOL[ann_idx],rownames(counts))
all_camera<-list(); fit_info<-list(); full_genes<-NULL
make_data<-function(choice='pooled',omit=NULL){
 m<-meta; x<-counts
 p<-which(m$cell_line=='MiaPaca-2' & m$condition=='KRAS'); stopifnot(length(p)==2)
 if(choice=='pooled'){
  x[,p[1]]<-rowSums(x[,p,drop=FALSE]); m$sample_name[p[1]]<-'KRAS_MiaPaca2_pooled'
  m$run_accession[p[1]]<-paste(m$run_accession[p],collapse=';'); colnames(x)[p[1]]<-m$sample_name[p[1]]
  keep<-setdiff(seq_len(ncol(x)),p[2])
 } else {keep<-setdiff(seq_len(ncol(x)),p[m$run_accession[p]!=choice])}
 x<-x[,keep,drop=FALSE]; m<-m[keep,,drop=FALSE]
 if(!is.null(omit)){keep<-m$cell_line!=omit; x<-x[,keep,drop=FALSE];m<-m[keep,,drop=FALSE]}
 m$cell_line<-factor(m$cell_line);m$condition<-factor(m$condition,levels=c('Control','KRAS'))
 rownames(m)<-m$sample_name
 stopifnot(identical(colnames(x),m$sample_name),all(table(m$cell_line,m$condition)==1))
 list(x=x,m=m)
}
run_fit<-function(label,choice='pooled',omit=NULL){
 cat('Fitting',label,'\n');flush.console()
 dat<-make_data(choice,omit);x<-dat$x;m<-dat$m
 design<-model.matrix(~cell_line+condition,m)
 stopifnot(qr(design)$rank==ncol(design),nrow(design)>ncol(design))
 keep<-rowSums(x>=10)>=2
 d<-calcNormFactors(DGEList(x[keep,,drop=FALSE]),method='TMM')
 effective_libraries<-d$samples$lib.size*d$samples$norm.factors
 stopifnot(max(effective_libraries)/min(effective_libraries)<3)
 v<-cpm(d,log=TRUE,prior.count=2)
 idx<-ids2indices(sets,rownames(d)); lens<-lengths(idx);idx<-idx[lens>=15 & lens<=500]
 fit<-eBayes(lmFit(v,design),trend=TRUE); coef<-which(colnames(design)=='conditionKRAS')
 cam<-camera(v,idx,design,contrast=coef,inter.gene.cor=NA,allow.neg.cor=FALSE,trend.var=TRUE,sort=FALSE)
 cam$gene_set<-rownames(cam);cam$collection<-unname(collection[cam$gene_set]);cam$fit<-label
 cam$q_global<-p.adjust(cam$PValue,'BH');cam$q_collection<-NA_real_
 for(c in unique(cam$collection)){i<-cam$collection==c;cam$q_collection[i]<-p.adjust(cam$PValue[i],'BH')}
 cam$FDR<-NULL
 gt<-data.frame(ENTREZID=rownames(d),SYMBOL=unname(symbols[rownames(d)]),
                log2FC=fit$coefficients[,coef],t=fit$t[,coef],p=fit$p.value[,coef])
 gm<-match(rownames(d),gt$ENTREZID)
 cam$median_log2FC<-vapply(idx,function(i)median(gt$log2FC[i]),numeric(1))
 cam$positive_gene_fraction<-vapply(idx,function(i)mean(gt$log2FC[i]>0),numeric(1))
 cam$raw_set_size<-vapply(cam$gene_set,function(s)length(sets[[s]]),integer(1))
 cam$members_entrez<-vapply(idx,function(i)paste(rownames(d)[i],collapse=';'),character(1))
 cam$members_symbols<-vapply(idx,function(i)paste(ifelse(is.na(gt$SYMBOL[i]),gt$ENTREZID[i],gt$SYMBOL[i]),collapse=';'),character(1))
 write(cam,paste0('camera_',label,'.tsv'));write(gt,paste0('gene_effects_',label,'.tsv'))
 norm<-data.frame(m,library_counts=colSums(x),TMM=d$samples$norm.factors,
                  retained_library_counts=d$samples$lib.size,row.names=NULL)
 write(norm,paste0('samples_',label,'.tsv'))
 write(data.frame(sample=rownames(design),design,check.names=FALSE),paste0('design_',label,'.tsv'))
 fit_info[[label]]<<-data.frame(fit=label,observations=ncol(x),cell_lines=nlevels(m$cell_line),
                     genes=sum(keep),rank=qr(design)$rank,residual_df=nrow(design)-ncol(design),
                     effective_library_ratio=max(effective_libraries)/min(effective_libraries),
                     Hallmark=sum(cam$collection=='Hallmark'),Reactome=sum(cam$collection=='Reactome'),
                     significant_global=sum(cam$q_global<.05),significant_Hallmark_global=sum(cam$q_global<.05 & cam$collection=='Hallmark'))
 all_camera[[label]]<<-cam
 if(label=='full'){
  full_genes<<-gt
  prev<-read('prior_filter.tsv');stopifnot(sum(keep)==17819,identical(unname(keep),unname(prev$prefilter_pass)))
  fixed<-camera(v,idx,design,contrast=coef,inter.gene.cor=.01,allow.neg.cor=FALSE,trend.var=TRUE,sort=FALSE)
  fixed$gene_set<-rownames(fixed); fixed$collection<-unname(collection[fixed$gene_set]);
  fixed$q_global<-p.adjust(fixed$PValue,'BH');fixed$FDR<-NULL
  write(fixed,'camera_full_fixed_correlation_001.tsv')
  write(data.frame(ENTREZID=rownames(d),mean_logCPM=rowMeans(v),residual_variance=fit$sigma^2,prior_variance=fit$s2.prior),
        'limma_trend_mean_variance.tsv')
 }
 invisible(NULL)
}
run_fit('full')
for(line in sort(unique(meta$cell_line)))run_fit(paste0('omit_',line),omit=line)
for(run in c('SRR24828471','SRR24828472'))run_fit(paste0('P5_',run),choice=run)
write(do.call(rbind,fit_info),'fit_summary.tsv')
long<-do.call(rbind,all_camera);rownames(long)<-NULL;write(long,'camera_all_fits.tsv')
full<-all_camera$full
stability<-full[,c('gene_set','collection','Direction','PValue','q_global','q_collection','NGenes','Correlation','median_log2FC')]
for(s in c('same_direction_rounds','significant_same_direction_rounds','available_rounds'))stability[[s]]<-0L
for(label in names(all_camera)[grepl('^omit_',names(all_camera))]){
 z<-all_camera[[label]][match(full$gene_set,all_camera[[label]]$gene_set),]
 available<-!is.na(z$PValue);agree<-available & z$Direction==full$Direction
 stability$available_rounds<-stability$available_rounds+available
 stability$same_direction_rounds<-stability$same_direction_rounds+ifelse(is.na(agree),FALSE,agree)
 stability$significant_same_direction_rounds<-stability$significant_same_direction_rounds+ifelse(is.na(agree),FALSE,agree & z$q_global<.05)
 stability[[paste0(label,'_q_global')]]<-z$q_global
}
for(run in c('SRR24828471','SRR24828472')){
 z<-all_camera[[paste0('P5_',run)]][match(full$gene_set,all_camera[[paste0('P5_',run)]]$gene_set),]
 stability[[paste0('P5_',run,'_q_global')]]<-z$q_global
 stability[[paste0('P5_',run,'_direction')]]<-z$Direction
}
write(stability,'camera_stability.tsv')


ds<-read('DESeq2_full.tsv');er<-read('edgeR_full.tsv');stable<-read('stable_ge7of8.tsv')
stopifnot(identical(ds$ENTREZID,er$ENTREZID),!anyDuplicated(ds$ENTREZID))
joint<-is.finite(ds$padj)&ds$padj<.05&abs(ds$log2FoldChange)>.5 & is.finite(er$FDR)&er$FDR<.05&abs(er$logFC)>.5
stopifnot(sum(joint)==2020,nrow(stable)==1515)
agree<-sign(ds$log2FoldChange)==sign(er$logFC)
eligible<-as.character(ds$ENTREZID[is.finite(ds$padj)&is.finite(er$FDR)])
retained<-as.character(ds$ENTREZID[ds$prefilter_pass])
write(data.frame(ENTREZID=eligible),'ora_eligible_background.tsv')
lists<-list(full_joint=as.character(ds$ENTREZID[joint & agree]),stable_ge7of8=as.character(stable$ENTREZID))
orows<-list();summary<-list()
for(listname in names(lists))for(bgname in c('eligible','retained')){
 bg<-if(bgname=='eligible')eligible else retained
 for(direction in c('Up','Down')){
  gl<-lists[[listname]]; idx<-match(gl,as.character(ds$ENTREZID));
  gl<-gl[if(direction=='Up')ds$log2FoldChange[idx]>0 else ds$log2FoldChange[idx]<0]
  gl<-intersect(gl,bg); N<-length(bg);n<-length(gl)
  summary[[paste(listname,bgname,direction)]]<-data.frame(list=listname,background=bgname,direction=direction,universe=N,selected=n)
  for(s in names(sets)){
   inbg<-intersect(sets[[s]],bg);K<-length(inbg)
   if(K<15 || K>500)next
   hits<-intersect(gl,inbg);k<-length(hits)
   orows[[length(orows)+1]]<-data.frame(list=listname,background=bgname,direction=direction,
      gene_set=s,collection=collection[[s]],universe=N,selected=n,set_measured=K,hits=k,
      expected=n*K/N,fold_enrichment=if(n>0)k/(n*K/N) else NA_real_,
      PValue=phyper(k-1,K,N-K,n,lower.tail=FALSE),
      hits_entrez=paste(hits,collapse=';'),hits_symbols=paste(symbols[hits],collapse=';'))
  }
 }
}
ora<-do.call(rbind,orows);rownames(ora)<-NULL;ora$q_global<-NA_real_
for(l in names(lists))for(b in c('eligible','retained')){
 i<-ora$list==l & ora$background==b;ora$q_global[i]<-p.adjust(ora$PValue[i],'BH')
}
write(ora,'ora_all.tsv');write(do.call(rbind,summary),'ora_universe_summary.tsv')
write(data.frame(ENTREZID=ds$ENTREZID[joint],SYMBOL=ds$SYMBOL[joint],
                 DESeq2_log2FC=ds$log2FoldChange[joint],edgeR_log2FC=er$logFC[joint],
                 same_direction=agree[joint]),'joint_2020_direction_audit.tsv')
writeLines(capture.output(sessionInfo()),file.path(root,'sources/R_session.txt'))
cat('Completed',length(all_camera),'paired CAMERA models and complementary ORA.\n')
