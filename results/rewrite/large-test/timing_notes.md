# Timing limitations

`editing_log.csv` preserves the editors' recorded wall-clock observations. These are not all independent
per-passage editing times. Do not sum the column or use it as a clean cost benchmark.

- Batch 1 shared an opening/working interval for `35-0023`, `S20-0221`, `145-1043`, `5200-0002`, and `S10-0041`.
  Those five originals had also appeared in an earlier grouped read before their recorded interval began.
  Sequential timing began with its sixth passage.
- Batch 2 shared intervals for `43-0050`, `11-0143`, `1342-0338`, `1184-1175`, `1400-0494`, `S29-0011`,
  `S29-0032`, and `120-0080`. The first four also exclude the initial reading.
- Batch 2's next eight observations include individual rereading but exclude earlier grouped reading:
  `S25-0059`, `345-0497`, `2701-0449`, `46-0125`, `33-0059`, `11-0005`, `1260-0353`, and `55-0119`.
  `S25-0059` and `1260-0353` also received final corrections after their recorded intervals ended.
  Its remaining passages were first opened after their individual timers began.
- Batch 3 shared intervals for its first 13 passages: `84-0053`, `S21-0251`, `S23-0008`, `205-0038`,
  `2554-0278`, `S05-0266`, `S22-0272`, `1400-0743`, `174-0227`, `145-0710`, `S18-0017`, `S24-0023`, and `S27-0032`.
  Sequential timing began at `S11-0005`.

These limitations affect 34 of the 100 observations. The remaining 66 use individual starts before the first
reading. All observations include environment and tool latency, so they are not model-only timing measurements.
The editors reported no per-passage 15-minute limit violations. Detection results are independent of these
timing measurements; quality judgments still require the separate blind review.
