from app.api.helpers.scoring import match_skills


class ScoreService:
    """Service class for scoring CVs"""

    @staticmethod
    def calculate_university_score(university: str, preferred_university: str = None, weight: float = 0.2):
        """Calculates the university score based on whether it matches the preferred university."""

        if university:
            if university.lower() == preferred_university.lower() or not preferred_university:
                return weight * 100
            return weight * 70
        return 0

    @staticmethod
    def calculate_gpa_score(gpa: float, weight: float = 0.3):
        """Calculates the GPA score, ensuring it is on a 4.0 scale."""

        if gpa:
            # Converts GPA from a 10-point scale to a 4-point scale.
            if gpa > 4.0:
                gpa = gpa * 4 / 10

            # calculate score based on GPA
            return weight * (gpa / 4) * 100

        return 0

    @staticmethod
    def calculate_technical_skills_score(required_skills: list[str], candidate_skills: list[str], weight: float = 0.2):
        """Calculates the score based on the match between required and candidate skills."""

        required_skills = [skill.lower() for skill in required_skills]
        candidate_skills = [skill.lower() for skill in candidate_skills]

        if not required_skills:
            return weight * 100

        if not candidate_skills:
            return 0

        match_count = len(match_skills(required_skills, candidate_skills))

        return (match_count / len(required_skills) * 100) * weight

    @staticmethod
    def calculate_experience_score(experiences: list[str], weight: float = 0.2):
        """Calculates the experience score based on the number of past jobs listed."""

        experience_count = len(experiences)

        if experience_count > 1:
            return weight * 100

        elif experience_count == 1:
            return weight * 70

        return 0

    @staticmethod
    def calculate_foreign_language_score(certificates: dict, weight: float = 0.1):
        """Calculates the score based on the candidate's proficiency in foreign languages."""

        if certificates["toeic"] or certificates["ielts"]:
            return weight * 100
        return weight * 70

    def calculate_score(self, jd: dict, cv: dict) -> float:
        """Calculates the score for a candidate based on their CV and a job description."""

        # Weights for different scoring categories
        weights = {
            "university": 0.2,
            "gpa": 0.3,
            "technical_skills": 0.2,
            "experience": 0.2,
            "foreign_language": 0.1,
        }

        # Calculate individual scores
        university_score = self.calculate_university_score(
            university=cv["university"],
            preferred_university="Da Nang University of Science and Technology",
            weight=weights["university"],
        )

        gpa_score = self.calculate_gpa_score(gpa=cv["gpa"], weight=weights["gpa"])

        technical_skills_score = self.calculate_technical_skills_score(
            required_skills=jd["requirements"]["technical_skills"],
            candidate_skills=cv["technical_skills"],
            weight=weights["technical_skills"],
        )

        experience_score = self.calculate_experience_score(
            experiences=cv["experiences"],
            weight=weights["experience"],
        )

        foreign_language_score = self.calculate_foreign_language_score(
            certificates=cv["certificates"],
            weight=weights["foreign_language"],
        )

        # Calculate total score
        total_score = (
            university_score
            + gpa_score
            + technical_skills_score
            + experience_score
            + foreign_language_score
        )

        return round(total_score, 2)
