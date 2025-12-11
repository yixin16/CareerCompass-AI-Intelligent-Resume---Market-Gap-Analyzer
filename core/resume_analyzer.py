"""
Ultra-Intelligent Resume Analyzer (Enhanced v2.0)
Extracts structured data, calculates true experience timeline, utilizes vectorized NLP,
generates candidate profile summary, and provides actionable insights.
"""

import re
from typing import Dict, List, Set, Tuple
from datetime import datetime
from collections import Counter
from utils.logger import logger
from core.semantic_matcher import SemanticMatcher


class UltraIntelligentResumeAnalyzer:
    def __init__(self):
        self.ai = SemanticMatcher()
        
        # Enhanced skill proficiency keywords
        self.proficiency_keywords = {
            'expert': ['expert', 'advanced', 'proficient', 'architect', 'lead', 'master', 
                      'specialist', 'guru', 'ninja', 'rockstar', '10+ years', '5+ years'],
            'intermediate': ['intermediate', 'solid', 'good', 'working knowledge', 'hands-on',
                           'experienced', 'comfortable', '3+ years', '2+ years'],
            'beginner': ['basic', 'familiar', 'learning', 'junior', 'exposure', 'beginner',
                        'entry-level', 'trainee', 'intern', 'studied', 'coursework']
        }
        
        # Industry recognition keywords
        self.achievement_keywords = [
            'award', 'recognition', 'achievement', 'published', 'patent', 'certified',
            'featured', 'speaker', 'presented', 'winner', 'finalist', 'top performer',
            'promoted', 'led', 'built', 'founded', 'launched', 'improved', 'increased',
            'reduced', 'optimized', 'achieved', 'delivered', 'managed'
        ]
        
    def extract_skills_dynamically(self, text: str) -> Dict:
        """
        Optimized Pipeline with Enhanced Proficiency Detection:
        1. Heuristic Extraction (Broad net)
        2. Vectorized Batch Validation (Fast filtering)
        3. Vectorized Categorization
        4. Context-Aware Proficiency Scoring
        """
        logger.info("  🧠 AI scanning for technical skills...")
        
        # 1. Candidate Extraction (Heuristics)
        pattern = r'\b[A-Z][a-zA-Z0-9]*\+?\+?#?(?:\s[A-Z][a-zA-Z0-9]*\+?)*\b|\b\.NET\b|\bNode\.js\b|\bReact\.js\b|\bVue\.js\b'
        raw_candidates = set(re.findall(pattern, text))
        
        stopwords = {
            "The", "A", "An", "In", "On", "To", "For", "Of", "And", "With", "By", "At", "From",
            "Work", "Experience", "Education", "University", "College", "School", "Institute",
            "Bachelor", "Master", "PhD", "Diploma", "Degree", "Certified", "Certificate",
            "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            "January", "February", "March", "April", "May", "June", "July", "August", 
            "September", "October", "November", "December",
            "Present", "Current", "Date", "Year", "Month", "Project", "Role", "Manager", 
            "Team", "Member", "Senior", "Junior", "Lead", "Associate", "Developer", 
            "Engineer", "Analyst", "Consultant", "About", "Skills", "Technologies"
        }
        
        clean_candidates = []
        for c in raw_candidates:
            c_clean = c.strip().strip(',').strip('.')
            if len(c_clean) > 1 and c_clean not in stopwords and not c_clean.isdigit():
                clean_candidates.append(c_clean)
        
        candidate_list = list(set(clean_candidates))[:200]
        
        # 2. BATCH Validation
        valid_skill_names = self.ai.batch_filter_skills(candidate_list, threshold=0.40)
        
        # 3. BATCH Categorization
        categorized_skills = self.ai.batch_classify_categories(valid_skill_names)
        
        # 4. Attach Enhanced Proficiency with Context
        final_skills = {}
        for category, skills in categorized_skills.items():
            final_skills[category] = []
            for skill in skills:
                proficiency_score, proficiency_level = self._estimate_proficiency_enhanced(text, skill)
                final_skills[category].append({
                    'skill': skill,
                    'proficiency': proficiency_score,
                    'proficiency_level': proficiency_level,  # "Expert", "Intermediate", "Beginner"
                    'frequency': text.lower().count(skill.lower())
                })
        
        # Sort skills within each category by proficiency
        for category in final_skills:
            final_skills[category].sort(key=lambda x: x['proficiency'], reverse=True)
        
        total = sum(len(x) for x in final_skills.values())
        logger.info(f"  ✓ AI identified {total} skills across {len(final_skills)} categories.")
        return final_skills

    def _estimate_proficiency_enhanced(self, text: str, skill: str) -> Tuple[float, str]:
        """
        Enhanced proficiency estimation with multi-factor analysis.
        Returns (score, level_label)
        """
        try:
            matches = [m.start() for m in re.finditer(re.escape(skill), text, re.IGNORECASE)]
            if not matches: 
                return 0.75, "Intermediate"
            
            scores = []
            frequency_bonus = min(len(matches) * 0.05, 0.15)  # Max 15% bonus for frequency
            
            for idx in matches:
                window = text[max(0, idx-100):min(len(text), idx+100)].lower()
                
                # Check for expert indicators
                if any(keyword in window for keyword in self.proficiency_keywords['expert']):
                    scores.append(0.95)
                # Check for beginner indicators
                elif any(keyword in window for keyword in self.proficiency_keywords['beginner']):
                    scores.append(0.50)
                # Check for intermediate indicators
                elif any(keyword in window for keyword in self.proficiency_keywords['intermediate']):
                    scores.append(0.75)
                else:
                    # Default based on context
                    # Check if skill is in a project description (likely hands-on)
                    if any(word in window for word in ['built', 'developed', 'implemented', 'created', 'designed']):
                        scores.append(0.80)
                    else:
                        scores.append(0.70)
            
            base_score = max(scores) if scores else 0.70
            final_score = min(base_score + frequency_bonus, 1.0)
            
            # Determine level label
            if final_score >= 0.85:
                level = "Expert"
            elif final_score >= 0.65:
                level = "Intermediate"
            else:
                level = "Beginner"
            
            return final_score, level
            
        except:
            return 0.75, "Intermediate"

    def _extract_contact_info(self, text: str) -> Dict:
        """Enhanced contact extraction with validation."""
        email = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
        phone = re.search(r'(?:\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        
        # Enhanced link extraction
        linkedin = re.search(r'(?:https?://)?(?:www\.)?linkedin\.com/in/([a-zA-Z0-9_-]+)', text)
        github = re.search(r'(?:https?://)?(?:www\.)?github\.com/([a-zA-Z0-9_-]+)', text)
        portfolio = re.search(r'(?:https?://)?(?:www\.)?([a-zA-Z0-9-]+\.(?:com|io|dev|me|portfolio))', text)
        
        links = []
        if linkedin:
            links.append({'type': 'LinkedIn', 'url': linkedin.group(0)})
        if github:
            links.append({'type': 'GitHub', 'url': github.group(0)})
        if portfolio and not any(domain in portfolio.group(0) for domain in ['linkedin', 'github']):
            links.append({'type': 'Portfolio', 'url': portfolio.group(0)})
        
        return {
            'email': email.group(0) if email else None,
            'phone': phone.group(0) if phone else None,
            'links': links,
            'has_digital_presence': len(links) > 0
        }

    def _calculate_experience_robust(self, text: str) -> Dict:
        """Enhanced experience calculation with gap detection."""
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        years = [int(y) for y in years]
        current_year = datetime.now().year
        total_years = 0
        
        if years:
            min_year = min(years)
            max_year = max(years)
            if re.search(r'\b(Present|Current|Now)\b', text, re.IGNORECASE):
                max_year = current_year
            span = max_year - min_year
            if 0 < span < 40:
                total_years = span
        
        # Fallback: Extract explicit year mentions
        if total_years == 0:
            text_years = re.findall(r'(\d+)\+?\s*years?', text.lower())
            if text_years:
                valid_years = [int(y) for y in text_years if int(y) < 40]
                if valid_years:
                    total_years = max(valid_years)

        # Determine seniority with more granular levels
        if total_years >= 10: 
            seniority = "Staff/Principal"
        elif total_years >= 7: 
            seniority = "Senior"
        elif total_years >= 5: 
            seniority = "Mid-Senior"
        elif total_years >= 2: 
            seniority = "Mid-Level"
        elif total_years >= 1:
            seniority = "Junior"
        else: 
            seniority = "Entry-Level"
        
        return {
            'total_years': total_years, 
            'seniority_level': seniority,
            'career_stage': self._determine_career_stage(total_years)
        }

    def _determine_career_stage(self, years: int) -> str:
        """Categorize career stage for better insights."""
        if years >= 10:
            return "Established Expert"
        elif years >= 5:
            return "Experienced Professional"
        elif years >= 2:
            return "Growing Professional"
        elif years >= 1:
            return "Early Career"
        else:
            return "Starting Career"

    def _extract_achievements(self, text: str) -> List[Dict]:
        """
        Extract quantifiable achievements and accomplishments.
        """
        achievements = []
        
        # Pattern for percentages and metrics
        metric_patterns = [
            r'(\d+)%\s*(?:increase|improvement|growth|reduction|decrease)',
            r'(?:increased|improved|reduced|decreased|boosted)\s*(?:by\s*)?(\d+)%',
            r'(\d+[KMB]?)\+?\s*(?:users|customers|clients|downloads|sales)',
            r'saved\s*\$?(\d+[KMB]?)',
            r'generated\s*\$?(\d+[KMB]?)',
        ]
        
        for pattern in metric_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Get surrounding context
                start = max(0, match.start() - 100)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                
                achievements.append({
                    'metric': match.group(0),
                    'context': context[:200]  # Limit context length
                })
        
        # Extract award/recognition mentions
        for keyword in ['award', 'recognition', 'certified', 'published', 'patent']:
            pattern = rf'\b{keyword}\w*\b'
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                context = text[start:end].strip()
                achievements.append({
                    'type': 'recognition',
                    'keyword': match.group(0),
                    'context': context[:150]
                })
        
        return achievements[:10]  # Limit to top 10

    def _analyze_skill_diversity(self, skills: Dict) -> Dict:
        """
        Analyze skill diversity and breadth vs. depth.
        """
        total_skills = sum(len(skills_list) for skills_list in skills.values())
        num_categories = len(skills)
        
        # Calculate average skills per category
        avg_per_category = total_skills / num_categories if num_categories > 0 else 0
        
        # Determine profile type
        if num_categories >= 4 and avg_per_category >= 5:
            profile_type = "Full-Stack / Generalist"
            recommendation = "Strong breadth across multiple domains. Consider deepening expertise in 1-2 areas for senior roles."
        elif num_categories <= 2 and avg_per_category >= 8:
            profile_type = "Specialist / Expert"
            recommendation = "Deep expertise in focused areas. Consider adding complementary skills for versatility."
        elif num_categories >= 3 and avg_per_category <= 4:
            profile_type = "Broad Explorer"
            recommendation = "Good exposure to various technologies. Focus on building depth in core areas."
        else:
            profile_type = "Balanced Professional"
            recommendation = "Solid balance of breadth and depth. Continue building on strengths."
        
        # Identify strongest category
        strongest_category = max(skills.items(), key=lambda x: len(x[1]))[0] if skills else "N/A"
        
        return {
            'total_skills': total_skills,
            'num_categories': num_categories,
            'avg_skills_per_category': round(avg_per_category, 1),
            'profile_type': profile_type,
            'strongest_category': strongest_category,
            'recommendation': recommendation
        }

    def _derive_strengths(self, skills: Dict, exp_data: Dict, achievements: List) -> List[str]:
        """Enhanced strength identification with achievement integration."""
        strengths = []
        years = exp_data['total_years']
        
        # Experience-based strengths
        if years >= 10:
            strengths.append(f"Veteran Professional with {years}+ years of industry leadership")
        elif years >= 5:
            strengths.append(f"Seasoned Professional with {years}+ years of proven expertise")
        elif years >= 2:
            strengths.append(f"Growing Professional with {years} years of hands-on experience")
        elif years >= 1:
            strengths.append(f"Emerging Talent with {years} year of practical experience")
        
        # Skill-based strengths
        max_cat = None
        max_count = 0
        for cat, s_list in skills.items():
            if len(s_list) > max_count:
                max_count = len(s_list)
                max_cat = cat
        
        if max_cat and max_count >= 5:
            # Count expert-level skills
            expert_skills = [s for s in skills[max_cat] if s.get('proficiency_level') == 'Expert']
            if len(expert_skills) >= 3:
                strengths.append(f"Expert-level mastery in {max_cat} ({len(expert_skills)} advanced skills)")
            else:
                strengths.append(f"Strong specialization in {max_cat} ({max_count} skills)")
        
        # Achievement-based strengths
        if achievements:
            metric_achievements = [a for a in achievements if 'metric' in a]
            if len(metric_achievements) >= 3:
                strengths.append(f"Results-driven with {len(metric_achievements)} quantifiable achievements")
        
        # Multi-domain strength
        if len(skills) >= 4:
            strengths.append(f"Versatile across {len(skills)} technical domains")
        
        return strengths

    def _generate_profile_summary(self, contact: Dict, exp_data: Dict, skills: Dict, 
                                 achievements: List, diversity: Dict) -> str:
        """
        Enhanced profile summary with comprehensive insights.
        """
        # 1. Opening Statement
        summary_parts = []
        
        career_descriptor = exp_data['career_stage']
        seniority = exp_data['seniority_level']
        years = exp_data['total_years']
        
        if years > 0:
            summary_parts.append(
                f"A {seniority} professional ({career_descriptor}) with {years} year{'s' if years != 1 else ''} of industry experience."
            )
        else:
            summary_parts.append(
                f"An {seniority} professional beginning their career journey with demonstrated technical capabilities."
            )
        
        # 2. Skill Profile Analysis
        profile_type = diversity['profile_type']
        strongest_cat = diversity['strongest_category']
        
        if strongest_cat and strongest_cat != "N/A":
            # Get top skills in strongest category
            top_skills = [s['skill'] for s in skills.get(strongest_cat, [])[:3]]
            if top_skills:
                skills_text = ", ".join(top_skills)
                summary_parts.append(
                    f"Profile demonstrates a {profile_type} orientation with particular strength in "
                    f"{strongest_cat}, showcasing proficiency in {skills_text}."
                )
        
        # 3. Technical Breadth
        total_skills = diversity['total_skills']
        num_categories = diversity['num_categories']
        
        if total_skills >= 20:
            summary_parts.append(
                f"Commands an impressive technical arsenal of {total_skills} validated skills "
                f"spanning {num_categories} categories."
            )
        elif total_skills >= 10:
            summary_parts.append(
                f"Possesses a solid foundation with {total_skills} technical skills "
                f"across {num_categories} domains."
            )
        
        # 4. Achievement Highlights
        if achievements:
            metric_achievements = [a for a in achievements if 'metric' in a]
            if metric_achievements:
                summary_parts.append(
                    f"Track record includes {len(metric_achievements)} quantifiable achievements, "
                    f"demonstrating measurable impact on projects and teams."
                )
        
        # 5. Digital Presence
        if contact['has_digital_presence']:
            link_count = len(contact['links'])
            summary_parts.append(
                f"Maintains professional visibility with {link_count} active "
                f"{'portfolio link' if link_count == 1 else 'portfolio links'}."
            )
        
        # 6. Career Stage Insight
        if years < 2 and total_skills > 10:
            summary_parts.append(
                "Shows exceptional learning velocity and breadth for early career stage—strong potential for rapid growth."
            )
        elif years >= 5 and len([s for cat in skills.values() for s in cat if s.get('proficiency_level') == 'Expert']) >= 5:
            summary_parts.append(
                "Exhibits deep technical expertise typical of senior practitioners, with multiple expert-level competencies."
            )
        
        return " ".join(summary_parts)

    def _generate_recommendations(self, profile_data: Dict) -> List[str]:
        """
        Generate actionable recommendations based on profile analysis.
        """
        recommendations = []
        
        years = profile_data['experience']['total_years']
        skills = profile_data['skills_by_category']
        diversity = profile_data['skill_diversity']
        contact = profile_data['contact_info']
        
        # Career advancement recommendations
        if years >= 5 and diversity['profile_type'] in ['Specialist / Expert']:
            recommendations.append({
                'category': 'Career Growth',
                'priority': 'High',
                'suggestion': 'Consider leadership roles or architect positions that leverage your deep expertise',
                'reasoning': 'Your specialized knowledge and experience level align with senior/lead positions'
            })
        
        # Skill development recommendations
        if diversity['profile_type'] == 'Broad Explorer':
            recommendations.append({
                'category': 'Skill Development',
                'priority': 'Medium',
                'suggestion': f"Focus on deepening expertise in {diversity['strongest_category']}",
                'reasoning': 'Building depth in your strongest area will increase competitiveness for senior roles'
            })
        
        # Digital presence recommendations
        if not contact['has_digital_presence'] or len(contact['links']) < 2:
            recommendations.append({
                'category': 'Professional Branding',
                'priority': 'Medium',
                'suggestion': 'Build stronger digital presence with GitHub, LinkedIn, and portfolio site',
                'reasoning': 'Active online presence significantly increases visibility to recruiters and opportunities'
            })
        
        # Experience-based recommendations
        if years < 2:
            recommendations.append({
                'category': 'Experience Building',
                'priority': 'High',
                'suggestion': 'Focus on building portfolio projects that demonstrate real-world impact',
                'reasoning': 'Concrete projects with metrics help compensate for limited work experience'
            })
        
        return recommendations

    def analyze_resume(self, text: str) -> Dict:
        """
        Main Entry Point - Comprehensive Resume Analysis
        """
        logger.info("🔍 Starting comprehensive resume analysis...")
        
        # 1. Extract Core Data
        contact = self._extract_contact_info(text)
        skills = self.extract_skills_dynamically(text)
        exp_data = self._calculate_experience_robust(text)
        achievements = self._extract_achievements(text)
        
        # 2. Perform Advanced Analysis
        diversity = self._analyze_skill_diversity(skills)
        strengths = self._derive_strengths(skills, exp_data, achievements)
        
        # 3. Generate Insights
        profile_summary = self._generate_profile_summary(
            contact, exp_data, skills, achievements, diversity
        )
        
        # 4. Compile Complete Profile
        profile = {
            # Basic Info
            'contact_info': contact,
            'skills_by_category': skills,
            'total_skills': diversity['total_skills'],
            
            # Experience Data
            'experience': exp_data,
            'career_level': exp_data['seniority_level'],
            'career_stage': exp_data['career_stage'],
            
            # Advanced Analysis
            'skill_diversity': diversity,
            'achievements': achievements,
            'strengths': strengths,
            
            # AI-Generated Insights
            'profile_summary': profile_summary,
            'recommendations': self._generate_recommendations({
                'experience': exp_data,
                'skills_by_category': skills,
                'skill_diversity': diversity,
                'contact_info': contact
            }),
            
            # Metadata
            'analysis_timestamp': datetime.now().isoformat(),
            'analysis_version': '2.0'
        }
        
        logger.info("✅ Resume analysis complete!")
        return profile
