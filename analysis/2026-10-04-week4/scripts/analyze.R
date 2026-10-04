#!/usr/bin/env Rscript
# Real PRJNA980201 counts. Independently written implementation of the Oct 3 methods.
options(stringsAsFactors=FALSE, digits=16)
set.seed(20261004)
suppressPackageStartupMessages({library(DESeq2); library(edgeR); library(apeglm); library(jsonlite)})
args <- commandArgs(TRUE)
if(length(args)<2) stop('Usage: Rscript analyze.R REPOSITORY_ROOT NEW_OUTPUT_DIR [PAPER_DATA_S1.csv]')
root <- normalizePath(args[1]); out <- args[2]
if(dir.exists(out)) stop('Use a new output directory; existing results are preserved.')
dir.create(out,recursive=TRUE)
src <- file.path(root,'analysis/2026-10-01/counts')
read <- function(p) read.delim(p,check.names=FALSE,colClasses='character')
dat <- read(file.path(src,'counts_raw.txt')); ids <- dat$ENTREZID
counts <- as.matrix(dat[,-1]); storage.mode(counts)<-'numeric'; rownames(counts)<-ids
meta <- read(file.path(src,'sample_annotation.txt'))
ann <- read(file.path(src,'annotate_geneID.txt'))
stopifnot(!anyDuplicated(ids),!anyDuplicated(meta$sample_name),identical(colnames(counts),meta$sample_name),
          all(is.finite(counts)),all(counts>=0),all(counts==floor(counts)),!anyDuplicated(ann$ENTREZID))
ann <- ann[match(ids,ann$ENTREZID),]; stopifnot(identical(ann$ENTREZID,ids))
stopifnot(identical(meta$ena_alias[meta$run_accession=='SRR24828471'],'MP2_K2v2'),
          identical(meta$ena_alias[meta$run_accession=='SRR24828472'],'MP2_K2'))
