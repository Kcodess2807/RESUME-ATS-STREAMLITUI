from typing import Dict, List, Optional, Tuple
import re
import streamlit as st
import hashlib


def calculate_formatting_score(sections: Dict[str, str], text: str) ->float:
    score = 0.0
    if sections.get('experience') and len(sections['experience']) > 50:
        score += 3.0
    if sections.get('education') and len(sections['education']) > 20:
        score += 2.0
    if sections.get('skills') and len(sections['skills']) > 10:
        score += 2.0
    if sections.get('summary') and len(sections['summary']) > 30:
        score += 1.5
    if sections.get('projects') and len(sections['projects']) > 30:
        score += 1.5
    bullet_patterns = ['^\\s*[•\\-\\*\\◦]', '^\\s*\\d+\\.']
    bullet_count = 0
    for line in text.split('\n'):
        for pattern in bullet_patterns:
            if re.match(pattern, line):
                bullet_count += 1
                break
    if bullet_count >= 15:
        score += 5.0
    elif bullet_count >= 10:
        score += 4.0
    elif bullet_count >= 5:
        score += 3.0
    elif bullet_count >= 3:
        score += 2.0
    elif bullet_count >= 1:
        score += 1.0
    section_headers_found = 0
    for section_name in ['experience', 'education', 'skills', 'summary',
        'projects']:
        if sections.get(section_name):
            section_headers_found += 1
    if section_headers_found >= 4:
        score += 5.0
    elif section_headers_found >= 3:
        score += 4.0
    elif section_headers_found >= 2:
        score += 3.0
    elif section_headers_found >= 1:
        score += 2.0
    return min(20.0, max(0.0, score))


def calculate_keywords_score(resume_keywords: List[str], skills: List[str],
    jd_keywords: Optional[List[str]]=None) ->float:
    score = 0.0
    keyword_count = len(resume_keywords)
    if keyword_count >= 20:
        score += 10.0
    elif keyword_count >= 15:
        score += 8.0
    elif keyword_count >= 10:
        score += 6.0
    elif keyword_count >= 5:
        score += 4.0
    elif keyword_count >= 3:
        score += 2.0
    skills_count = len(skills)
    if skills_count >= 15:
        score += 10.0
    elif skills_count >= 10:
        score += 8.0
    elif skills_count >= 7:
        score += 6.0
    elif skills_count >= 5:
        score += 4.0
    elif skills_count >= 3:
        score += 2.0
    if jd_keywords:
        resume_kw_set = set(kw.lower() for kw in resume_keywords)
        jd_kw_set = set(kw.lower() for kw in jd_keywords)
        if jd_kw_set:
            overlap = len(resume_kw_set & jd_kw_set)
            match_percentage = overlap / len(jd_kw_set)
            if match_percentage >= 0.7:
                score += 5.0
            elif match_percentage >= 0.5:
                score += 4.0
            elif match_percentage >= 0.3:
                score += 3.0
            elif match_percentage >= 0.2:
                score += 2.0
            elif match_percentage >= 0.1:
                score += 1.0
    elif keyword_count >= 10:
        score += 3.0
    return min(25.0, max(0.0, score))


def calculate_content_score(text: str, action_verbs: List[str],
    grammar_results: Dict) ->float:
    score = 0.0
    action_verb_count = len(action_verbs)
    if action_verb_count >= 15:
        score += 10.0
    elif action_verb_count >= 10:
        score += 8.0
    elif action_verb_count >= 7:
        score += 6.0
    elif action_verb_count >= 5:
        score += 4.0
    elif action_verb_count >= 3:
        score += 2.0
    number_patterns = ['\\d+%', '\\$\\d+', '\\d+[kKmMbB]',
        '\\d+\\s*(?:users|customers|clients|projects|hours|days|months|years)',
        '(?:increased|decreased|improved|reduced|grew|saved)\\s+(?:by\\s+)?\\d+'
        ]
    achievement_count = 0
    for pattern in number_patterns:
        achievement_count += len(re.findall(pattern, text, re.IGNORECASE))
    if achievement_count >= 10:
        score += 5.0
    elif achievement_count >= 7:
        score += 4.0
    elif achievement_count >= 5:
        score += 3.0
    elif achievement_count >= 3:
        score += 2.0
    elif achievement_count >= 1:
        score += 1.0
    grammar_penalty = grammar_results.get('penalty_applied', 0.0)
    grammar_score = max(0.0, 10.0 - grammar_penalty / 2.0)
    score += grammar_score
    return min(25.0, max(0.0, score))


def calculate_skill_validation_score(validation_results: Dict) ->float:
    score = validation_results.get('validation_score', 0.0)
    return min(15.0, max(0.0, score))


def calculate_ats_compatibility_score(text: str, location_results: Dict,
    sections: Dict[str, str]) ->float:
    score = 15.0
    location_penalty = location_results.get('penalty_applied', 0.0)
    score -= location_penalty
    special_char_count = len(re.findall('[│┤├┼┴┬╔╗╚╝═║╠╣╦╩╬]', text))
    if special_char_count > 20:
        score -= 2.0
    elif special_char_count > 10:
        score -= 1.0
    short_sections = 0
    for section_name, content in sections.items():
        if section_name in ['experience', 'education', 'skills']:
            if content and len(content) < 20:
                short_sections += 1
    if short_sections >= 2:
        score -= 2.0
    elif short_sections >= 1:
        score -= 1.0
    if len(sections.get('experience', '')) > 100 and len(sections.get(
        'skills', '')) > 20:
        score += 1.0
    return min(15.0, max(0.0, score))


def apply_penalties_and_bonuses(base_score: float, grammar_results: Dict,
    location_results: Dict, skill_validation_results: Dict) ->Tuple[float,
    Dict, Dict]:
    penalties = {}
    bonuses = {}
    adjusted_score = base_score
    grammar_penalty = grammar_results.get('penalty_applied', 0.0)
    if grammar_penalty > 0:
        penalties['grammar'] = grammar_penalty
    location_penalty = location_results.get('penalty_applied', 0.0)
    if location_penalty > 0:
        penalties['location_privacy'] = location_penalty
    validation_percentage = skill_validation_results.get(
        'validation_percentage', 0.0)
    if validation_percentage >= 0.9:
        bonus = 2.0
        bonuses['excellent_skill_validation'] = bonus
        adjusted_score += bonus
    elif validation_percentage >= 0.8:
        bonus = 1.0
        bonuses['good_skill_validation'] = bonus
        adjusted_score += bonus
    if grammar_results.get('total_errors', 0) == 0:
        bonus = 2.0
        bonuses['perfect_grammar'] = bonus
        adjusted_score += bonus
    adjusted_score = min(100.0, max(0.0, adjusted_score))
    return adjusted_score, penalties, bonuses
