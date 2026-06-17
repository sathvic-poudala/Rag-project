import re
pattern = re.compile(r'(?:export\s+)?(?:const|let|var)\s+\w+\s*=\s*asyncHandler\s*\(')
line = "export const registerUser = asyncHandler(async (req, res) => {"
print(pattern.search(line))  # should print a match object, not None
