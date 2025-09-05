#!/usr/bin/env python3
"""
JavaScript Static Analysis Tool for QR Portal
Analysiert das JavaScript in hours.html für Checkbox-State-Persistence Probleme
"""

import re
import json
import os
from datetime import datetime

class JavaScriptAnalyzer:
    def __init__(self):
        self.results = {
            "analysis_timestamp": datetime.now().isoformat(),
            "files_analyzed": [],
            "checkbox_issues": [],
            "recommendations": [],
            "code_quality": {}
        }
    
    def analyze_hours_template(self):
        """Analysiert die hours.html Datei speziell für Checkbox-Probleme"""
        hours_file = "app/templates/admin/hours.html"
        
        if not os.path.exists(hours_file):
            print(f"❌ File not found: {hours_file}")
            return None
        
        with open(hours_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extrahiere JavaScript Block
        js_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
        if not js_match:
            print("❌ No JavaScript block found in hours.html")
            return None
        
        js_code = js_match.group(1)
        
        analysis = {
            "file": hours_file,
            "js_lines": len(js_code.split('\n')),
            "functions_found": [],
            "checkbox_related_code": [],
            "state_management_issues": [],
            "event_listeners": [],
            "potential_race_conditions": []
        }
        
        # Find all functions
        function_pattern = r'function\s+(\w+)\s*\([^)]*\)\s*{'
        functions = re.findall(function_pattern, js_code)
        analysis["functions_found"] = functions
        
        # Find checkbox-related code
        checkbox_patterns = [
            r'\.checked\s*=',
            r'getElementById\([^)]*checkbox',
            r'day-closed-toggle',
            r'day-single-toggle',
            r'bulk-\w+',
            r'singleToggle',
            r'closedToggle'
        ]
        
        for pattern in checkbox_patterns:
            matches = re.findall(pattern, js_code, re.IGNORECASE)
            if matches:
                analysis["checkbox_related_code"].extend([f"{pattern}: {len(matches)} occurrences"])
        
        # Analyze renderWeeklyHours function specifically
        render_func_match = re.search(r'function renderWeeklyHours\(\)\s*{(.*?)}(?=\s*function|\s*$)', js_code, re.DOTALL)
        if render_func_match:
            render_func = render_func_match.group(1)
            
            # Check for checkbox state setting logic
            if 'weeklyHours[day].length === 1' in render_func:
                if 'singleToggle.checked = true' in render_func:
                    analysis["checkbox_related_code"].append("✅ Single toggle logic present in renderWeeklyHours")
                else:
                    analysis["state_management_issues"].append(
                        "❌ Single slot detection present but checkbox not set to true"
                    )
            
            # Check for proper closed state handling
            if 'weeklyHours[day].length === 0' in render_func:
                if 'closedToggle.checked = true' in render_func:
                    analysis["checkbox_related_code"].append("✅ Closed toggle logic present in renderWeeklyHours")
                else:
                    analysis["state_management_issues"].append(
                        "❌ Empty slot detection present but closed checkbox not set"
                    )
        
        # Analyze applyBulkHours function
        bulk_func_match = re.search(r'function applyBulkHours\(\)\s*{(.*?)}(?=\s*function|\s*$)', js_code, re.DOTALL)
        if bulk_func_match:
            bulk_func = bulk_func_match.group(1)
            
            # Check if bulk function sets checkbox states
            if 'closedCheckbox.checked = false' in bulk_func:
                analysis["checkbox_related_code"].append("✅ Bulk function sets closed checkbox to false")
            else:
                analysis["state_management_issues"].append(
                    "❌ Bulk function doesn't explicitly set closed checkbox state"
                )
            
            if 'singleCheckbox.checked = true' in bulk_func:
                analysis["checkbox_related_code"].append("✅ Bulk function sets single checkbox to true")
            else:
                analysis["state_management_issues"].append(
                    "❌ Bulk function doesn't explicitly set single checkbox state"
                )
            
            # Check if renderWeeklyHours is called after bulk operation
            if 'renderWeeklyHours()' in bulk_func:
                analysis["checkbox_related_code"].append("✅ Bulk function calls renderWeeklyHours")
            else:
                analysis["state_management_issues"].append(
                    "⚠️ Bulk function may not call renderWeeklyHours to update UI"
                )
        
        # Find event listeners
        event_listener_pattern = r'addEventListener\([\'"](\w+)[\'"],\s*function'
        listeners = re.findall(event_listener_pattern, js_code)
        analysis["event_listeners"] = listeners
        
        # Check for potential race conditions
        if js_code.count('renderWeeklyHours()') > 3:
            analysis["potential_race_conditions"].append(
                f"renderWeeklyHours() called {js_code.count('renderWeeklyHours()')} times - potential race condition"
            )
        
        # Check for setTimeout usage without cleanup
        if 'setTimeout(' in js_code and 'clearTimeout' not in js_code:
            timeout_count = js_code.count('setTimeout(')
            analysis["potential_race_conditions"].append(
                f"{timeout_count} setTimeout calls without clearTimeout - potential memory leaks"
            )
        
        self.results["files_analyzed"].append(analysis)
        return analysis
    
    def identify_checkbox_bug_root_cause(self):
        """Identifiziert die Hauptursache des Checkbox-Problems"""
        hours_analysis = self.analyze_hours_template()
        
        if not hours_analysis:
            return None
        
        # Root Cause Analysis basierend auf gefundenen Problemen
        root_causes = []
        
        # Problem 1: State Management Issues
        if hours_analysis.get("state_management_issues"):
            root_causes.append({
                "category": "State Management",
                "severity": "high",
                "issues": hours_analysis["state_management_issues"],
                "description": "Checkbox states are not properly synchronized with data state"
            })
        
        # Problem 2: Race Conditions
        if hours_analysis.get("potential_race_conditions"):
            root_causes.append({
                "category": "Race Conditions", 
                "severity": "medium",
                "issues": hours_analysis["potential_race_conditions"],
                "description": "Multiple async operations may interfere with checkbox updates"
            })
        
        # Problem 3: Missing Event Synchronization
        expected_listeners = ["change", "click", "submit"]
        missing_listeners = [l for l in expected_listeners if l not in hours_analysis.get("event_listeners", [])]
        
        if missing_listeners:
            root_causes.append({
                "category": "Event Listeners",
                "severity": "medium", 
                "issues": [f"Missing event listener for: {l}" for l in missing_listeners],
                "description": "Some user interactions may not be properly handled"
            })
        
        self.results["checkbox_issues"] = root_causes
        return root_causes
    
    def generate_fix_recommendations(self):
        """Generiert konkrete Fix-Empfehlungen"""
        recommendations = []
        
        # Hauptempfehlung für Checkbox-Synchronisation
        recommendations.append({
            "priority": "high",
            "title": "Explicit Checkbox State Synchronization",
            "description": "Add explicit checkbox state updates in all data-changing functions",
            "implementation": """
// Add this helper function:
function syncCheckboxStates() {
    Object.keys(weeklyHours).forEach(day => {
        const closedCheckbox = document.getElementById(`${day}-closed`);
        const singleCheckbox = document.getElementById(`${day}-single`);
        
        if (closedCheckbox) {
            closedCheckbox.checked = (weeklyHours[day].length === 0);
        }
        
        if (singleCheckbox) {
            singleCheckbox.checked = (weeklyHours[day].length === 1);
        }
    });
}

// Call this function after:
// - applyBulkHours()
// - loadWeeklyHours()
// - resetWeeklyHours()
// - Any weeklyHours data changes
""",
            "files_to_modify": ["app/templates/admin/hours.html"]
        })
        
        # Zweite Empfehlung für Bulk-Funktion
        recommendations.append({
            "priority": "high", 
            "title": "Improve applyBulkHours() function",
            "description": "Ensure bulk hours function properly updates checkbox states",
            "implementation": """
// Modify applyBulkHours() function:
function applyBulkHours() {
    // ... existing validation code ...
    
    // Apply to selected days
    selectedDays.forEach(day => {
        weeklyHours[day] = [timeStr];
        
        // CRITICAL: Explicit checkbox updates
        const closedCheckbox = document.getElementById(`${day}-closed`);
        const singleCheckbox = document.getElementById(`${day}-single`);
        
        if (closedCheckbox && closedCheckbox.checked) {
            closedCheckbox.checked = false;
            // Trigger change event to ensure UI updates
            closedCheckbox.dispatchEvent(new Event('change'));
        }
        
        if (singleCheckbox && !singleCheckbox.checked) {
            singleCheckbox.checked = true;
            // Trigger change event
            singleCheckbox.dispatchEvent(new Event('change'));
        }
    });
    
    // Force UI update
    renderWeeklyHours();
    syncCheckboxStates(); // Call new helper function
}
""",
            "files_to_modify": ["app/templates/admin/hours.html"]
        })
        
        # Dritte Empfehlung für Debug-Logging
        recommendations.append({
            "priority": "medium",
            "title": "Add Debug Logging",
            "description": "Add console logging to track checkbox state changes",
            "implementation": """
// Add debug function:
function debugCheckboxState(day, action) {
    const closedCheckbox = document.getElementById(`${day}-closed`);
    const singleCheckbox = document.getElementById(`${day}-single`);
    
    console.log(`Checkbox Debug [${day}] ${action}:`, {
        weeklyHours: weeklyHours[day],
        closedChecked: closedCheckbox ? closedCheckbox.checked : 'not found',
        singleChecked: singleCheckbox ? singleCheckbox.checked : 'not found',
        expectedClosed: weeklyHours[day].length === 0,
        expectedSingle: weeklyHours[day].length === 1
    });
}

// Call debugCheckboxState(day, 'after_bulk') after bulk operations
// Call debugCheckboxState(day, 'after_render') after renderWeeklyHours
""",
            "files_to_modify": ["app/templates/admin/hours.html"]
        })
        
        self.results["recommendations"] = recommendations
        return recommendations
    
    def run_complete_analysis(self):
        """Führt die komplette JavaScript-Analyse aus"""
        print("🔍 Starting Complete JavaScript Analysis...")
        
        # Analyze hours template
        self.analyze_hours_template()
        
        # Identify root causes
        self.identify_checkbox_bug_root_cause()
        
        # Generate fix recommendations
        self.generate_fix_recommendations()
        
        # Save results
        results_file = f"js_analysis_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Analysis results saved: {results_file}")
        return self.results

