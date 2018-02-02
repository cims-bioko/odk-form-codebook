# ODK Form Codebook

A simple python script for describing multiple-choice questions from an ODK xform definition. It
works by inspecting the xform (xml, not the xls precursor form) and generating the lists based on
the form design.

## Usage

The following example generates a code book for a fictional xform definition, `formdef.xml`:

```shell
# Generate a code listing using embedded English translations
./form_codes.py --lang English formdef.xml
```

