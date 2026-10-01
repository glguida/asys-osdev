---
name: exokernel
description: The MIT Exokernel literature (Engler, Kaashoek et al., 1994-2002) as local PDFs with searchable text. Use when reasoning about exokernel design (secure bindings, visible revocation, the abort protocol, library operating systems, XN and UDFs, DPF, ASHs, application-level virtual memory), when comparing an OS design with Aegis, Xok or ExOS, or when an argument needs a citation from Dawson Engler's theses or the exokernel papers.
---

# MIT Exokernel literature

Local copies of the exokernel project's papers and theses, all downloaded from
pdos.csail.mit.edu. Every `papers/NAME.pdf` has a `papers/NAME.txt` made with
`pdftotext -layout`.

Start with [papers/INDEX.md](papers/INDEX.md). It gives each file's full
citation, source URL and a short summary, grouped by topic.

## Where to look

- The architecture, stated in full: `engler-1998-phd-thesis-exokernel-architecture`.
- The defining paper (secure bindings, visible revocation, abort protocol,
  Aegis/ExOS on MIPS): `engler-1995-sosp-exokernel-architecture`.
- The x86 system (Xok/ExOS, XN, application performance):
  `kaashoek-1997-sosp-application-performance-flexibility-exokernel`.
- The first prototype in detail: `engler-1995-ms-thesis-prototype-exokernel`.
- The philosophy: `engler-1995-hotos-exterminate-all-os-abstractions`.
- Application-level virtual memory: `engler-1995-hotos-avm-application-level-virtual-memory`.
- Network multiplexing: DPF, ASHs, Wallach's thesis and Ganger's TOCS 2002 paper.
- The later MIT theses cover the disk (ExoDisk), shared libraries, sharing
  protected abstractions, multiprocessing and an x86 VMM on Xok.
- `pdos-exokernel-project-pages.txt` snapshots the original project pages.

## Searching

Search the text files, then read the surrounding pages:

```sh
cd /opt/asys/environment/skills/exokernel/papers
rg -n -i "secure binding" *.txt
rg -n -i -C3 "abort protocol" engler-1995-sosp-exokernel-architecture.txt
pdftotext -f 40 -l 45 -layout engler-1998-phd-thesis-exokernel-architecture.pdf -
```

Several older TeX documents lose their fi/fl/ff ligatures in extraction, so
words such as "efficient" may appear as "ecient". A fix-up pass restored the
common words, but search for a stem (`rg "fici|cient"`) or check the PDF when
a word seems missing.

When you rely on a paper, cite the file and the section or page. The two
`*-talk-slides-*` files are slides with little text; use the papers for claims.
