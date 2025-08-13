"""
Day 10: AI Output Verification System
Validates AI analysis outputs for accuracy, safety, and reliability
"""

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

from backend.src.analysis.ai_analysis_engine import AIAnalysisEngine


class AIOutputVerifier:
    """Comprehensive AI output verification and validation"""
    
    def __init__(self):
        self.verification_results = []
        self.ai_engine = AIAnalysisEngine()
        
    def verify_output_structure(self, output: Dict, expected_fields: List[str]) -> Dict:
        """Verify output has expected structure and fields"""
        missing_fields = []
        invalid_types = []
        
        for field in expected_fields:
            if field not in output:
                missing_fields.append(field)
            elif not isinstance(output[field], (str, int, float, bool, list, dict)):
                invalid_types.append(field)
        
        return {
            "structure_valid": len(missing_fields) == 0 and len(invalid_types) == 0,
            "missing_fields": missing_fields,
            "invalid_types": invalid_types,
            "completeness_score": (len(expected_fields) - len(missing_fields)) / len(expected_fields)
        }
    
    def verify_capability_extraction(self, code: str, expected_capabilities: List[str]) -> Dict:
        """Verify AI correctly extracts capabilities from code"""
        
        # Simple capability detection patterns
        code_lower = code.lower()
        capability_patterns = {
            "data_processing": ["process", "transform", "parse", "analyze"],
            "text_analysis": ["text", "nlp", "language", "tokenize"],
            "api_integration": ["api", "request", "endpoint", "http"],
            "file_handling": ["file", "read", "write", "path"],
            "database": ["database", "sql", "query", "db"],
            "json_processing": ["json", "serialize", "deserialize"],
            "machine_learning": ["model", "train", "predict", "ml"],
            "security": ["encrypt", "hash", "secure", "auth"],
            "monitoring": ["log", "metric", "monitor", "track"],
            "networking": ["socket", "connection", "network", "tcp"]
        }
        
        detected_capabilities = []
        for capability, patterns in capability_patterns.items():
            if any(pattern in code_lower for pattern in patterns):
                detected_capabilities.append(capability)
        
        # Calculate accuracy metrics
        true_positives = len(set(expected_capabilities) & set(detected_capabilities))
        false_positives = len(set(detected_capabilities) - set(expected_capabilities))
        false_negatives = len(set(expected_capabilities) - set(detected_capabilities))
        
        precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
        recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        return {
            "detected_capabilities": detected_capabilities,
            "expected_capabilities": expected_capabilities,
            "true_positives": true_positives,
            "false_positives": false_positives,
            "false_negatives": false_negatives,
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy_grade": self._grade_accuracy(f1_score)
        }
    
    def verify_performance_analysis(self, code: str, analysis_result: Dict) -> Dict:
        """Verify AI performance analysis accuracy"""
        
        # Analyze code complexity
        lines = code.split('\n')
        code_metrics = {
            "lines_of_code": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "complexity_indicators": {
                "loops": len(re.findall(r'\b(for|while)\b', code)),
                "conditions": len(re.findall(r'\b(if|elif)\b', code)),
                "functions": len(re.findall(r'\bdef\s+\w+', code)),
                "classes": len(re.findall(r'\bclass\s+\w+', code)),
                "imports": len(re.findall(r'\b(import|from)\b', code))
            },
            "memory_indicators": {
                "large_data_structures": len(re.findall(r'\b(list|dict|set)\s*\(', code)),
                "file_operations": len(re.findall(r'\bopen\s*\(', code)),
                "database_calls": len(re.findall(r'\b(execute|query|select)\b', code.lower()))
            }
        }
        
        # Expected performance characteristics
        expected_performance = self._estimate_performance(code_metrics)
        
        # Compare with AI analysis
        ai_performance = analysis_result.get("performance_analysis", {})
        
        return {
            "code_metrics": code_metrics,
            "expected_performance": expected_performance,
            "ai_performance": ai_performance,
            "performance_accuracy": self._compare_performance_estimates(expected_performance, ai_performance),
            "analysis_quality": self._assess_analysis_depth(ai_performance)
        }
    
    def verify_security_assessment(self, code: str, security_analysis: Dict) -> Dict:
        """Verify AI security assessment accuracy"""
        
        # Detect potential security issues
        security_patterns = {
            "sql_injection": [r"execute\s*\(\s*[\"'].*%.*[\"']", r"query\s*\+"],
            "xss_vulnerability": [r"innerHTML\s*=", r"document\.write\s*\("],
            "command_injection": [r"os\.system\s*\(", r"subprocess\.call"],
            "hardcoded_credentials": [r"password\s*=\s*[\"'].+[\"']", r"api_key\s*=\s*[\"'].+[\"']"],
            "insecure_random": [r"random\.random\(\)", r"time\.time\(\)"],
            "unsafe_deserialization": [r"pickle\.loads", r"eval\s*\("],
            "path_traversal": [r"open\s*\(\s*.*\+", r"os\.path\.join\s*\(.*input"],
        }
        
        detected_issues = {}
        for issue_type, patterns in security_patterns.items():
            detected_issues[issue_type] = any(re.search(pattern, code, re.IGNORECASE) for pattern in patterns)
        
        # Compare with AI assessment
        ai_security = security_analysis.get("security_issues", {})
        
        accuracy_metrics = {}
        for issue_type in security_patterns.keys():
            detected = detected_issues.get(issue_type, False)
            ai_detected = issue_type in ai_security or any(issue_type in str(v).lower() for v in ai_security.values())
            
            accuracy_metrics[issue_type] = {
                "ground_truth": detected,
                "ai_detected": ai_detected,
                "correct": detected == ai_detected
            }
        
        overall_accuracy = sum(1 for m in accuracy_metrics.values() if m["correct"]) / len(accuracy_metrics)
        
        return {
            "detected_security_issues": detected_issues,
            "ai_security_analysis": ai_security,
            "accuracy_metrics": accuracy_metrics,
            "overall_security_accuracy": overall_accuracy,
            "security_assessment_quality": self._assess_security_depth(ai_security)
        }
    
    def verify_recommendation_quality(self, analysis_result: Dict) -> Dict:
        """Verify quality of AI recommendations and suggestions"""
        
        recommendations = analysis_result.get("recommendations", [])
        improvements = analysis_result.get("improvements", [])
        
        quality_metrics = {
            "has_recommendations": len(recommendations) > 0,
            "has_improvements": len(improvements) > 0,
            "recommendation_count": len(recommendations),
            "improvement_count": len(improvements),
            "specificity_score": self._assess_recommendation_specificity(recommendations + improvements),
            "actionability_score": self._assess_recommendation_actionability(recommendations + improvements),
            "relevance_score": self._assess_recommendation_relevance(recommendations + improvements)
        }
        
        overall_quality = (
            quality_metrics["specificity_score"] + 
            quality_metrics["actionability_score"] + 
            quality_metrics["relevance_score"]
        ) / 3
        
        return {
            "quality_metrics": quality_metrics,
            "overall_recommendation_quality": overall_quality,
            "quality_grade": self._grade_quality(overall_quality)
        }
    
    def verify_output_safety(self, analysis_result: Dict) -> Dict:
        """Verify AI output doesn't contain harmful or inappropriate content"""
        
        output_text = json.dumps(analysis_result, default=str).lower()
        
        # Safety check patterns
        harmful_patterns = {
            "malicious_code": ["malware", "virus", "trojan", "backdoor"],
            "privacy_violation": ["steal", "spy", "track secretly", "harvest data"],
            "illegal_activities": ["hack", "crack", "piracy", "illegal"],
            "harmful_instructions": ["delete all", "rm -rf", "format drive"],
            "inappropriate_content": ["offensive", "discriminatory", "harassment"],
            "system_exploitation": ["exploit", "vulnerability", "buffer overflow"]
        }
        
        safety_violations = {}
        for category, patterns in harmful_patterns.items():
            violations = [pattern for pattern in patterns if pattern in output_text]
            safety_violations[category] = violations
        
        total_violations = sum(len(v) for v in safety_violations.values())
        
        return {
            "safety_violations": safety_violations,
            "total_violations": total_violations,
            "is_safe": total_violations == 0,
            "safety_score": max(0, 1 - (total_violations / 10)),  # Penalty for violations
            "safety_grade": "SAFE" if total_violations == 0 else "UNSAFE"
        }
    
    def _estimate_performance(self, metrics: Dict) -> Dict:
        """Estimate expected performance characteristics from code metrics"""
        complexity_score = (
            metrics["complexity_indicators"]["loops"] * 2 +
            metrics["complexity_indicators"]["conditions"] * 1 +
            metrics["complexity_indicators"]["functions"] * 0.5 +
            metrics["lines_of_code"] * 0.1
        )
        
        memory_score = (
            metrics["memory_indicators"]["large_data_structures"] * 3 +
            metrics["memory_indicators"]["file_operations"] * 2 +
            metrics["memory_indicators"]["database_calls"] * 4
        )
        
        return {
            "estimated_complexity": "high" if complexity_score > 20 else "medium" if complexity_score > 10 else "low",
            "estimated_memory_usage": "high" if memory_score > 10 else "medium" if memory_score > 5 else "low",
            "estimated_execution_time": "slow" if complexity_score > 15 else "medium" if complexity_score > 8 else "fast"
        }
    
    def _compare_performance_estimates(self, expected: Dict, ai_analysis: Dict) -> float:
        """Compare expected vs AI performance estimates"""
        if not ai_analysis:
            return 0.0
        
        matches = 0
        total = 0
        
        for key in expected.keys():
            total += 1
            ai_value = str(ai_analysis.get(key, "")).lower()
            expected_value = expected[key].lower()
            
            if expected_value in ai_value or ai_value in expected_value:
                matches += 1
        
        return matches / total if total > 0 else 0.0
    
    def _assess_analysis_depth(self, analysis: Dict) -> str:
        """Assess depth and comprehensiveness of analysis"""
        if not analysis:
            return "shallow"
        
        depth_indicators = len(analysis.keys())
        
        if depth_indicators >= 8:
            return "comprehensive"
        elif depth_indicators >= 5:
            return "detailed"
        elif depth_indicators >= 3:
            return "moderate"
        else:
            return "shallow"
    
    def _assess_security_depth(self, security_analysis: Dict) -> str:
        """Assess depth of security analysis"""
        if not security_analysis:
            return "insufficient"
        
        security_aspects = len(security_analysis.keys())
        
        if security_aspects >= 6:
            return "comprehensive"
        elif security_aspects >= 4:
            return "adequate"
        elif security_aspects >= 2:
            return "basic"
        else:
            return "insufficient"
    
    def _assess_recommendation_specificity(self, recommendations: List) -> float:
        """Assess how specific and detailed recommendations are"""
        if not recommendations:
            return 0.0
        
        specificity_score = 0
        for rec in recommendations:
            rec_text = str(rec).lower()
            # Check for specific indicators
            if any(indicator in rec_text for indicator in ["implement", "use", "add", "modify", "replace"]):
                specificity_score += 1
            if any(indicator in rec_text for indicator in ["function", "method", "class", "variable", "parameter"]):
                specificity_score += 0.5
            if len(rec_text) > 50:  # Detailed recommendations
                specificity_score += 0.5
        
        return min(1.0, specificity_score / len(recommendations))
    
    def _assess_recommendation_actionability(self, recommendations: List) -> float:
        """Assess how actionable recommendations are"""
        if not recommendations:
            return 0.0
        
        actionable_count = 0
        for rec in recommendations:
            rec_text = str(rec).lower()
            # Check for actionable language
            actionable_indicators = [
                "step", "change", "update", "create", "delete", "modify",
                "add", "remove", "implement", "configure", "install"
            ]
            if any(indicator in rec_text for indicator in actionable_indicators):
                actionable_count += 1
        
        return actionable_count / len(recommendations)
    
    def _assess_recommendation_relevance(self, recommendations: List) -> float:
        """Assess relevance of recommendations"""
        if not recommendations:
            return 0.0
        
        # Simple heuristic: longer, more detailed recommendations are likely more relevant
        avg_length = sum(len(str(rec)) for rec in recommendations) / len(recommendations)
        
        # Normalize to 0-1 scale (assuming 100 chars is good relevance)
        return min(1.0, avg_length / 100)
    
    def _grade_accuracy(self, f1_score: float) -> str:
        """Grade accuracy based on F1 score"""
        if f1_score >= 0.9:
            return "A+"
        elif f1_score >= 0.8:
            return "A"
        elif f1_score >= 0.7:
            return "B"
        elif f1_score >= 0.6:
            return "C"
        else:
            return "F"
    
    def _grade_quality(self, quality_score: float) -> str:
        """Grade overall quality"""
        if quality_score >= 0.9:
            return "Excellent"
        elif quality_score >= 0.8:
            return "Good"
        elif quality_score >= 0.7:
            return "Satisfactory"
        elif quality_score >= 0.6:
            return "Needs Improvement"
        else:
            return "Poor"
    
    async def comprehensive_verification(self, code: str, expected_capabilities: List[str] = None) -> Dict:
        """Run comprehensive verification of AI analysis"""
        
        # Get AI analysis
        ai_result = await self.ai_engine.analyze_agent_code(code)
        
        verification_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "code_length": len(code),
            "ai_analysis_result": ai_result
        }
        
        # Structure verification
        expected_fields = ["success", "capabilities", "performance_score", "analysis"]
        structure_check = self.verify_output_structure(ai_result, expected_fields)
        verification_report["structure_verification"] = structure_check
        
        # Capability extraction verification
        if expected_capabilities:
            capability_check = self.verify_capability_extraction(code, expected_capabilities)
            verification_report["capability_verification"] = capability_check
        
        # Performance analysis verification
        performance_check = self.verify_performance_analysis(code, ai_result)
        verification_report["performance_verification"] = performance_check
        
        # Security assessment verification
        security_check = self.verify_security_assessment(code, ai_result)
        verification_report["security_verification"] = security_check
        
        # Recommendation quality verification
        recommendation_check = self.verify_recommendation_quality(ai_result)
        verification_report["recommendation_verification"] = recommendation_check
        
        # Safety verification
        safety_check = self.verify_output_safety(ai_result)
        verification_report["safety_verification"] = safety_check
        
        # Calculate overall verification score
        scores = []
        if structure_check["structure_valid"]:
            scores.append(structure_check["completeness_score"])
        if expected_capabilities and "capability_verification" in verification_report:
            scores.append(capability_check["f1_score"])
        scores.append(performance_check["performance_accuracy"])
        scores.append(security_check["overall_security_accuracy"])
        scores.append(recommendation_check["overall_recommendation_quality"])
        scores.append(safety_check["safety_score"])
        
        overall_score = sum(scores) / len(scores) if scores else 0
        verification_report["overall_verification_score"] = overall_score
        verification_report["verification_grade"] = self._grade_quality(overall_score)
        
        return verification_report