def main():
    print("🔍 QR Portal JavaScript Analysis Tool")
    print("=" * 45)
    
    analyzer = JavaScriptAnalyzer()
    results = analyzer.run_complete_analysis()
    
    # Print summary
    print(f"\n📊 ANALYSIS SUMMARY")
    print(f"Files analyzed: {len(results.get('files_analyzed', []))}")
    print(f"Checkbox issues found: {len(results.get('checkbox_issues', []))}")
    print(f"Recommendations generated: {len(results.get('recommendations', []))}")
    
    # Print checkbox issues
    if results.get('checkbox_issues'):
        print(f"\n🐛 CHECKBOX ISSUES:")
        for issue in results['checkbox_issues']:
            print(f"   {issue['severity'].upper()}: {issue['category']}")
            for problem in issue['issues']:
                print(f"      • {problem}")
    
    # Print top recommendations
    if results.get('recommendations'):
        print(f"\n🛠️ TOP RECOMMENDATIONS:")
        for i, rec in enumerate(results['recommendations'][:3], 1):
            print(f"   {i}. [{rec['priority'].upper()}] {rec['title']}")
            print(f"      {rec['description']}")
    
    print(f"\n📁 Full analysis available in: js_analysis_results_*.json")

if __name__ == "__main__":
    main()