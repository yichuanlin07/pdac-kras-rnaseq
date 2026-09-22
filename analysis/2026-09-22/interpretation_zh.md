# 结果怎么理解

本记录区分已经验证的结果和仍在修复的任务。原始数据、失败任务和历史报告全部保留。

## HISAT2：完成的是试跑，不是全量分析

六个任务各用了前 100 万对读段。Control M1 的总体比对率为 96.63%，KRAS P1 为 96.40%。这里的“总体”以单条读段计算；“成对且唯一比对”以读段对计算，分别约为 86.40%–86.44% 和 87.43%。两种百分比不是同一个指标。

这说明两个试跑输入大部分能比对到人类 hg38 参考基因组。它不证明 KRAS 敲低成功，也不能代替基因计数或差异表达分析。Control M1 是 Pa01C，KRAS P1 是 Pa16C，不能直接把它们的差别归因于处理。FR 和 RF 结果相同，也不足以判断文库链方向。

## 三种“重复”不要混淆

1. **重复上传文件**：同一文件在存储中出现多次，需要按来源和校验值核对。
2. **重复实验或测序运行**：两个 MiaPaca-2 KRAS 记录有不同的运行号、实验号和 BioSample 号。ENA 将其中一个标记为重复，但没有说明是生物学重复、技术重复还是重做的实验。不能自动删除或合并。
3. **FastQC 序列重复**：一个 FASTQ 文件里出现相同读段序列。高表达转录本可以造成这种现象，PCR 扩增也可能贡献重复；不能仅凭该指标区分原因。

M1–M3 对应转移来源细胞系，P1–P5 对应原发肿瘤来源细胞系。它们不是同一个患者的原发/转移配对样本。分析 KRAS 处理效果时，应在同一细胞系内对应 Control 和 KRAS。

## FastQC 的红色 Fail 不等于程序运行失败

碱基组成 Fail 检查的是读段各位置 A/T、G/C 比例是否平衡，不是测序碱基的可信度。RNA 文库的引物和建库偏好可能造成位置偏差。序列重复 Fail 也不等于文件损坏。不能为了让页面“全绿”而盲目截短读段或去重。

SRR24828471 两端都有 GC 分布 Warn。已查看的 R2 图形大致为钟形，但高 GC 一侧有肩部，偏离理论分布；未见明显孤立尖峰。警告并不确定证明污染，原因仍需结合比对结果和必要的污染检查判断。整体 GC 百分比落在其他样本范围内，也不能取代分布检查。

真正的运行错误是另一回事：SRR24828471 的两次 R1 在线导入都被截断，FastQC 读到半条记录时退出；原 R2 则导入失败。完整本地副本已完成 FastQC，R1 的全部序列和质量值也与通过 ENA 校验值验证的完整文件一致。Galaxy 已用 SRA Toolkit 恢复完整配对集合 156（R1 为 175，R2 为 176）。额外的 Galaxy FastQC 复核也已完成：两端各 37,886,040 条、150 bp、51% GC，所有模块状态与本地结果一致。

现在的 MultiQC **165** 已完整汇总 34 个文件：32 份 Galaxy FastQC 加两份本地补跑结果。重复率为 57.0%–67.3%；GC 分布为 32 个 Pass、两个 Warn。所谓“检查完成”不等于每一个模块都为 Pass。旧错误副本保留并标记停用，旧暂停报告 148 不再作为最新结果。

资料：[FastQC 碱基组成说明](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/4%20Per%20Base%20Sequence%20Content.html)、[序列重复说明](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/8%20Duplicate%20Sequences.html)、[GC 分布说明](https://www.bioinformatics.babraham.ac.uk/projects/fastqc/Help/3%20Analysis%20Modules/5%20Per%20Sequence%20GC%20Content.html)。
