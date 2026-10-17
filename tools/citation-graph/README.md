# Citation graph (homepage source)

The ercref.org homepage (`/index.html`) is a force-directed graph of every
Final EIP and ERC and their authors. This folder holds the source that builds it.

```
tools/citation-graph/
├── template.html     page markup, styles and graph code; __DATA__ and __DATE__ are placeholders
├── pagerank.py       parses EIP/ERC front matter, builds the citation graph, runs PageRank
├── export_graph.py   turns the result into graph JSON and writes /index.html
└── build.sh          one command: fetch repos and avatars, then write /index.html
```

## How the scores work

- A citation is an `EIP-N` or `ERC-N` mention, a link to `eip-N.md` or `erc-N.md`,
  or an entry in `requires:`. PageRank runs over all non-Moved EIPs and ERCs
  (damping 0.85). Scores are scaled so the average document is 1.00.
- Each Final document's score is shared among its authors by author order.
  With n authors, the first author gets n parts and the last author gets 1 part.
- An author's score is the sum of their shares over all Final documents.

## Rebuild the page

```sh
tools/citation-graph/build.sh
```

The script needs `git`, `curl`, `python3` and macOS `sips`. It caches clones and
avatars in `tools/citation-graph/.work/` (git-ignored). The page loads d3 from cdnjs
and embeds all other data, so it works as a static GitHub Pages file.
