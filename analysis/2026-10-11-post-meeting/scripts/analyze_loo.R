options(stringsAsFactors = FALSE, digits = 16)
set.seed(20261011)
suppressPackageStartupMessages({library(DESeq2); library(edgeR); library(apeglm); library(jsonlite)})
args <- commandArgs(TRUE)
if (length(args) != 2) stop("Usage: Rscript analyze_loo.R REPOSITORY_ROOT NEW_RESULTS_DIR")
root <- normalizePath(args[1]); out <- args[2]
if (dir.exists(out)) stop("Existing output is preserved. Choose a new directory.")
dir.create(out, recursive=TRUE)
src <- file.path(root, "analysis/2026-10-01/counts")
read <- function(p) read.delim(p, check.names=FALSE, colClasses="character")
dat <- read(file.path(src, "counts_raw.txt")); ids <- dat$ENTREZID
cts <- as.matrix(dat[,-1]); storage.mode(cts) <- "numeric"; rownames(cts) <- ids
m <- read(file.path(src, "sample_annotation.txt")); ann <- read(file.path(src,"annotate_geneID.txt"))
stopifnot(nrow(cts)==28395, ncol(cts)==17, !anyDuplicated(ids), !anyDuplicated(m$sample_name),
          identical(colnames(cts),m$sample_name), all(is.finite(cts)), all(cts>=0), all(cts==floor(cts)),
          !anyDuplicated(ann$ENTREZID))
ann <- ann[match(ids,ann$ENTREZID),]; stopifnot(identical(ann$ENTREZID,ids))
groups <- paste(m$cell_line, m$condition, sep="_"); ordered <- unique(groups)
merged <- sapply(ordered,function(g) rowSums(cts[,groups==g,drop=FALSE])); rownames(merged)<-ids
cm <- m[match(ordered,groups),c("cell_line","condition")]
cm$source_runs <- vapply(ordered,function(g) paste(m$run_accession[groups==g],collapse=";"), "")
cm$condition <- factor(ifelse(cm$condition=="KRAS","Treatment","Control"),levels=c("Control","Treatment"))
cm$cell_line <- factor(cm$cell_line); rownames(cm)<-colnames(merged)<-ordered
stopifnot(ncol(merged)==16,all(table(cm$cell_line,cm$condition)==1),
          identical(as.numeric(merged[,"MiaPaca-2_KRAS"]),as.numeric(rowSums(cts[,m$run_accession %in% c("SRR24828471","SRR24828472"),drop=FALSE]))))
