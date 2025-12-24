# Project Requirements

## 1. Data Source
- The source data is provided as Microsoft Word documents.
- Each document contains multiple product images.
- Product specifications (model, parameters, dimensions, etc.) are embedded within the images as text.

## 2. Data Extraction Scope
- Extract product-related information from images inside Word documents.
- Text extraction will be performed using OCR.
- Each product image represents one product entry.

## 3. Input Format
- File format: .docx
- Images embedded in the document
- Language: Chinese (Simplified)

## 4. Output Format
- File format: CSV
- Encoding: UTF-8
- One row per product
- Each column represents a standardized product attribute

## 5. Primary Key Definition
- A product is considered unique by the combination of:
  - product_model
  - product_name

## 6. Required Fields
The following fields must be extracted and standardized:
- product_name
- product_model
- brand (if available)
- key_specifications (structured fields where possible)
- source_document_name

## 7. Data Handling Rules
- If a field cannot be reliably extracted, it should be left empty.
- Low-confidence OCR results should be flagged.
- Duplicate products should be deduplicated based on the primary key.
- All extracted text should be normalized to a consistent format.