write <- function(x,name,dir=out) write.table(x,file.path(dir,name),sep='\t',quote=FALSE,row.names=FALSE,na='NA')
wm <- function(x,name,dir=out) write(data.frame(ENTREZID=rownames(x),x,check.names=FALSE),name,dir)
raw <- calcNormFactors(DGEList(counts)); rawlog <- cpm(raw,log=TRUE,prior.count=2)
wm(rawlog,'raw17_logCPM.tsv'); write(meta,'raw17_samples.tsv')
p5 <- which(meta$run_accession %in% c('SRR24828471','SRR24828472'))
write(data.frame(metric=c('Pearson_logCPM_all_genes','Spearman_raw_counts_all_genes'),value=c(cor(rawlog[,p5[1]],rawlog[,p5[2]]),cor(counts[,p5[1]],counts[,p5[2]],method='spearman'))),'p5_library_correlation.tsv')
scenarios <- c('merge_p5','retain_SRR24828472','retain_SRR24828471')
all_summary <- list(); fits <- list()
for(scenario in scenarios) {
  message('SCENARIO ',scenario)
  d <- file.path(out,scenario);dir.create(d)
  use <- rep(TRUE,nrow(meta))
  if(scenario=='retain_SRR24828472') use[meta$run_accession=='SRR24828471']<-FALSE
  if(scenario=='retain_SRR24828471') use[meta$run_accession=='SRR24828472']<-FALSE
  m <- meta[use,]; cts <- counts[,use,drop=FALSE]
  group <- paste(m$cell_line,m$condition,sep='_'); ordered <- unique(group)
  cts <- sapply(ordered,function(g) rowSums(cts[,group==g,drop=FALSE])); rownames(cts)<-ids
  cm <- m[match(ordered,group),c('cell_line','condition')]; cm$source_runs<-vapply(ordered,function(g) paste(m$run_accession[group==g],collapse=';'),'')
  cm$condition<-factor(ifelse(cm$condition=='KRAS','Treatment','Control'),levels=c('Control','Treatment'))
  cm$cell_line<-factor(cm$cell_line);rownames(cm)<-colnames(cts)<-ordered
  design <- model.matrix(~condition+cell_line,cm); coef <- which(colnames(design)=='conditionTreatment')
  stopifnot(ncol(cts)==16,all(table(cm$cell_line,cm$condition)==1),qr(design)$rank==ncol(design),length(coef)==1,
            all(design[cm$condition=='Treatment',coef]==1),all(design[cm$condition=='Control',coef]==0))
  write(data.frame(sample=rownames(cm),cm),'samples.tsv',d); write(data.frame(sample=rownames(design),design,check.names=FALSE),'design.tsv',d)
  wm(cts,'analysis_counts.tsv',d)
  keep <- rowSums(cts>=10)>=2
  write(data.frame(ENTREZID=ids,retained=keep,samples_count_ge10=rowSums(cts>=10)),'filter.tsv',d)
  dds <- DESeqDataSetFromMatrix(cts[keep,],cm,~condition+cell_line)
  dds <- DESeq(dds,quiet=TRUE)
  res <- results(dds,contrast=c('condition','Treatment','Control'),alpha=.05)
  reversed <- results(dds,contrast=c('condition','Control','Treatment'),alpha=.05)
  stopifnot(isTRUE(all.equal(res$log2FoldChange,-reversed$log2FoldChange)),isTRUE(all.equal(res$pvalue,reversed$pvalue)))
  shr <- lfcShrink(dds,coef='condition_Treatment_vs_Control',res=res,type='apeglm',quiet=TRUE)
  de <- as.data.frame(res);de$log2FC_apeglm<-shr$log2FoldChange;de$apeglm_posterior_SD<-shr$lfcSE
  de$padj_no_independent_filter<-results(dds,contrast=c('condition','Treatment','Control'),independentFiltering=FALSE)$padj
  de$padj_tutorial_alpha_0.1<-results(dds,contrast=c('condition','Treatment','Control'))$padj
  de$status<-ifelse(is.na(de$pvalue),'pvalue_unavailable_Cooks_or_all_zero',ifelse(is.na(de$padj),'independent_filtered','tested'))
  deg <- calcNormFactors(DGEList(cts[keep,]),method='TMM')
  deg <- estimateDisp(deg,design,robust=TRUE)
  fit <- glmQLFit(deg,design,robust=TRUE); qlf <- glmQLFTest(fit,coef=coef)
  contrast_reverse<-rep(0,ncol(design));contrast_reverse[coef]<- -1
  er_reverse<-glmQLFTest(fit,contrast=contrast_reverse)$table
  stopifnot(isTRUE(all.equal(qlf$table$logFC,-er_reverse$logFC)),isTRUE(all.equal(qlf$table$PValue,er_reverse$PValue)))
  er <- topTags(qlf,n=Inf,adjust.method='BH',sort.by='none')$table;er$status<-'tested'
  stopifnot(identical(rownames(de),rownames(er)))
  full <- function(x) { a<-ann; index<-match(ids,rownames(x));for(k in names(x)) a[[k]]<-x[[k]][index];a$prefilter_pass<-keep;a$status[!keep]<-'low_count_prefilter'; a }
  df <- full(de);ef<-full(er)
  write(df,'DESeq2_full.tsv',d);write(ef,'edgeR_full.tsv',d)
  common <- is.finite(de$pvalue)&is.finite(er$PValue)
  cmp<-data.frame(ENTREZID=rownames(de)[common],SYMBOL=ann$SYMBOL[keep][common],DESeq2_log2FC=de$log2FoldChange[common],DESeq2_shrunken_log2FC=de$log2FC_apeglm[common],edgeR_log2FC=er$logFC[common],DESeq2_padj=de$padj[common],edgeR_FDR=er$FDR[common],DESeq2_common_BH=p.adjust(de$pvalue[common],'BH'),edgeR_common_BH=p.adjust(er$PValue[common],'BH'))
  write(cmp,'method_comparison.tsv',d)
  sets <- list(DESeq2=rownames(de)[which(de$padj<.05)],edgeR=rownames(er)[which(er$FDR<.05)])
  summ<-data.frame(scenario=scenario,input_genes=length(ids),prefilter_pass=sum(keep),observations=nrow(cm),design_rank=qr(design)$rank,residual_df=nrow(cm)-ncol(design),DESeq2_finite_p=sum(is.finite(de$pvalue)),DESeq2_finite_padj=sum(is.finite(de$padj)),DESeq2_sig=length(sets$DESeq2),DESeq2_down=sum(de$padj<.05 & de$log2FoldChange<0,na.rm=TRUE),DESeq2_up=sum(de$padj<.05 & de$log2FoldChange>0,na.rm=TRUE),edgeR_sig=length(sets$edgeR),edgeR_down=sum(er$FDR<.05 & er$logFC<0),edgeR_up=sum(er$FDR<.05 & er$logFC>0),overlap=length(intersect(sets$DESeq2,sets$edgeR)),union=length(union(sets$DESeq2,sets$edgeR)),jaccard=length(intersect(sets$DESeq2,sets$edgeR))/length(union(sets$DESeq2,sets$edgeR)),LFC_pearson=cor(cmp$DESeq2_log2FC,cmp$edgeR_log2FC),LFC_spearman=cor(cmp$DESeq2_log2FC,cmp$edgeR_log2FC,method='spearman'),shared_finite_p=nrow(cmp),DESeq2_common_BH_sig=sum(cmp$DESeq2_common_BH<.05),edgeR_common_BH_sig=sum(cmp$edgeR_common_BH<.05),DESeq2_alpha01_sig=sum(de$padj_tutorial_alpha_0.1<.05,na.rm=TRUE))
  write(summ,'summary.tsv',d);all_summary[[scenario]]<-summ;fits[[scenario]]<-list(de=df,er=ef)
  write(data.frame(sample=rownames(cm),size_factor=sizeFactors(dds),TMM_factor=deg$samples$norm.factors,library_size=deg$samples$lib.size),'normalization.tsv',d)
  wm(counts(dds,normalized=TRUE),'DESeq2_normalized_counts.tsv',d)
  lognorm<-log2(counts(dds,normalized=TRUE)+1)
  write(data.frame(ENTREZID=rownames(lognorm),mean=rowMeans(lognorm),SD=apply(lognorm,1,sd)),'DESeq2_log_normalized_mean_SD.tsv',d)
  vstmat <- assay(vst(dds,blind=FALSE)); logcpm <- cpm(deg,log=TRUE,prior.count=2)
  for(method in c('DESeq2','edgeR')) {
    transformed<-if(method=='DESeq2') vstmat else logcpm
    pcgenes<-order(apply(transformed,1,var),decreasing=TRUE)[1:min(500,nrow(transformed))]
    pc<-prcomp(t(transformed[pcgenes,]),center=TRUE,scale.=FALSE);ve<-pc$sdev^2/sum(pc$sdev^2)
    write(data.frame(sample=rownames(pc$x),cm,PC1=pc$x[,1],PC2=pc$x[,2]),paste0(method,'_PCA.tsv'),d)
    write(data.frame(PC=seq_along(ve),variance_fraction=ve),paste0(method,'_PCA_variance.tsv'),d)
    write(data.frame(ENTREZID=rownames(transformed)[pcgenes]),paste0(method,'_PCA_genes.tsv'),d)
    wm(as.matrix(dist(t(transformed))),paste0(method,'_sample_distance.tsv'),d)
    write(data.frame(ENTREZID=rownames(transformed),mean=rowMeans(transformed),SD=apply(transformed,1,sd)),paste0(method,'_mean_SD.tsv'),d)
    if(scenario=='merge_p5') wm(transformed,paste0(method,'_transformed.tsv'),d)
  }
  cairo_pdf(file.path(d,'dispersion_diagnostics.pdf'),width=6.5,height=5,family='Times New Roman')
  plotDispEsts(dds);plotBCV(deg);plotQLDisp(fit);dev.off()
  write(data.frame(ENTREZID=rownames(de),baseMean=de$baseMean,DESeq2_dispersion=dispersions(dds),DESeq2_dispersion_fit=mcols(dds)$dispFit,edgeR_logCPM=er$logCPM,edgeR_NB_dispersion=deg$tagwise.dispersion,edgeR_QL_variance=fit$s2.post,edgeR_QL_prior=fit$s2.prior),'dispersion.tsv',d)
  write_json(list(contrast='Treatment (KRAS siRNA) / Control',reverse_contrast_LFC_negation_and_pvalue_identity=TRUE,model='~condition+cell_line',alpha=.05,DESeq2_independent_filter_threshold=unname(metadata(res)$filterThreshold),DESeq2_filter_theta=metadata(res)$filterTheta,edgeR_common_dispersion=deg$common.dispersion,P5_assumption=if(scenario=='merge_p5') 'Tutorial sum-count assumption; repeat type unresolved; exploratory' else 'One library retained; not a biological-repeat claim'),file.path(d,'method_metadata.json'),pretty=TRUE,auto_unbox=TRUE,digits=16)
}
write(do.call(rbind,all_summary),'scenario_summary.tsv')
sens<-ann
for(s in scenarios) {
  sens[[paste0(s,'_DESeq2_log2FC')]]<-fits[[s]]$de$log2FoldChange
  sens[[paste0(s,'_DESeq2_padj')]]<-fits[[s]]$de$padj
  sens[[paste0(s,'_edgeR_log2FC')]]<-fits[[s]]$er$logFC
  sens[[paste0(s,'_edgeR_FDR')]]<-fits[[s]]$er$FDR
}
sigcols<-grep('_padj$|_FDR$',names(sens),value=TRUE);lfccols<-grep('_log2FC$',names(sens),value=TRUE)
sens$significant_all_six<-apply(sens[,sigcols],1,function(v) all(is.finite(v)&v<.05))
sens$same_direction_all_six<-apply(sens[,lfccols],1,function(v) all(is.finite(v)) && (all(v<0)||all(v>0)))
write(sens,'sensitivity_full.tsv')
if(length(args)>=3) {
  paper<-read.csv(args[3],check.names=FALSE,colClasses='character'); names(paper)[1]<-'ENSEMBL_VERSION'
  stopifnot(nrow(paper)==14799,all(c('entrezgene_id','logFC','FDR','PValue') %in% names(paper)))
  numeric_id <- grepl('^[0-9]+$',paper$entrezgene_id)
  dup <- duplicated(paper$entrezgene_id)|duplicated(paper$entrezgene_id,fromLast=TRUE)
  excluded<-paper[!numeric_id|dup,];excluded$reason<-ifelse(!numeric_id[!numeric_id|dup],'missing_or_nonnumeric_Entrez','ambiguous_multiple_Ensembl_to_Entrez')
  write(excluded,'paper_excluded_mapping_rows.tsv')
  audit<-data.frame(paper_rows=nrow(paper),missing_or_nonnumeric=sum(!numeric_id),ambiguous_numeric_ID_rows=sum(dup&numeric_id),unique_numeric_rows=sum(numeric_id&!dup),paper_FDR05=sum(as.numeric(paper$FDR)<.05),paper_FDR05_absLFC_gt05=sum(as.numeric(paper$FDR)<.05 & abs(as.numeric(paper$logFC))>.5))
  write(audit,'paper_input_audit.tsv');paper<-paper[numeric_id&!dup,]
  a<-fits$merge_p5$er;de<-fits$merge_p5$de
  idx<-match(a$ENTREZID,paper$entrezgene_id);valid<-!is.na(idx)&is.finite(a$PValue)&is.finite(de$pvalue)
  b<-paper[idx[valid],]; joined<-data.frame(ENTREZID=a$ENTREZID[valid],SYMBOL=a$SYMBOL[valid],paper_symbol=b$external_gene_name,local_edgeR_logFC=a$logFC[valid],local_edgeR_FDR=a$FDR[valid],local_DESeq2_logFC=de$log2FoldChange[valid],local_DESeq2_padj=de$padj[valid],paper_logFC=as.numeric(b$logFC),paper_FDR=as.numeric(b$FDR))
  write(joined,'paper_comparison_common_unique.tsv')
  ps <- list()
  for(method in c('edgeR','DESeq2')) for(gate in c(0,.5)) {
    lfc<-joined[[if(method=='edgeR') 'local_edgeR_logFC' else 'local_DESeq2_logFC']];fdr<-joined[[if(method=='edgeR') 'local_edgeR_FDR' else 'local_DESeq2_padj']]
    l<-joined$ENTREZID[which(fdr<.05 & abs(lfc)>gate)];p<-joined$ENTREZID[which(joined$paper_FDR<.05 & abs(joined$paper_logFC)>gate)]
    ov<-intersect(l,p); oi<-match(ov,joined$ENTREZID)
    ps[[length(ps)+1]]<-data.frame(method=method,absLFC_gt=gate,common_genes=nrow(joined),local_sig=length(l),paper_sig=length(p),overlap=length(ov),jaccard=length(ov)/length(union(l,p)),overlap_same_direction=sum(sign(lfc[oi])==sign(joined$paper_logFC[oi])),LFC_Pearson=cor(lfc,joined$paper_logFC),LFC_Spearman=cor(lfc,joined$paper_logFC,method='spearman'))
  }
  write(do.call(rbind,ps),'paper_comparison_summary.tsv')
}
write(data.frame(Package=rownames(installed.packages()),Version=installed.packages()[,'Version']),'package_versions.tsv')
capture.output(sessionInfo(),file=file.path(out,'sessionInfo.txt'))
message('Completed ',normalizePath(out))