write <- function(x,name,d=out) write.table(x,file.path(d,name),sep="\t",quote=FALSE,row.names=FALSE,na="NA")
wm <- function(x,name,d=out) write(data.frame(ENTREZID=rownames(x),x,check.names=FALSE),name,d)
wm(merged,"merged_counts.tsv"); write(data.frame(sample=rownames(cm),cm),"merged_samples.tsv")
lines <- levels(cm$cell_line)
rounds <- c("full",paste0("omit_",lines)); summary <- list(); coverage <- list()
for (round in rounds) {
  omitted <- if(round=="full") "NONE" else sub("^omit_","",round)
  message("START ", round)
  use <- if(round=="full") rep(TRUE,nrow(cm)) else as.character(cm$cell_line)!=omitted
  mm <- droplevels(cm[use,,drop=FALSE]); cc <- merged[,use,drop=FALSE]
  design <- model.matrix(~condition+cell_line,mm); coef <- which(colnames(design)=="conditionTreatment")
  expected_n <- if(round=="full") 16L else 14L
  stopifnot(ncol(cc)==expected_n, all(table(mm$cell_line,mm$condition)==1),qr(design)$rank==ncol(design),
            length(coef)==1, ncol(design)==if(round=="full") 9L else 8L)
  coverage[[round]] <- data.frame(round=round,omitted_cell_line=omitted,retained_cells=paste(levels(mm$cell_line),collapse=";"),
    excluded_samples=paste(rownames(cm)[!use],collapse=";"),excluded_runs=paste(cm$source_runs[!use],collapse=";"),
    observations=ncol(cc),design_columns=ncol(design),design_rank=qr(design)$rank,residual_df=nrow(mm)-ncol(design))
  d <- file.path(out,round); dir.create(d)
  write(data.frame(sample=rownames(mm),mm),"samples.tsv",d)
  write(data.frame(sample=rownames(design),design,check.names=FALSE),"design.tsv",d)
  keep <- rowSums(cc>=10)>=2
  write(data.frame(ENTREZID=ids,prefilter_pass=keep,samples_count_ge10=rowSums(cc>=10)),"filter.tsv",d)
  dds <- DESeqDataSetFromMatrix(cc[keep,,drop=FALSE],mm,~condition+cell_line)
  dds <- DESeq(dds,quiet=TRUE)
  res <- results(dds,contrast=c("condition","Treatment","Control"),alpha=0.05)
  rev <- results(dds,contrast=c("condition","Control","Treatment"),alpha=0.05)
  stopifnot(isTRUE(all.equal(res$log2FoldChange,-rev$log2FoldChange)),isTRUE(all.equal(res$pvalue,rev$pvalue)))
  shr <- lfcShrink(dds,coef="condition_Treatment_vs_Control",res=res,type="apeglm",quiet=TRUE)
  de <- as.data.frame(res); de$log2FC_apeglm <- shr$log2FoldChange; de$apeglm_posterior_SD <- shr$lfcSE
  de$beta_converged <- mcols(dds)$betaConv
  de$status <- ifelse(is.na(de$pvalue),"pvalue_unavailable_Cooks_or_all_zero",ifelse(is.na(de$padj),"independent_filtered","tested"))
  deg <- calcNormFactors(DGEList(cc[keep,,drop=FALSE]),method="TMM")
  deg <- estimateDisp(deg,design,robust=TRUE)
  fit <- glmQLFit(deg,design,robust=TRUE)
  qlf <- glmQLFTest(fit,coef=coef)
  reverse <- rep(0,ncol(design)); reverse[coef] <- -1
  errev <- glmQLFTest(fit,contrast=reverse)$table
  stopifnot(isTRUE(all.equal(qlf$table$logFC,-errev$logFC)),isTRUE(all.equal(qlf$table$PValue,errev$PValue)))
  er <- topTags(qlf,n=Inf,adjust.method="BH",sort.by="none")$table; er$status <- "tested"
  stopifnot(identical(rownames(de),rownames(er)))
  full <- function(x) { a<-ann; index<-match(ids,rownames(x)); for(k in names(x)) a[[k]]<-x[[k]][index]
    a$prefilter_pass<-keep; a$status[!keep]<-"low_count_prefilter"; a }
  df <- full(de); ef <- full(er); write(df,"DESeq2_full.tsv",d); write(ef,"edgeR_full.tsv",d)
  gates <- list(DESeq2_unshrunk=which(df$padj<0.05 & abs(df$log2FoldChange)>0.5),
                DESeq2_apeglm=which(df$padj<0.05 & abs(df$log2FC_apeglm)>0.5),
                edgeR=which(ef$FDR<0.05 & abs(ef$logFC)>0.5))
  summary[[round]] <- data.frame(round=round,prefilter_genes=sum(keep),DESeq2_finite_p=sum(is.finite(df$pvalue)),
    DESeq2_finite_padj=sum(is.finite(df$padj)),DESeq2_beta_nonconverged=sum(!de$beta_converged,na.rm=TRUE),
    DESeq2_FDR05=sum(df$padj<0.05,na.rm=TRUE),edgeR_FDR05=sum(ef$FDR<0.05,na.rm=TRUE),
    DESeq2_unshrunk_gate=length(gates$DESeq2_unshrunk),DESeq2_apeglm_gate=length(gates$DESeq2_apeglm),edgeR_gate=length(gates$edgeR),
    intersection_unshrunk=length(intersect(gates$DESeq2_unshrunk,gates$edgeR)),intersection_apeglm=length(intersect(gates$DESeq2_apeglm,gates$edgeR)))
  write(data.frame(sample=rownames(mm),size_factor=sizeFactors(dds),TMM_factor=deg$samples$norm.factors,
    library_size=deg$samples$lib.size),"normalization.tsv",d)
  write_json(list(round=round,model="~condition+cell_line",contrast="Treatment (KRAS siRNA) / Control",
    prefilter="count >=10 in at least 2 retained observations; recalculated each fit",zero_effect_null=TRUE,
    screen="FDR<0.05 and abs(unshrunk log2FC)>0.5, after testing",alpha=0.05,
    independent_filter_threshold=unname(metadata(res)$filterThreshold),edgeR_legacy=FALSE,
    reverse_contrast_verified=TRUE,P5="raw integer counts summed before filtering and normalization; repeat identity unresolved"),
    file.path(d,"method_metadata.json"),pretty=TRUE,auto_unbox=TRUE,digits=16)
  write(do.call(rbind,summary),"round_summary.tsv"); write(do.call(rbind,coverage),"round_coverage.tsv")
  message("DONE ",round)
}
stopifnot(length(coverage)==9,length(unique(sub("^omit_","",rounds[-1])))==8)
write(data.frame(Package=rownames(installed.packages()),Version=installed.packages()[,"Version"]),"package_versions.tsv")
capture.output(sessionInfo(),file=file.path(out,"sessionInfo.txt"))
message("ALL NINE FITS COMPLETE")
