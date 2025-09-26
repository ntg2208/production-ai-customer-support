import re
import json
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import hashlib

@dataclass
class QAPair:
    chunk_id: str
    question: str
    answer: str
    section: str
    topics: List[str]
    extraction_method: str
    confidence: float
    metadata: Dict
    
    def to_dict(self) -> Dict:
        return asdict(self)

class UKConnectQAExtractor:
    """Complete Q&A extraction system for UKConnect policy document"""
    
    def __init__(self):
        self.topic_keywords = {
            'invoice': ['invoice', 'receipt', 'confirmation', 'billing', 'e-ticket'],
            'booking': ['book', 'booking', 'reservation', 'ticket'],
            'cancellation': ['cancel', 'cancellation', 'terminate', 'cancel'],
            'payment': ['payment', 'pay', 'card', 'paypal', 'fee', 'charge', 'cost'],
            'modification': ['change', 'modify', 'rebook', 'alter', 'edit'],
            'refund': ['refund', 'money back', 'reimburs', 'return money'],
            'eligibility': ['eligible', 'requirements', 'criteria', 'qualify'],
            'timing': ['time', 'hours', 'days', 'deadline', 'before departure'],
            'fares': ['fare', 'fares', 'price', 'pricing', 'flexible', 'standard', 'first class'],
            'security': ['security', '3-d secure', 'authentication', 'verification'],
            'rebooking': ['rebook', 'rebooking', 'change booking', 'modify booking']
        }
        
    def extract_all_qa_pairs(self, policy_text: str) -> List[QAPair]:
        """Main method to extract all types of Q&A pairs"""
        all_pairs = []
        
        # Method 1: Numbered FAQ questions
        all_pairs.extend(self._extract_numbered_faq(policy_text))
        
        # Method 2: Policy statements to Q&A
        all_pairs.extend(self._extract_policy_statements(policy_text))
        
        # Method 3: Procedure sections to Q&A
        all_pairs.extend(self._extract_procedures(policy_text))
        
        # Method 4: Implicit Q&A from requirements
        all_pairs.extend(self._extract_requirements(policy_text))
        
        # Method 5: Create comparison Q&A
        all_pairs.extend(self._create_comparison_qa(policy_text))
        
        # Clean and deduplicate
        return self._deduplicate_and_clean(all_pairs)
    
    def _extract_numbered_faq(self, text: str) -> List[QAPair]:
        """Extract numbered FAQ items"""
        pairs = []
        
        # Pattern for numbered questions with markdown bold
        pattern = r'(\d+)\.\s+\*\*([^*]+)\*\*\s*(.*?)(?=\d+\.\s+\*\*|##|###|$)'
        matches = re.findall(pattern, text, re.DOTALL)
        
        for number, question, answer in matches:
            clean_answer = self._clean_text(answer)
            
            # Only include if answer has substantial content
            if len(clean_answer) > 20 and '?' in question:
                pairs.append(QAPair(
                    chunk_id=f"UKC_FAQ_{number}",
                    question=question.strip(),
                    answer=clean_answer,
                    section=self._get_section_name(text, question),
                    topics=self._extract_topics(f"{question} {clean_answer}"),
                    extraction_method="numbered_faq",
                    confidence=0.95,
                    metadata={
                        "question_number": int(number),
                        "extracted_at": datetime.now().isoformat()
                    }
                ))
        
        return pairs
    
    def _extract_policy_statements(self, text: str) -> List[QAPair]:
        """Convert policy statements to Q&A format"""
        pairs = []
        
        # Extract fare type policies
        fare_pattern = r'\*\*([^*]+Fares?)\*\*:\s*([^*]+?)(?=\*\*[^*]+Fares?|\n\n|##|$)'
        fare_matches = re.findall(fare_pattern, text, re.DOTALL)
        
        for idx, (fare_type, description) in enumerate(fare_matches):
            clean_description = self._clean_text(description)
            
            if len(clean_description) > 15:
                question = f"What is the policy for {fare_type.lower()}?"
                
                pairs.append(QAPair(
                    chunk_id=f"UKC_POLICY_{idx+1}",
                    question=question,
                    answer=clean_description,
                    section="Fare Policies",
                    topics=self._extract_topics(f"{question} {clean_description}"),
                    extraction_method="policy_statement",
                    confidence=0.90,
                    metadata={
                        "fare_type": fare_type,
                        "extracted_at": datetime.now().isoformat()
                    }
                ))
        
        return pairs
    
    def _extract_procedures(self, text: str) -> List[QAPair]:
        """Extract procedural information as Q&A"""
        pairs = []
        
        # Find "How to" sections
        how_to_pattern = r'###\s*(How to [^#\n]+)\s*(.*?)(?=###|##|$)'
        how_to_matches = re.findall(how_to_pattern, text, re.DOTALL)
        
        for idx, (title, content) in enumerate(how_to_matches):
            clean_content = self._clean_text(content)
            
            if len(clean_content) > 30:
                # Convert title to question
                question = title.strip()
                if not question.endswith('?'):
                    question += '?'
                
                pairs.append(QAPair(
                    chunk_id=f"UKC_PROCEDURE_{idx+1}",
                    question=question,
                    answer=clean_content,
                    section="Procedures",
                    topics=self._extract_topics(f"{question} {clean_content}"),
                    extraction_method="procedure_extraction",
                    confidence=0.85,
                    metadata={
                        "original_title": title,
                        "extracted_at": datetime.now().isoformat()
                    }
                ))
        
        return pairs
    
    def _extract_requirements(self, text: str) -> List[QAPair]:
        """Extract requirements from bullet point lists"""
        pairs = []
        
        # Find bullet point lists following questions
        question_bullet_pattern = r'(\*\*[^*]+\?\*\*)\s*((?:\s*[\*\-•][^*•\-\n]+\n?)+)'
        matches = re.findall(question_bullet_pattern, text, re.MULTILINE)
        
        for idx, (question_text, bullet_list) in enumerate(matches):
            # Extract the question
            question = re.sub(r'\*\*(.+?)\*\*', r'\1', question_text)
            
            # Clean bullet points
            bullets = re.findall(r'[\*\-•]\s*([^*•\-\n]+)', bullet_list)
            requirements = '. '.join(bullet.strip() for bullet in bullets if bullet.strip())
            
            if len(requirements) > 30:
                req_question = f"What are the requirements to {question.lower().replace('?', '')}?"
                
                pairs.append(QAPair(
                    chunk_id=f"UKC_REQ_{idx+1}",
                    question=req_question,
                    answer=requirements,
                    section="Requirements",
                    topics=self._extract_topics(f"{req_question} {requirements}"),
                    extraction_method="requirements_extraction",
                    confidence=0.80,
                    metadata={
                        "original_question": question,
                        "extracted_at": datetime.now().isoformat()
                    }
                ))
        
        return pairs
    
    def _create_comparison_qa(self, text: str) -> List[QAPair]:
        """Create comparison Q&A for related concepts"""
        pairs = []
        
        # Extract all fare types and their descriptions
        fare_info = {}
        fare_pattern = r'\*\*([^*]+Fares?)\*\*:\s*([^*]+?)(?=\*\*[^*]+Fares?|\n\n|##|$)'
        fare_matches = re.findall(fare_pattern, text, re.DOTALL)
        
        for fare_type, description in fare_matches:
            fare_info[fare_type] = self._clean_text(description)
        
        if len(fare_info) > 1:
            # Create comparison question
            question = "What are the differences between the fare types?"
            answer = ". ".join([f"{fare}: {desc}" for fare, desc in fare_info.items()])
            
            pairs.append(QAPair(
                chunk_id="UKC_COMPARISON_FARES",
                question=question,
                answer=answer,
                section="Fare Comparison",
                topics=self._extract_topics(f"{question} {answer}"),
                extraction_method="comparison_synthesis",
                confidence=0.75,
                metadata={
                    "comparison_type": "fare_types",
                    "items_compared": list(fare_info.keys()),
                    "extracted_at": datetime.now().isoformat()
                }
            ))
        
        return pairs
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove markdown formatting
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)      # Italic
        
        # Clean bullet points
        text = re.sub(r'^\s*[\*\-•]\s*', '', text, flags=re.MULTILINE)
        
        # Remove leading/trailing whitespace
        return text.strip()
    
    def _extract_topics(self, text: str) -> List[str]:
        """Extract relevant topics from text"""
        text_lower = text.lower()
        topics = []
        
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)
        
        return list(set(topics))  # Remove duplicates
    
    def _get_section_name(self, full_text: str, question: str) -> str:
        """Determine which section a question belongs to"""
        # Find the section header before this question
        lines = full_text.split('\n')
        question_line = -1
        
        for i, line in enumerate(lines):
            if question in line:
                question_line = i
                break
        
        if question_line > 0:
            # Look backwards for section header
            for i in range(question_line, -1, -1):
                if lines[i].startswith('##'):
                    return lines[i].replace('##', '').strip()
        
        return "General"
    
    def _deduplicate_and_clean(self, pairs: List[QAPair]) -> List[QAPair]:
        """Remove duplicates and filter low-quality pairs"""
        seen_questions = set()
        filtered_pairs = []
        
        for pair in pairs:
            # Create a normalized version of the question for deduplication
            normalized_q = re.sub(r'\W+', ' ', pair.question.lower()).strip()
            
            # Quality filters
            if (len(pair.answer) >= 20 and 
                len(pair.question) >= 10 and
                '?' in pair.question and
                normalized_q not in seen_questions):
                
                seen_questions.add(normalized_q)
                filtered_pairs.append(pair)
        
        return filtered_pairs
    
    def save_qa_pairs(self, pairs: List[QAPair], filename: str) -> None:
        """Save Q&A pairs to JSON file"""
        qa_data = [pair.to_dict() for pair in pairs]
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(qa_data, f, indent=2, ensure_ascii=False)
    
    def create_rag_format(self, pairs: List[QAPair]) -> List[Dict]:
        """Convert Q&A pairs to RAG-friendly format"""
        rag_chunks = []
        
        for pair in pairs:
            # Create embedding-friendly text
            combined_text = f"Question: {pair.question}\nAnswer: {pair.answer}"
            
            rag_chunk = {
                "id": pair.chunk_id,
                "text": combined_text,
                "metadata": {
                    "question": pair.question,
                    "answer": pair.answer,
                    "section": pair.section,
                    "topics": pair.topics,
                    "extraction_method": pair.extraction_method,
                    "confidence": pair.confidence,
                    "token_count": len(combined_text.split()),
                    "created_at": datetime.now().isoformat()
                }
            }
            rag_chunks.append(rag_chunk)
        
        return rag_chunks

