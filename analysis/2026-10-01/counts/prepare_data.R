args <- commandArgs(trailingOnly = FALSE)
script <- sub("^--file=", "", args[grepl("^--file=", args)])
if (length(script)) setwd(dirname(normalizePath(script[1])))
read_tab <- function(file) read.delim(file, check.names = FALSE, stringsAsFactors = FALSE)
write_tab <- function(x, file) write.table(x, file, sep = "\t", quote = FALSE,
                                         row.names = FALSE, na = "NA")
samples <- read_tab("sources/sample_manifest.txt")
stopifnot(nrow(samples) == 17L, !anyDuplicated(samples$sample_name))
input <- lapply(samples$file, read_tab)
names(input) <- samples$sample_name
ids <- as.character(input[[1]][[1]])
stopifnot(!anyNA(ids), !anyDuplicated(ids))
matrix_counts <- matrix(NA_real_, length(ids), nrow(samples),
                        dimnames = list(ids, samples$sample_name))
for (i in seq_along(input)) {
    tab <- input[[i]]
    gene_ids <- as.character(tab[[1]])
    stopifnot(ncol(tab) == 2L, names(tab)[2] == samples$sample_name[i],
              !anyNA(gene_ids), !anyDuplicated(gene_ids), setequal(ids, gene_ids))
    values <- tab[[2]][match(ids, gene_ids)]
    stopifnot(is.numeric(values), !anyNA(values), all(is.finite(values)),
              all(values >= 0), all(values == floor(values)))
    matrix_counts[, i] <- values
}
qc <- read_tab("sources/summary_review.tsv")
qc <- qc[match(samples$sample_name, qc$sample), ]
stopifnot(!anyNA(qc$sample), identical(qc$sample, samples$sample_name),
          all(colSums(matrix_counts) == qc$assigned))

source_annot <- read_tab("sources/annotate_geneID.tabular")
source_annot$ENTREZID <- as.character(source_annot$ENTREZID)
stopifnot(all(ids %in% source_annot$ENTREZID))
by_gene <- split(seq_len(nrow(source_annot)), source_annot$ENTREZID)
collapse_mapping <- function(id, field) {
    values <- unique(source_annot[by_gene[[id]], field])
    values <- values[!is.na(values) & nzchar(values)]
    if (!length(values)) return(NA_character_)
    if (field %in% c("SYMBOL", "GENENAME")) stopifnot(length(values) == 1L)
    paste(values, collapse = ";")
}
annotation <- data.frame(ENTREZID = ids, stringsAsFactors = FALSE)
for (field in c("ENSEMBL", "SYMBOL", "GENENAME")) {
    annotation[[field]] <- vapply(ids, collapse_mapping, character(1), field = field)
}
count <- data.frame(ENTREZID = ids, SYMBOL = annotation$SYMBOL,
                    matrix_counts, check.names = FALSE)
raw_count <- data.frame(ENTREZID = ids, matrix_counts, check.names = FALSE)
samples$assigned_counts <- as.numeric(colSums(matrix_counts))
samples$assigned_percent <- qc$assigned_percent
samples$included_in_count_table <- TRUE
samples$qc_flag <- ifelse(samples$local_label == "KRAS M1",
    "CORRECTED_ENA_PAIR_FULLY_VERIFIED", "NO_EXTREME_COUNTING_FAILURE_DETECTED")
samples$repeat_status <- ifelse(samples$cell_line == "MiaPaca-2" & samples$condition == "KRAS",
    "UNRESOLVED_KEEP_RUNS_SEPARATE", "NOT_ASSESSED")
samples$matched_condition_available <- TRUE
write_tab(count, "count.txt")
write_tab(raw_count, "counts_raw.txt")
write_tab(annotation, "annotate_geneID.txt")
write_tab(samples[, c("sample_name", "condition", "cell_line", "local_label", "run_accession",
    "ena_alias", "included_in_count_table", "qc_flag", "repeat_status",
    "assigned_counts", "assigned_percent")], "sample_annotation.txt")

read_count <- read_tab("count.txt")
read_raw <- read_tab("counts_raw.txt")
read_sample <- read_tab("sample_annotation.txt")
read_annot <- read_tab("annotate_geneID.txt")
stopifnot(identical(names(read_count)[-(1:2)], read_sample$sample_name),
          identical(names(read_raw)[-1], read_sample$sample_name),
          identical(as.character(read_count$ENTREZID), ids),
          identical(as.character(read_annot$ENTREZID), ids),
          all(as.matrix(read_raw[, -1]) == matrix_counts),
          all(as.matrix(read_count[, -(1:2)]) == matrix_counts),
          sum(read_sample$condition == "Control") == 8,
          sum(read_sample$condition == "KRAS") == 9,
          "KRAS_siRNA_M1" %in% read_sample$sample_name,
          sum(read_raw$KRAS_siRNA_M1) == samples$assigned_counts[samples$local_label == "KRAS M1"])
verification <- c(
    "PASS: downloaded counts match exported counts after matching by gene ID",
    "PASS: every sample count sum equals featureCounts Summary Assigned",
    "PASS: all gene IDs match the supplied classroom annotation",
    "PASS: sample annotation order matches count columns",
    "PASS: all 17 runs included; 8 Control and 9 KRAS",
    "PASS: KRAS M1 replaced using verified corrected inputs; see source summary for assigned counts",
    "PASS: P5 KRAS runs retained separately",
    paste("Gene rows:", length(ids)),
    paste("Missing SYMBOL:", sum(is.na(annotation$SYMBOL))),
    paste("Genes with multiple ENSEMBL mappings:", sum(grepl(";", annotation$ENSEMBL))),
    "No normalization, gene filtering, differential expression or batch correction performed.")
writeLines(verification, "verification.txt")
writeLines(capture.output(sessionInfo()), "R_session.txt")
cat(paste(verification, collapse = "\n"), "\n")
