# Project Status

Prototype scope: educational/hackathon use only. The system assists human review and must not automatically make real-world immigration or security decisions.

- [x] Repository scaffold
- [x] Minimal FastAPI service and health endpoint
- [x] Basic React/Vite frontend scaffold
- [x] Module 1: document upload and image preprocessing
- [ ] Document type detection
- [x] Integrate PaddleOCR and FastAPI
- [x] Field extraction (name, DOB, passport number, issue/expiry dates)
- [x] Confidence score inclusion

### Module 3: Document Validation
- [x] Field presence and format validation
- [x] Date logic (expired, future DOB, etc.)
- [x] Checksum and MRZ parsing
- [x] Cross-field consistency (Visual ↔ MRZ)
- [x] Validation API endpoint integration
- [x] Tampering/manipulation detection (Classical heuristics)
- [ ] Face verification using only consented/synthetic data (IN DEVELOPMENT)
- [ ] Explainable risk scoring for human review
- [ ] Explainable screening report
- [ ] React dashboard
- [ ] Automated tests and deployment documentation