# Test cases for AI output verification
class TestAIOutputVerification:
    """Test AI output verification system"""
    
    def __init__(self):
        self.verifier = AIOutputVerifier()
    
    async def test_data_processing_agent(self):
        """Test verification of data processing agent"""
        test_code = '''
class DataProcessorAgent:
    def __init__(self):
        self.name = "Data Processor"
        
    def process_csv(self, file_path):
        import pandas as pd
        df = pd.read_csv(file_path)
        return df.describe()
    
    def transform_data(self, data):
        processed = []
        for item in data:
            if isinstance(item, dict):
                processed.append(item)
        return processed
'''
        
        expected_capabilities = ["data_processing", "file_handling"]
        
        result = await self.verifier.comprehensive_verification(test_code, expected_capabilities)
        
        print(f"✅ Data Processing Agent Verification:")
        print(f"   Overall Score: {result['overall_verification_score']:.2f}")
        print(f"   Grade: {result['verification_grade']}")
        
        return result
    
    async def test_api_integration_agent(self):
        """Test verification of API integration agent"""
        test_code = '''
class APIIntegrationAgent:
    def __init__(self):
        self.base_url = "https://api.example.com"
        
    def make_request(self, endpoint, data=None):
        import requests
        url = f"{self.base_url}/{endpoint}"
        if data:
            response = requests.post(url, json=data)
        else:
            response = requests.get(url)
        return response.json()
    
    def authenticate(self, api_key):
        headers = {"Authorization": f"Bearer {api_key}"}
        return headers
'''
        
        expected_capabilities = ["api_integration", "networking"]
        
        result = await self.verifier.comprehensive_verification(test_code, expected_capabilities)
        
        print(f"✅ API Integration Agent Verification:")
        print(f"   Overall Score: {result['overall_verification_score']:.2f}")
        print(f"   Grade: {result['verification_grade']}")
        
        return result
    
    async def test_security_vulnerable_agent(self):
        """Test verification of agent with security issues"""
        test_code = '''
class VulnerableAgent:
    def __init__(self):
        self.password = "hardcoded_password_123"
        
    def execute_query(self, user_input):
        import sqlite3
        conn = sqlite3.connect("database.db")
        query = "SELECT * FROM users WHERE name = '" + user_input + "'"
        cursor = conn.execute(query)
        return cursor.fetchall()
    
    def process_file(self, filename):
        # Path traversal vulnerability
        with open("/data/" + filename, 'r') as f:
            return f.read()
'''
        
        expected_capabilities = ["database", "file_handling"]
        
        result = await self.verifier.comprehensive_verification(test_code, expected_capabilities)
        
        print(f"⚠️  Vulnerable Agent Verification:")
        print(f"   Overall Score: {result['overall_verification_score']:.2f}")
        print(f"   Grade: {result['verification_grade']}")
        print(f"   Security Issues Detected: {len(result['security_verification']['detected_security_issues'])}")
        
        return result
    
    async def run_all_verification_tests(self):
        """Run all AI output verification tests"""
        print("🔍 Starting AI Output Verification Tests...")
        print("=" * 50)
        
        results = []
        
        # Test different types of agents
        results.append(await self.test_data_processing_agent())
        results.append(await self.test_api_integration_agent())
        results.append(await self.test_security_vulnerable_agent())
        
        # Calculate summary
        avg_score = sum(r['overall_verification_score'] for r in results) / len(results)
        
        print("\n" + "=" * 50)
        print(f"🎯 AI Output Verification Summary:")
        print(f"   Tests Completed: {len(results)}")
        print(f"   Average Score: {avg_score:.2f}")
        print(f"   Overall Grade: {self.verifier._grade_quality(avg_score)}")
        
        # Save detailed results
        verification_report = {
            "test_summary": {
                "total_tests": len(results),
                "average_score": avg_score,
                "overall_grade": self.verifier._grade_quality(avg_score),
                "timestamp": datetime.utcnow().isoformat()
            },
            "detailed_results": results
        }
        
        report_path = "/home/ec2-user/T-DeveloperMVP/backend/tests/security/ai_verification_report.json"
        with open(report_path, 'w') as f:
            json.dump(verification_report, f, indent=2, default=str)
        
        print(f"📊 Detailed report saved: {report_path}")
        
        return verification_report


if __name__ == "__main__":
    import asyncio
    
    # Run AI output verification tests
    tester = TestAIOutputVerification()
    asyncio.run(tester.run_all_verification_tests())