def main():
    """Example usage of the Q&A extractor"""
    
    # Read the UKConnect policy file
    with open('UKConnect_policy.txt', 'r', encoding='utf-8') as f:
        policy_text = f.read()
    
    # Initialize extractor
    extractor = UKConnectQAExtractor()
    
    # Extract Q&A pairs
    print("Extracting Q&A pairs from UKConnect policy...")
    qa_pairs = extractor.extract_all_qa_pairs(policy_text)
    
    # Print summary
    print(f"\nExtracted {len(qa_pairs)} Q&A pairs:")
    print("=" * 50)
    
    for i, pair in enumerate(qa_pairs[:5]):  # Show first 5
        print(f"\n{i+1}. ID: {pair.chunk_id}")
        print(f"   Question: {pair.question}")
        print(f"   Answer: {pair.answer[:100]}...")
        print(f"   Topics: {', '.join(pair.topics)}")
        print(f"   Confidence: {pair.confidence}")
    
    if len(qa_pairs) > 5:
        print(f"\n... and {len(qa_pairs) - 5} more pairs")
    
    # Save to files
    extractor.save_qa_pairs(qa_pairs, 'ukconnect_qa_pairs.json')
    
    # Create RAG format
    rag_chunks = extractor.create_rag_format(qa_pairs)
    with open('ukconnect_rag_chunks.json', 'w', encoding='utf-8') as f:
        json.dump(rag_chunks, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved Q&A pairs to 'ukconnect_qa_pairs.json'")
    print(f"Saved RAG chunks to 'ukconnect_rag_chunks.json'")
    
    # Print statistics
    print(f"\nStatistics:")
    print(f"- Total Q&A pairs: {len(qa_pairs)}")
    print(f"- Average confidence: {sum(p.confidence for p in qa_pairs) / len(qa_pairs):.2f}")
    
    # Topic distribution
    all_topics = [topic for pair in qa_pairs for topic in pair.topics]
    topic_counts = {}
    for topic in all_topics:
        topic_counts[topic] = topic_counts.get(topic, 0) + 1
    
    print(f"\nTopic distribution:")
    for topic, count in sorted(topic_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"- {topic}: {count} pairs")

if __name__ == "__main__":
    main()