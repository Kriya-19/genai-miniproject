




class ExplainabilityAgent:
    def __init__(self):
        self.name = "ExplainabilityAgent"
        self.version = "1.0.0"

    def generate_explainability_report(
        self,
        top_diagnosis: dict,
        all_diagnoses: list,
        literature_validation: str,
        case_study_validation: str,
    ) -> str:
        report_parts = []

        # Section 1: Top Diagnosis with details
        report_parts.append("=== Top Diagnosis ===")
        if top_diagnosis and isinstance(top_diagnosis, dict):
            condition = top_diagnosis.get("condition", "Unknown")
            confidence = top_diagnosis.get("confidence", 0.0)
            medications = top_diagnosis.get("medications", [])
            precautions = top_diagnosis.get("precautions", [])
            exercises = top_diagnosis.get("exercises", [])
            diet = top_diagnosis.get("diet", [])

            report_parts.append(f"Condition: {condition}")
            report_parts.append(f"Ranking score (not medical probability): {confidence:.2f}")
            if medications:
                report_parts.append("Medications:")
                for med in medications:
                    report_parts.append(f"  - {med}")
            if precautions:
                report_parts.append("Precautions:")
                for prec in precautions:
                    report_parts.append(f"  - {prec}")
            if exercises:
                report_parts.append("Exercises:")
                for ex in exercises:
                    report_parts.append(f"  - {ex}")
            if diet:
                report_parts.append("Diet:")
                for d in diet:
                    report_parts.append(f"  - {d}")
        else:
            report_parts.append("No top diagnosis information available.")

        # Section 2: Top 5 Diagnoses with ranking scores
        report_parts.append("\n=== Top 5 Diagnoses ===")
        if all_diagnoses and isinstance(all_diagnoses, list):
            for i, diag in enumerate(all_diagnoses[:5], start=1):
                condition = diag.get("condition", "Unknown")
                confidence = diag.get("confidence", 0.0)
                report_parts.append(f"{i}. {condition} - Ranking score: {confidence:.2f}")
        else:
            report_parts.append("No diagnoses data available.")

        # Section 3: Literature Agent Validation
        report_parts.append("\n=== Literature Agent Validation ===")
        if literature_validation:
            report_parts.append(literature_validation)
        else:
            report_parts.append("No literature validation available.")

        # Section 4: Case Study Agent Validation
        report_parts.append("\n=== Case Study Agent Validation ===")
        if case_study_validation:
            report_parts.append(case_study_validation)
        else:
            report_parts.append("No case study validation available.")

        return "\n".join(report_parts)

    def print_explainability_report(
        self,
        top_diagnosis: dict,
        all_diagnoses: list,
        literature_validation: str,
        case_study_validation: str,
    ):
        report = self.generate_explainability_report(
            top_diagnosis, all_diagnoses, literature_validation, case_study_validation
        )
        print(report)


if __name__ == "__main__":
    agent = ExplainabilityAgent()

    # Hardcoded test input
    top_diagnosis = {
        "condition": "Influenza",
        "confidence": 0.87,
        "medications": ["Oseltamivir", "Paracetamol"],
        "precautions": ["Rest", "Hydration", "Avoid Smoking"],
        "exercises": ["Light Walking"],
        "diet": ["Fluid-rich foods", "Vitamin C"],
    }

    all_diagnoses = [
        {"condition": "Influenza", "confidence": 0.87},
        {"condition": "Common Cold", "confidence": 0.65},
        {"condition": "COVID-19", "confidence": 0.45},
        {"condition": "Pneumonia", "confidence": 0.30},
        {"condition": "Bronchitis", "confidence": 0.25},
    ]

    literature_validation = "Multiple clinical research articles validate Influenza as primary diagnosis."
    case_study_validation = "Clinical case reports confirm symptom patterns consistent with Influenza."

    agent.print_explainability_report(
        top_diagnosis, all_diagnoses, literature_validation, case_study_validation
    )
