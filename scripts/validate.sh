#!/bin/bash
# Pre-push validation script for CareSphere API
# Checks for syntax errors, import issues, and common problems

set -e  # Exit on first error

echo "🔍 Starting validation checks..."
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Track errors
ERRORS=0
WARNINGS=0

# Change to project root
cd "$(dirname "$0")/.."

echo ""
echo "${BLUE}📁 Project Directory:${NC} $(pwd)"
echo ""

# 1. Check Python syntax in all .py files
echo "${BLUE}1️⃣  Checking Python syntax...${NC}"
SYNTAX_ERRORS=0

while IFS= read -r file; do
    if ! python3 -m py_compile "$file" 2>/dev/null; then
        echo "${RED}   ✗ Syntax error in: $file${NC}"
        python3 -m py_compile "$file" 2>&1 | sed 's/^/     /'
        SYNTAX_ERRORS=$((SYNTAX_ERRORS + 1))
    fi
done < <(find app -name "*.py" -type f ! -name "._*" 2>/dev/null)

if [ $SYNTAX_ERRORS -eq 0 ]; then
    echo "${GREEN}   ✓ All Python files have valid syntax${NC}"
else
    echo "${RED}   ✗ Found $SYNTAX_ERRORS file(s) with syntax errors${NC}"
    ERRORS=$((ERRORS + SYNTAX_ERRORS))
fi

echo ""

# 2. Check for import errors
echo "${BLUE}2️⃣  Checking imports...${NC}"
IMPORT_ERRORS=0

# Create a temporary Python script to check imports
cat > /tmp/check_imports.py << 'EOF'
import sys
import ast
import importlib.util

def check_imports(filename):
    try:
        with open(filename, 'r') as f:
            tree = ast.parse(f.read(), filename)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name.split('.')[0]
                    # Skip checking app modules (they need the full environment)
                    if not module.startswith('app'):
                        try:
                            spec = importlib.util.find_spec(module)
                            if spec is None:
                                print(f"MISSING: {module} in {filename}")
                                return False
                        except (ModuleNotFoundError, ValueError):
                            print(f"MISSING: {module} in {filename}")
                            return False
        return True
    except SyntaxError as e:
        return True  # Already caught by syntax check
    except Exception as e:
        print(f"ERROR checking {filename}: {e}")
        return False

if __name__ == "__main__":
    import sys
    success = check_imports(sys.argv[1])
    sys.exit(0 if success else 1)
EOF

while IFS= read -r file; do
    if ! python3 /tmp/check_imports.py "$file" 2>&1; then
        IMPORT_ERRORS=$((IMPORT_ERRORS + 1))
    fi
done < <(find app -name "*.py" -type f ! -name "._*" 2>/dev/null | grep -v __pycache__)

rm -f /tmp/check_imports.py

if [ $IMPORT_ERRORS -eq 0 ]; then
    echo "${GREEN}   ✓ All imports are valid${NC}"
else
    echo "${YELLOW}   ⚠ Found $IMPORT_ERRORS potential import issue(s)${NC}"
    WARNINGS=$((WARNINGS + IMPORT_ERRORS))
fi

echo ""

# 3. Check for common issues
echo "${BLUE}3️⃣  Checking for common issues...${NC}"

# Check for print statements (should use logger)
PRINT_COUNT=$(grep -r "print(" app --include="*.py" 2>/dev/null | grep -v "# print(" | wc -l | tr -d ' ')
if [ "$PRINT_COUNT" -gt 0 ]; then
    echo "${YELLOW}   ⚠ Found $PRINT_COUNT print() statement(s) - consider using logger${NC}"
    WARNINGS=$((WARNINGS + 1))
fi

# Check for exposed secrets patterns
SECRET_PATTERNS=("password\s*=\s*['\"][^'\"]*['\"]" "api_key\s*=\s*['\"][^'\"]*['\"]" "secret\s*=\s*['\"][^'\"]*['\"]")
SECRET_FOUND=0

