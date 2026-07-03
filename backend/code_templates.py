LANGUAGE_TEMPLATES = {
    "python": {
        "label": "Python",
        "extension": ".py",
        "comment": "#",
        "boilerplate": "def solution():\n    pass\n\n\nif __name__ == \"__main__\":\n    result = solution()\n    print(result)",
        "function_snippet": "def {function_name}({params}):\n    ",
    },
    "java": {
        "label": "Java",
        "extension": ".java",
        "comment": "//",
        "boilerplate": "public class Solution {\n    public static void main(String[] args) {\n        Solution s = new Solution();\n        System.out.println(s.solution());\n    }\n\n    public Object solution() {\n        \n    }\n}",
        "function_snippet": "public {return_type} {function_name}({params}) {\n    \n}",
    },
    "cpp": {
        "label": "C++",
        "extension": ".cpp",
        "comment": "//",
        "boilerplate": "#include <iostream>\n#include <vector>\n#include <string>\n\nusing namespace std;\n\nclass Solution {\npublic:\n    auto solution() {\n        \n    }\n};\n\nint main() {\n    Solution s;\n    auto result = s.solution();\n    cout << result << endl;\n    return 0;\n}",
        "function_snippet": "auto {function_name}({params}) {\n    \n}",
    },
    "javascript": {
        "label": "JavaScript",
        "extension": ".js",
        "comment": "//",
        "boilerplate": "function solution() {\n\n}\n\nconsole.log(solution());",
        "function_snippet": "function {function_name}({params}) {\n    \n}",
    },
}


def get_template(language: str) -> dict:
    return LANGUAGE_TEMPLATES.get(language, LANGUAGE_TEMPLATES["python"])


def get_boilerplate(language: str) -> str:
    return get_template(language)["boilerplate"]


def get_language_prompt(language: str) -> str:
    prompts = {
        "python": "Write a Python solution. Use type hints and follow PEP 8.",
        "java": "Write a Java solution. Use proper class structure and follow Java conventions.",
        "cpp": "Write a C++ solution. Use modern C++ features and STL where appropriate.",
        "javascript": "Write a JavaScript solution. Use modern ES6+ syntax.",
    }
    return prompts.get(language, prompts["python"])
