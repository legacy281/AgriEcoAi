def match_skills(technical_skills_required: list, technical_skills: list, threshold=80):
    """Matches required technical skills with the candidate's technical skills."""

    matches = []
    # for skill in technical_skills_required:
    #     for target_skill in technical_skills:
    #         # Check for exact matches first
    #         if skill.lower() == target_skill.lower():
    #             matches.append((skill, target_skill, 100))
    #         else:
    #             # Fuzzy matching for similar skills
    #             similarity = fuzz.partial_ratio(skill.lower(), target_skill.lower())
    #             if similarity >= threshold:
    #                 if not (
    #                     skill.lower() in target_skill.lower()
    #                     or target_skill.lower() in skill.lower()
    #                 ):
    #                     matches.append((skill, target_skill, similarity))
    return matches
