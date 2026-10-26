# import asyncio
# import logging

# from literature_agent import LiteratureAgent
# from case_study_agent import CaseStudyAgent

# logging.basicConfig(level=logging.INFO)

# async def run_agents():
#     input_data = {
#         'extracted_symptoms': [{'name': 'cough'}, {'name': 'fever'}, {'name': 'fatigue'}],
#         'initial_diagnoses': [
#             {'condition': 'Influenza', 'confidence': 0.7},
#             {'condition': 'Common Cold', 'confidence': 0.6},
#         ],
#         'demographics': {'age': 30, 'gender': 'female'},
#     }

#     literature_agent = LiteratureAgent()
#     await literature_agent._load_models()
#     literature_output = await literature_agent.process(input_data)
#     print("\n--- Literature Agent Output ---")
#     print(literature_output)

#     case_study_agent = CaseStudyAgent()
#     await case_study_agent._load_models()
#     await case_study_agent._load_data()
#     case_study_output = await case_study_agent.process(input_data)
#     print("\n--- Case Study Agent Output ---")
#     print(case_study_output)

#     await literature_agent.cleanup()
#     await case_study_agent.cleanup()

# if __name__ == "__main__":
#     asyncio.run(run_agents())






import asyncio
import logging

from literature_agent import LiteratureAgent
from case_study_agent import CaseStudyAgent

logging.basicConfig(level=logging.INFO)

async def run_agents():
    input_data = {
        'extracted_symptoms': [{'name': 'cough'}, {'name': 'fever'}, {'name': 'fatigue'}],
        'initial_diagnoses': [
            {'condition': 'Influenza', 'confidence': 0.7},
            {'condition': 'Common Cold', 'confidence': 0.6},
        ],
        'demographics': {'age': 30, 'gender': 'female'},
    }

    literature_agent = LiteratureAgent()
    await literature_agent._load_models()
    literature_full_output = await literature_agent.process(input_data)

    # Simplify literature output: keep top 3 articles per source
    simplified_lit_evidence = []
    by_source = {}
    for article in literature_full_output['literature_evidence']:
        src = article['source']
        by_source.setdefault(src, []).append(article)
    for src, articles in by_source.items():
        simplified_lit_evidence.extend(articles[:3])

    simplified_lit_output = {
        'literature_evidence': simplified_lit_evidence,
        # 'validated_diagnoses': literature_full_output['validated_diagnoses'],
        # 'validation_metadata': literature_full_output['validation_metadata']
    }

    print("\n--- Literature Agent Reduced Output ---")
    print(simplified_lit_output)

    case_study_agent = CaseStudyAgent()
    await case_study_agent._load_models()
    # Use conditions from input diagnoses for loading case studies
    conditions = [diag['condition'] for diag in input_data['initial_diagnoses']]
    await case_study_agent._load_data(conditions=conditions)

    case_study_output = await case_study_agent.process(input_data)
    print("\n--- Case Study Agent Output ---")
    print(case_study_output)

    await literature_agent.cleanup()
    await case_study_agent.cleanup()

if __name__ == "__main__":
    asyncio.run(run_agents())
