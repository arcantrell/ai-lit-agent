# Demo Workflow

This walkthrough is designed for reviewers who want to understand the project quickly.

## 1. Start The App

```bash
python -m pip install -e .
lit-agent-app
```

Open:

```text
http://127.0.0.1:8000
```

## 2. Search For Papers

Search:

```text
galactose metabolism mouse brain
```

Suggested filters:

- From year: 2019
- To year: 2026
- Sort: Newest first

Save one or two relevant papers into the library.

Use the Previous and Next buttons to move through additional PubMed result pages.

## 3. Create A Research Briefing

Create a briefing named:

```text
Mouse brain metabolism
```

Add terms:

```text
galactose metabolism mouse brain
fucose metabolism mouse brain
astrocyte glycogen metabolism
```

Then click:

```text
Run Briefing
```

The app will search the saved terms, generate a Research Briefing, and show candidate paper cards. Save only the candidate papers you want in the library.

## 4. Import A PDF

Use the library's PDF import control to add a downloaded paper.

The app will:

- extract searchable text
- look for a DOI
- fetch citation metadata when possible
- allow manual citation editing when no DOI is available
- save the PDF record into the library
- show an Open PDF link on saved records with attached files

## 5. Export Citations

Use the BibTeX, BibTeX + PDFs, or RIS buttons to export the local library for citation managers such as Zotero, Mendeley, EndNote, or Paperpile.

When saved papers have attached PDFs, use BibTeX + PDFs to download a ZIP file containing the `.bib` file and the PDFs together. PDFs in the export package use first-author/year names, such as `Soares_2010.pdf`.

Each saved paper card also includes one-paper BibTeX and BibTeX + PDF export actions.
