// Build: typst compile report/MS1report.typ. The text lives in MS1report.md; this file only sets the layout.
#import "@preview/cmarker:0.1.6"

#set document(title: "Milestone 1 Report", author: ("Rowen Ess", "Austin Sternberg", "Will Nahra"))
#set page(paper: "us-letter", margin: 1in, numbering: "1")
#set text(font: "Times New Roman", size: 11pt)
#set par(justify: true, leading: 0.6em, spacing: 0.9em)
#show heading: set text(size: 12pt)
#show heading: set block(above: 1.1em, below: 0.6em)
#show raw: set text(size: 10pt)
#show link: set text(fill: rgb("#1a5fb4"))
#set table(stroke: 0.5pt + rgb("#c9c9c9"), inset: 4pt)
#show table: set text(size: 9pt)
#show table: set par(justify: false)
#show list: set text(size: 9pt)
#show list: set par(leading: 0.5em)

#align(center)[
  #block(below: 0.8em, text(size: 16pt, weight: "bold")[Milestone 1 Report])
  Rowen Ess, Austin Sternberg, Will Nahra
]

// Readable table text needs the threat model at full width; false_positives.png is natively 4.6 in wide.
#let fit(path) = if path.contains("threat_model") { 100% } else if path.contains("false_positives") { 60% } else { 82% }

#cmarker.render(
  read("MS1report.md"),
  scope: (image: (path, alt: none) => block(sticky: true, width: 100%, align(center, image(path, alt: alt, width: fit(path))))),
)
