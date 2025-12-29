# OCR Product Specification Extraction Pipeline

## Overview
This project implements an end-to-end OCR and data extraction pipeline
that converts unstructured product specification images into structured CSV data.

It is designed for real-world data cleaning tasks where OCR output is noisy,
fields are inconsistently formatted, and business rules affect which fields
are expected.

## Pipeline Stages
1. OCR text ingestion (pre-generated CSV)
2. Text normalization
3. Rule-based field extraction with fallbacks
4. Device power-type classification
5. Field coverage analysis

## Extracted Fields
- model
- voltage_v
- power_w
- charging_time_h
- runtime_min
- weight_g
- color
- power_source
- battery_possible

## Project Structure
- data/
  - images/
  - ocr/
  - processed/
- scripts/
  - run_pipeline.py
  - classify_power_type.py
  - analyze_field_coverage_by_power_type.py
  - debug_charging_time_candidates.py
- src/
  - clean_text.py

## How to Run
```bash
python scripts/run_pipeline.py
