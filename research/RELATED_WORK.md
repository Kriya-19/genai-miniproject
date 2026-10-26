# Related work

This file is intentionally conservative. References must be checked against
the cited DOI or stable publisher/repository page before publication. The
comparison describes what this repository implements; “not established” means
the available source does not support a stronger claim.

## Verified references

The following references were checked against the DOI or official publisher/
proceedings record. The DxGPT item is a preprint and is labeled accordingly.

| Work | Relevance to DiagnoSure |
|---|---|
| **Evaluation of the Clinical Utility of DxGPT, a GPT-4 Based Large Language Model, through an Analysis of Diagnostic Accuracy and User Experience** (Alvarez-Estape et al., 2024, medRxiv preprint, [DOI](https://doi.org/10.1101/2024.07.23.24310847)) | Directly evaluates a GPT-4-based diagnostic assistant. It is a preprint, not peer-reviewed evidence, and is not a direct benchmark for this implementation. |
| **Clinical Decision Support and Natural Language Processing in Medicine: Systematic Literature Review** (Eguia et al., 2024, *Journal of Medical Internet Research*, [DOI](https://doi.org/10.2196/55315)) | Reviews NLP and AI methods in clinical decision support and provides context for the application-level workflow. |
| **MedAgents: Large Language Models as Collaborators for Zero-shot Medical Reasoning** (Tang et al., 2024, *Findings of ACL 2024*, [DOI](https://doi.org/10.18653/v1/2024.findings-acl.33)) | Multi-agent role-based medical reasoning; relevant to the orchestration concept but uses different tasks and benchmarks. |
| **MDAgents: An Adaptive Collaboration of LLMs for Medical Decision-Making** (Kim et al., 2024, *NeurIPS 2024*, [DOI](https://doi.org/10.52202/079017-2522)) | Studies adaptive solo/group medical-agent collaboration and moderator/external-knowledge effects; DiagnoSure uses a fixed sequential workflow instead. |
| **ReasonMed: A 370K Multi-Agent Generated Dataset for Advancing Medical Reasoning** (Sun et al., 2025, *EMNLP 2025*, [DOI](https://doi.org/10.18653/v1/2025.emnlp-main.1344)) | Multi-agent generation, verification and refinement of medical reasoning data; relevant to evaluation design, not an implementation match. |
| **Retrieval augmented generation for large language models in healthcare: A systematic review** (Amugongo et al., 2025, *PLOS Digital Health*, [DOI](https://doi.org/10.1371/journal.pdig.0000877)) | Reviews healthcare retrieval-augmented systems, grounding and evaluation limitations. DiagnoSure uses public API retrieval and generated summaries rather than vector RAG. |
| **Explainable AI in hospital clinical decision support systems: A scoping review of healthcare professionals’ perspectives** (Van Dort et al., 2026, *PLOS Digital Health*, [DOI](https://doi.org/10.1371/journal.pdig.0001417)) | Supports evaluating explanation usefulness, workflow fit, data quality and overreliance concerns. DiagnoSure's report is generated text, not feature attribution. |
| **Patient-Centered Digital Health Records and Their Effects on Health Outcomes: Systematic Review** (Brands et al., 2022, *Journal of Medical Internet Research*, [DOI](https://doi.org/10.2196/43086)) | Relevant to the Health Passport and patient-record component, though it does not evaluate DiagnoSure's model workflow. |
| **WHO guideline: recommendations on digital interventions for health system strengthening** (World Health Organization, 2019, WHO guideline, [stable record](https://iris.who.int/handle/10665/311941)) | Policy context for digital-health and patient-record workflows; not an LLM evaluation. |

These references are not evidence that DiagnoSure matches their methods or
results. A final paper should verify full author lists, venue metadata,
licensing and claims from the original publications.

## Comparison matrix

| System/paper | Diagnostic approach | Multi-agent coordination | Literature retrieval | Case-study retrieval | Explainability | Patient-facing integration |
|---|---|---|---|---|---|---|
| DiagnoSure implementation | symptom extraction + primary diagnosis agent | Yes, sequential orchestrator | Yes, public PubMed/trials | Yes, PubMed case reports | generated report and warnings; no feature attribution | Yes |
| Med-PaLM | medical LLM evaluation | Not established as multi-agent from cited work | Not established as this application workflow | Not established | evaluation and safety work, not this report | No |
| MedRAG | retrieval-augmented medical QA | Not established as DiagnoSure-style agents | Yes, retrieval-augmented | Not established | generated answers; methodology differs | No |
| General RAG method | retrieve then generate | No | Yes, general knowledge retrieval | No | not a medical explainability method | No |
| XAI systematic review | review of explanation methods | No single system | Not applicable | Not applicable | taxonomy of methods | Not applicable |

## Cautious research gap

The selected literature separately studies LLM diagnostic accuracy, multi-agent
medical reasoning, retrieval grounding, explainability and patient-centered
digital records. A cautious proposed gap is whether one patient-facing
decision-support prototype can combine these components while being evaluated
end-to-end for diagnostic accuracy, evidence citation quality, explanation
usefulness, record-context handling, uncertainty communication and clinician
oversight. This is an integration-and-evaluation question, not a claim that no
prior system has combined these elements.