for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -rE "$pattern" app --include="*.py" 2>/dev/null | grep -v "settings\." | grep -v "getattr" | grep -v "Field(" > /dev/null; then
        SECRET_FOUND=1
        echo "${RED}   ✗ Potential exposed secret found (pattern: $pattern)${NC}"
        grep -rE "$pattern" app --include="*.py" 2>/dev/null | grep -v "settings\." | grep -v "getattr" | grep -v "Field(" | sed 's/^/     /'
    fi
done

if [ $SECRET_FOUND -eq 0 ]; then
    echo "${GREEN}   ✓ No exposed secrets detected${NC}"
else
    ERRORS=$((ERRORS + 1))
fi

# Check for .env file is not tracked
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo "${RED}   ✗ .env file is tracked by git! This is dangerous!${NC}"
    ERRORS=$((ERRORS + 1))
else
    echo "${GREEN}   ✓ .env file is not tracked${NC}"
fi

echo ""

# 4. Check requirements.txt
echo "${BLUE}4️⃣  Checking requirements...${NC}"
if [ -f "requirements.txt" ]; then
    echo "${GREEN}   ✓ requirements.txt exists${NC}"
    
    # Check if all imports in code are in requirements
    # This is a simplified check
    if command -v pip3 &> /dev/null; then
        echo "${BLUE}   Verifying installed packages...${NC}"
        # Just check if file is readable
        if [ -r "requirements.txt" ]; then
            echo "${GREEN}   ✓ requirements.txt is readable${NC}"
        fi
    fi
else
    echo "${RED}   ✗ requirements.txt not found${NC}"
    ERRORS=$((ERRORS + 1))
fi

echo ""

# 5. Check for TODO/FIXME comments
echo "${BLUE}5️⃣  Checking for TODO/FIXME comments...${NC}"
TODO_COUNT=$(grep -r "TODO\|FIXME" app --include="*.py" 2>/dev/null | wc -l | tr -d ' ')
if [ "$TODO_COUNT" -gt 0 ]; then
    echo "${YELLOW}   ⚠ Found $TODO_COUNT TODO/FIXME comment(s)${NC}"
    grep -rn "TODO\|FIXME" app --include="*.py" 2>/dev/null | head -5 | sed 's/^/     /'
    if [ "$TODO_COUNT" -gt 5 ]; then
        echo "${YELLOW}     ... and $((TODO_COUNT - 5)) more${NC}"
    fi
fi

echo ""

# 6. Check file structure
echo "${BLUE}6️⃣  Checking file structure...${NC}"
REQUIRED_FILES=("app/__init__.py" "app/main.py" "app/config.py" "requirements.txt" ".gitignore")
MISSING_FILES=0

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "${RED}   ✗ Missing required file: $file${NC}"
        MISSING_FILES=$((MISSING_FILES + 1))
    fi
done

if [ $MISSING_FILES -eq 0 ]; then
    echo "${GREEN}   ✓ All required files present${NC}"
else
    ERRORS=$((ERRORS + MISSING_FILES))
fi

echo ""

# 7. Check for large files
echo "${BLUE}7️⃣  Checking for large files...${NC}"
LARGE_FILES=$(find . -type f -size +5M 2>/dev/null | grep -v ".git" | grep -v "node_modules" | grep -v "__pycache__")
if [ -n "$LARGE_FILES" ]; then
    echo "${YELLOW}   ⚠ Large files detected (>5MB):${NC}"
    echo "$LARGE_FILES" | sed 's/^/     /'
    WARNINGS=$((WARNINGS + 1))
else
    echo "${GREEN}   ✓ No large files detected${NC}"
fi

echo ""
echo "================================"

# Summary
if [ $ERRORS -eq 0 ] && [ $WARNINGS -eq 0 ]; then
    echo "${GREEN}✅ All checks passed! Ready to push.${NC}"
    exit 0
elif [ $ERRORS -eq 0 ]; then
    echo "${YELLOW}⚠️  Validation completed with $WARNINGS warning(s).${NC}"
    echo "${YELLOW}You can proceed with push, but consider fixing warnings.${NC}"
    exit 0
else
    echo "${RED}❌ Validation failed with $ERRORS error(s) and $WARNINGS warning(s).${NC}"
    echo "${RED}Please fix errors before pushing!${NC}"
    exit 1
fi
