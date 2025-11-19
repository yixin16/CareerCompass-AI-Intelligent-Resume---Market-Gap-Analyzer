"""
Ultra-Intelligent Resume Analyzer
Advanced resume analysis with semantic understanding and proficiency detection
"""

import re
from typing import Dict, List
from datetime import datetime
from utils.logger import logger
from config import SKILL_CATEGORY_WEIGHTS


class UltraIntelligentResumeAnalyzer:
    """Advanced resume analyzer with pattern recognition and NLP."""
    
    def __init__(self):
        self.skill_patterns = self._build_skill_patterns()
        self.context_keywords = self._build_context_keywords()
    
    def _build_skill_patterns(self) -> Dict:
        """Build optimized regex patterns for skill detection."""
        from data.skill_categories import SKILL_CATEGORIES
        
        patterns = {}
        for category, data in SKILL_CATEGORIES.items():
            patterns[category] = []
            for skill in data['skills']:
                pattern = r'\b' + re.escape(skill) + r'\b'
                weight = SKILL_CATEGORY_WEIGHTS.get(category, 1.0)
                patterns[category].append((skill, re.compile(pattern, re.IGNORECASE), weight))
        return patterns
    
    def _build_context_keywords(self) -> Dict:
        """Keywords that indicate skill proficiency level."""
        return {
            'expert': ['expert', 'advanced', 'proficient', 'mastery', 'extensive', 'deep', 'specialist'],
            'intermediate': ['experience', 'familiar', 'working knowledge', 'solid', 'competent', 'practical'],
            'basic': ['basic', 'beginner', 'learning', 'exposure', 'understanding', 'awareness']
        }
    
    def extract_contact_info(self, text: str) -> Dict:
        """Extract contact information with validation."""
        info = {
            'email': None,
            'phone': None,
            'linkedin': None,
            'github': None,
            'portfolio': None
        }
        
        # Email
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            info['email'] = emails[0]
        
        # Phone (Malaysia format)
        phone_pattern = r'\b(?:\+?60)?(?:1[0-9]|[0-9]{2})[-\s]?\d{7,8}\b'
        phones = re.findall(phone_pattern, text)
        if phones:
            info['phone'] = phones[0]
        
        # LinkedIn
        linkedin_pattern = r'linkedin\.com/in/([\w-]+)'
        linkedin = re.search(linkedin_pattern, text, re.IGNORECASE)
        if linkedin:
            info['linkedin'] = f"linkedin.com/in/{linkedin.group(1)}"
        
        # GitHub
        github_pattern = r'github\.com/([\w-]+)'
        github = re.search(github_pattern, text, re.IGNORECASE)
        if github:
            info['github'] = f"github.com/{github.group(1)}"
        
        # Portfolio
        url_pattern = r'https?://(?:www\.)?[\w\-\.]+\.[a-z]{2,}(?:/[\w\-\.]*)*'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        if urls:
            portfolio_urls = [u for u in urls if not any(site in u.lower() 
                            for site in ['linkedin', 'github', 'email'])]
            if portfolio_urls:
                info['portfolio'] = portfolio_urls[0]
        
        return info
    
    def extract_technical_skills_with_proficiency(self, text: str) -> Dict:
        """Extract skills with proficiency estimation."""
        skills_by_category = {}
        
        for category, patterns in self.skill_patterns.items():
            matches = []
            for skill_name, pattern, weight in patterns:
                findings = list(pattern.finditer(text))
                if findings:
                    # Estimate proficiency
                    proficiency = self._estimate_proficiency(text, findings, skill_name)
                    
                    # Get contexts
                    contexts = []
                    for match in findings[:2]:
                        start = max(0, match.start() - 60)
                        end = min(len(text), match.end() + 60)
                        contexts.append(text[start:end].strip())
                    
                    matches.append({
                        'skill': skill_name,
                        'mentions': len(findings),
                        'proficiency': proficiency,
                        'weight': weight,
                        'weighted_score': len(findings) * weight * proficiency,
                        'contexts': contexts
                    })
            
            if matches:
                skills_by_category[category] = sorted(
                    matches,
                    key=lambda x: x['weighted_score'],
                    reverse=True
                )
        
        return skills_by_category
    
    def _estimate_proficiency(self, text: str, findings: List, skill_name: str) -> float:
        """Estimate proficiency level (0.5=basic, 0.75=intermediate, 1.0=expert)."""
        context_range = 100
        proficiency_score = 0.75  # Default: intermediate
        
        for finding in findings:
            start = max(0, finding.start() - context_range)
            end = min(len(text), finding.end() + context_range)
            context = text[start:end].lower()
            
            # Check for expert indicators
            if any(kw in context for kw in self.context_keywords['expert']):
                proficiency_score = max(proficiency_score, 1.0)
            # Check for basic indicators
            elif any(kw in context for kw in self.context_keywords['basic']):
                proficiency_score = min(proficiency_score, 0.5)
        
        # Years of experience with skill
        years_pattern = rf'(\d+)\+?\s*(?:years?|yrs?)\s+(?:of\s+)?.*?{re.escape(skill_name)}'
        years_match = re.search(years_pattern, text.lower())
        if years_match:
            years = int(years_match.group(1))
            if years >= 5:
                proficiency_score = 1.0
            elif years >= 2:
                proficiency_score = max(proficiency_score, 0.75)
        
        return proficiency_score
    
    def extract_experience_with_details(self, text: str) -> Dict:
        """Enhanced experience extraction with role analysis."""
        # Extract year ranges
        year_pattern = r'(\d{4})\s*[-–—]\s*(\d{4}|present|current|now|ongoing)'
        matches = re.findall(year_pattern, text, re.IGNORECASE)
        
        year_ranges = []
        unique_years = set()
        
        for match in matches:
            try:
                start = int(match[0])
                end_str = match[1].lower()
                end = 2025 if end_str in ['present', 'current', 'now', 'ongoing'] else int(end_str)
                years = end - start
                
                if 0 <= years <= 60 and start >= 1950:
                    year_ranges.append({'start': start, 'end': end, 'duration': years})
                    for year in range(start, end):
                        unique_years.add(year)
            except:
                continue
        
        total_years = len(unique_years) if unique_years else 0
        
        # Seniority detection
        text_lower = text.lower()
        seniority_scores = {'senior': 0, 'mid': 0, 'junior': 0}
        
        seniority_indicators = {
            'senior': ['senior', 'sr.', 'lead', 'principal', 'staff', 'architect',
                      'director', 'manager', 'head of', 'chief', 'vp', 'expert'],
            'mid': ['engineer', 'scientist', 'analyst', 'developer', 'specialist',
                   'consultant', 'coordinator', 'professional'],
            'junior': ['junior', 'jr.', 'associate', 'intern', 'trainee', 'graduate',
                      'entry level', 'assistant', 'beginner']
        }
        
        for level, keywords in seniority_indicators.items():
            for kw in keywords:
                seniority_scores[level] += text_lower.count(kw)
        
        # Determine seniority
        if total_years >= 8 or seniority_scores['senior'] >= 3:
            seniority_level = 'senior'
        elif total_years >= 5 or (seniority_scores['senior'] > 0 and total_years >= 3):
            seniority_level = 'senior'
        elif total_years < 2 and seniority_scores['junior'] > seniority_scores['mid']:
            seniority_level = 'junior'
        else:
            seniority_level = 'mid'
        
        # Leadership indicators
        leadership_keywords = ['lead', 'manage', 'mentor', 'supervise', 'direct',
                              'coordinate', 'architect', 'strategy', 'coach']
        leadership_count = sum(text_lower.count(kw) for kw in leadership_keywords)
        has_leadership = leadership_count >= 3
        
        return {
            'total_years': total_years,
            'year_ranges': year_ranges,
            'seniority_level': seniority_level,
            'has_leadership': has_leadership,
            'leadership_score': leadership_count,
            'roles_count': len(year_ranges),
            'career_trajectory': self._analyze_career_trajectory(total_years, seniority_level)
        }
    
    def _analyze_career_trajectory(self, years: int, seniority: str) -> str:
        """Analyze career progression."""
        if years == 0:
            return "Entry-level professional"
        elif years >= 10:
            return "Seasoned professional with extensive expertise"
        elif years >= 7:
            return "Experienced professional with strong track record"
        elif years >= 4:
            return "Mid-career professional with proven experience"
        elif years >= 2:
            return "Growing professional with solid foundation"
        else:
            return "Early career professional"
    
    def extract_education_detailed(self, text: str) -> List[Dict]:
        """Extract detailed education information."""
        education = []
        text_lower = text.lower()
        
        degrees = {
            'phd': {'keywords': ['ph.d', 'phd', 'doctorate', 'doctoral'], 'level': 5},
            'masters': {'keywords': ['master', 'm.s.', 'msc', 'm.sc', 'mba', 'm.b.a', 'ma', 'meng'], 'level': 4},
            'bachelors': {'keywords': ['bachelor', 'b.s.', 'bsc', 'b.sc', 'b.a.', 'b.tech', 'b.e.'], 'level': 3},
            'diploma': {'keywords': ['diploma', 'associate'], 'level': 2}
        }
        
        for degree_type, data in degrees.items():
            for keyword in data['keywords']:
                if keyword in text_lower:
                    # Extract field of study
                    field_pattern = rf'{re.escape(keyword)}[^\n]*?(?:in|of)\s+([A-Za-z\s]+?)(?:\s+from|\s+at|\s*,|\n)'
                    field_match = re.search(field_pattern, text, re.IGNORECASE)
                    field = field_match.group(1).strip() if field_match else "Not specified"
                    
                    # Extract institution
                    inst_pattern = rf'{re.escape(keyword)}[^\n]*?(?:from|at)\s+([A-Z][^\n,]+?)(?:\s*,|\n|$)'
                    inst_match = re.search(inst_pattern, text, re.IGNORECASE)
                    institution = inst_match.group(1).strip() if inst_match else "Not specified"
                    
                    education.append({
                        'level': degree_type,
                        'field': field,
                        'institution': institution,
                        'priority_level': data['level']
                    })
                    break
        
        return sorted(education, key=lambda x: x['priority_level'], reverse=True)
    
    def extract_achievements_scored(self, text: str) -> List[Dict]:
        """Extract and score achievements by impact."""
        achievement_patterns = [
            (r'(\d+%)\s+(?:increase|improvement|reduction|growth|boost|decrease)', 'percentage', 1.0),
            (r'(?:saved|reduced|increased|generated)\s+(?:by\s+)?\$?(\d+[kKmMbB]?)', 'financial', 1.2),
            (r'(?:managed|led|supervised)\s+(?:team\s+of\s+)?(\d+)', 'team_management', 0.9),
            (r'(\d+[kKmM]?)\+?\s+(?:users|customers|clients|transactions|records)', 'scale', 1.1),
            (r'(?:delivered|shipped|launched|completed)\s+(\d+)', 'delivery', 0.8),
            (r'(?:improved|optimized|enhanced).*?(?:by\s+)?(\d+)(%|x|\s*times)', 'optimization', 1.0),
        ]
        
        achievements = []
        for pattern, category, impact_score in achievement_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                context_start = max(0, match.start() - 120)
                context_end = min(len(text), match.end() + 120)
                context = text[context_start:context_end].strip()
                
                achievements.append({
                    'metric': match.group(0),
                    'value': match.group(1) if match.groups() else None,
                    'category': category,
                    'impact_score': impact_score,
                    'context': context
                })
        
        achievements.sort(key=lambda x: x['impact_score'], reverse=True)
        return achievements[:20]
    
    def detect_industries_with_confidence(self, text: str) -> List[Dict]:
        """Enhanced industry detection with confidence scoring."""
        industries = {
            'fintech': {'keywords': ['financial', 'banking', 'payment', 'fintech'], 'weight': 1.2},
            'healthcare': {'keywords': ['healthcare', 'medical', 'hospital', 'pharma'], 'weight': 1.1},
            'ecommerce': {'keywords': ['e-commerce', 'retail', 'marketplace'], 'weight': 1.0},
            'ai_ml': {'keywords': ['artificial intelligence', 'ai company', 'ml platform'], 'weight': 1.3}
        }
        
        text_lower = text.lower()
        detected = []
        
        for industry, data in industries.items():
            matches = [kw for kw in data['keywords'] if kw in text_lower]
            if matches:
                score = len(matches) * data['weight']
                confidence = min(1.0, score / 5)
                
                detected.append({
                    'industry': industry,
                    'relevance_score': round(score, 2),
                    'confidence': round(confidence, 2),
                    'matched_keywords': matches
                })
        
        return sorted(detected, key=lambda x: x['relevance_score'], reverse=True)
    
    def analyze_resume(self, text: str) -> Dict:
        """Ultra-comprehensive resume analysis."""
        logger.info("🔍 Performing intelligent resume analysis...")
        
        if len(text) < 100:
            logger.warning("Resume text too short for analysis")
            return {}
        
        # Extract all components
        contact = self.extract_contact_info(text)
        skills = self.extract_technical_skills_with_proficiency(text)
        experience = self.extract_experience_with_details(text)
        education = self.extract_education_detailed(text)
        achievements = self.extract_achievements_scored(text)
        industries = self.detect_industries_with_confidence(text)
        
        # Calculate metrics
        total_skills = sum(len(s) for s in skills.values())
        expert_skills = sum(1 for cat in skills.values() for skill in cat if skill['proficiency'] >= 0.9)
        
        # Build profile
        profile = {
            'contact_info': contact,
            'summary': self._generate_summary(experience, skills, achievements),
            'skills_by_category': skills,
            'total_skills': total_skills,
            'expert_skills': expert_skills,
            'experience': experience,
            'education': education,
            'achievements': achievements,
            'industry_focus': industries,
            'strengths': self._identify_strengths(skills, achievements, experience),
            'career_level': self._determine_career_level(experience, skills, achievements),
            'analysis_timestamp': datetime.now().isoformat()
        }
        
        # Log insights
        logger.info(f"✓ Skills: {total_skills} total ({expert_skills} expert-level)")
        logger.info(f"✓ Experience: {experience['total_years']} years ({experience['seniority_level']})")
        logger.info(f"✓ Achievements: {len(achievements)} quantified")
        logger.info(f"✓ Career Level: {profile['career_level']}")
        
        return profile
    
    def _generate_summary(self, exp: Dict, skills: Dict, achievements: List) -> str:
        """Generate intelligent summary."""
        years = exp['total_years']
        level = exp['seniority_level'].title()
        skill_count = sum(len(s) for s in skills.values())
        
        summary = f"{level}-level professional with {years} years of experience"
        
        if skill_count > 30:
            summary += f" and extensive technical expertise"
        elif skill_count > 15:
            summary += f" and strong technical skills"
        
        if len(achievements) >= 5:
            summary += f", with proven track record of measurable impact"
        
        return summary + "."
    
    def _identify_strengths(self, skills: Dict, achievements: List, exp: Dict) -> List[str]:
        """Identify top strengths."""
        strengths = []
        
        if sum(len(s) for s in skills.values()) > 25:
            strengths.append("Broad technical expertise across multiple domains")
        
        for category, skill_list in skills.items():
            if len(skill_list) >= 8:
                strengths.append(f"Deep specialization in {category.replace('_', ' ')}")
                break
        
        if len(achievements) >= 8:
            strengths.append("Strong track record of measurable business impact")
        
        if exp.get('has_leadership'):
            strengths.append("Proven leadership and team management")
        
        if exp['total_years'] >= 7:
            strengths.append(f"Extensive experience ({exp['total_years']} years)")
        
        return strengths[:5]
    
    def _determine_career_level(self, exp: Dict, skills: Dict, achievements: List) -> str:
        """Determine career level."""
        score = 0
        
        if exp['total_years'] >= 10:
            score += 3
        elif exp['total_years'] >= 5:
            score += 2
        elif exp['total_years'] >= 2:
            score += 1
        
        skill_count = sum(len(s) for s in skills.values())
        if skill_count >= 30:
            score += 2
        elif skill_count >= 15:
            score += 1
        
        if len(achievements) >= 10:
            score += 2
        elif len(achievements) >= 5:
            score += 1
        
        if exp.get('has_leadership'):
            score += 1
        
        if score >= 7:
            return "Senior/Principal Level"
        elif score >= 4:
            return "Mid-Senior Level"
        elif score >= 2:
            return "Mid Level"
        else:
            return "Junior/Entry Level"