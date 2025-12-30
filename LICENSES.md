# Third-Party Licenses

This document lists the licenses for all third-party dependencies used in print-daily.

## Summary

| Package | Version | License | Commercial Use |
|---------|---------|---------|----------------|
| reportlab | >=4.0 | BSD-3-Clause | Yes |
| requests | >=2.28 | Apache-2.0 | Yes |
| PyPDF2 | >=3.0 | BSD-3-Clause | Yes |
| python-dotenv | >=1.0 | BSD-3-Clause | Yes |

All dependencies use permissive open-source licenses that allow commercial use, modification, and redistribution.

---

## reportlab

- **License**: BSD-3-Clause
- **Copyright**: Copyright (c) 2000-2024, ReportLab Inc.
- **PyPI**: https://pypi.org/project/reportlab/
- **Description**: PDF generation library for Python

The BSD-3-Clause license permits:
- Commercial use
- Modification
- Distribution
- Private use

Requirements:
- Include copyright notice and license text in distributions

---

## requests

- **License**: Apache-2.0
- **Copyright**: Copyright 2019 Kenneth Reitz
- **PyPI**: https://pypi.org/project/requests/
- **GitHub**: https://github.com/psf/requests
- **Description**: HTTP library for Python

The Apache 2.0 license permits:
- Commercial use
- Modification
- Distribution
- Patent use
- Private use

Requirements:
- Include copyright notice and license text
- State changes made to the code
- Include NOTICE file if present

---

## PyPDF2

- **License**: BSD-3-Clause
- **Copyright**: Copyright (c) 2006-2008, Mathieu Fenniak; Copyright (c) 2022, Martin Thoma
- **PyPI**: https://pypi.org/project/PyPDF2/
- **Description**: PDF manipulation library for Python

The BSD-3-Clause license permits:
- Commercial use
- Modification
- Distribution
- Private use

Requirements:
- Include copyright notice and license text in distributions

---

## python-dotenv

- **License**: BSD-3-Clause
- **Copyright**: Copyright (c) 2014, Saurabh Kumar
- **PyPI**: https://pypi.org/project/python-dotenv/
- **GitHub**: https://github.com/theskumar/python-dotenv
- **Description**: Reads key-value pairs from .env files and sets them as environment variables

The BSD-3-Clause license permits:
- Commercial use
- Modification
- Distribution
- Private use

Requirements:
- Include copyright notice and license text in distributions

---

## License Compatibility

All dependencies use permissive licenses (BSD-3-Clause and Apache-2.0) that are compatible with each other and with most open-source and proprietary licenses. This project can be distributed under any license without conflict.

## External APIs (Not Bundled)

This project also uses external APIs that are not bundled as dependencies:

| Service | Purpose | Terms |
|---------|---------|-------|
| Guardian API | News content | [Guardian API Terms](https://open-platform.theguardian.com/documentation/) |
| Open-Meteo | Weather data | [Open-Meteo Terms](https://open-meteo.com/en/terms) - Free for non-commercial use |
| Anthropic Claude API | AI summarization | [Anthropic Terms](https://www.anthropic.com/policies/consumer-terms) |
| Readwise API | Reading highlights | [Readwise Terms](https://readwise.io/terms) |

Users must comply with each API's terms of service independently.
