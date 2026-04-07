# Safety Precautions & Security Guidelines

## Overview
This document outlines all safety precautions implemented in the Multipersona Chatbot to protect users and ensure responsible AI usage.

---

## 1. INPUT VALIDATION & SANITIZATION

### Message Validation
- ✅ **Length Limits**: Messages must be between 1-1000 characters
- ✅ **Type Checking**: Only accepts string input
- ✅ **Empty Check**: Rejects empty or whitespace-only messages
- ✅ **Field Requirements**: Uses Pydantic for strict input validation

### Persona Validation
- ✅ **Whitelist Enforcement**: Only allows "teacher", "doctor", or "friend"
- ✅ **Case-Insensitive**: Normalizes persona to lowercase
- ✅ **Type Checking**: Ensures persona is string type

### History Validation
- ✅ **Length Limits**: Maximum 50 history messages per request
- ✅ **Structure Validation**: Each entry must have "role" and "content"
- ✅ **Role Validation**: Roles must be "User" or "Assistant"
- ✅ **Individual Entry Size**: History entries are truncated at 500 chars
- ✅ **Type Checking**: All content must be strings

---

## 2. INJECTION ATTACK PREVENTION

### Input Sanitization
- ✅ **HTML Tag Removal**: Strips `<script>`, `<img>`, and other HTML tags
- ✅ **Template Injection Prevention**: Detects and blocks `{{}}` patterns
- ✅ **Code Execution Prevention**: Blocks Python dunder methods and eval/exec attempts
- ✅ **Whitespace Normalization**: Removes excessive whitespace

### Detectable Patterns Blocked
```
- <script>...</script> tags (XSS)
- __method__ patterns (Python injection)
- {{...}} and {%...%} (Template injection)
- eval, exec, __import__ (Code execution)
```

---

## 3. HARMFUL CONTENT FILTERING

### Blocked Categories
- ✅ **Self-Harm Content**: Detects and blocks self-harm and suicide mentions
- ✅ **Violence & Weapons**: Blocks references to weapons and attacks
- ✅ **Illegal Drugs**: Prevents drug manufacturing instructions
- ✅ **Abuse & Exploitation**: Blocks child abuse and exploitation content
- ✅ **Hate Speech**: Detects racial slurs and discriminatory language

### Detection Method
- Regex pattern matching with case-insensitive search
- Expandable pattern list for future threats
- Returns specific blocking reason to user

---

## 4. RESPONSE SAFETY GUARDRAILS

### Response Validation
- ✅ **Length Limits**: Maximum 4000 characters per response
- ✅ **Minimum Quality**: Minimum 10 characters (prevents empty responses)
- ✅ **Type Validation**: Ensures response is valid string
- ✅ **Format Checks**: Validates response structure

### Persona-Specific Safeguards

#### Doctor Persona
- Mandatory medical disclaimer appended if missing
- Disclaimer: "This is not a substitute for a licensed medical professional. Please seek real medical advice for critical issues."
- Safety note in system prompt about avoiding prescriptions without disclaimers

#### Teacher Persona
- Educational content validation
- Encourages structured, step-by-step responses
- Includes safety notes about avoiding harmful instructions

#### Friend Persona
- Empathy and support focus
- Crisis detection language in prompt
- Encourages seeking professional help when needed

---

## 5. API SECURITY

### CORS Configuration
- ✅ **Whitelisted Origins**: Only allows requests from:
  - `http://localhost:8000`
  - `http://localhost:3000`
- ✅ **Method Restrictions**: Only allows GET and POST
- ✅ **Header Validation**: Accepts Content-Type header only

### Rate Limiting (Ready for Implementation)
- Infrastructure in place for rate limiting
- Can be enhanced with Redis backend
- Tracks requests per IP address
- Default limit: 100 requests/minute per IP

### Error Handling
- ✅ **HTTP 400**: Input validation errors (bad data)
- ✅ **HTTP 500**: Server errors (Ollama connection issues)
- ✅ **Descriptive Messages**: Explains why requests were blocked
- ✅ **No Sensitive Info Leakage**: Error messages don't expose internal details

---

## 6. LOGGING & MONITORING

### Safety Logging
- ✅ **Request Logging**: Tracks all API requests with persona
- ✅ **Error Logging**: Records all errors with timestamps
- ✅ **Security Events**: Logs blocked harmful requests
- ✅ **Response Monitoring**: Tracks response generation

### Log Location
- Application logs go to console/application output
- In production, configure external logging service (e.g., ELK, Datadog)

---

## 7. SERVICE RELIABILITY

### Timeout Protection
- ✅ **Request Timeout**: 60 seconds max per Ollama request
- ✅ **Prevents Hanging**: Automatically aborts stuck requests
- ✅ **Graceful Degradation**: Returns helpful error message

### Error Recovery
- ✅ **Connection Failures**: Handles Ollama unavailability gracefully
- ✅ **HTTP Errors**: Catches and reports specific HTTP error codes
- ✅ **Undefined Errors**: Catches unexpected exceptions
- ✅ **User-Friendly Messages**: Explains how to resolve issues

---

## 8. BEST PRACTICES FOR DEPLOYMENT

### Before Going to Production

1. **Security Review**
   - [ ] Review all system prompts with security team
   - [ ] Test injection attack filters
   - [ ] Verify CORS whitelist matches your domain
   - [ ] Test all error scenarios

2. **Rate Limiting**
   - [ ] Deploy Redis backend for rate limiting
   - [ ] Configure appropriate limits per persona
   - [ ] Monitor for abuse patterns

3. **Logging & Monitoring**
   - [ ] Set up centralized logging (ELK, Datadog, etc.)
   - [ ] Configure alerts for suspicious patterns
   - [ ] Archive logs for compliance

4. **HTTPS & Encryption**
   - [ ] Use HTTPS in production
   - [ ] Implement TLS 1.2+
   - [ ] Use secure cookies

5. **Model Safety**
   - [ ] Monitor model outputs for drift
   - [ ] Implement human review for edge cases
   - [ ] Maintain audit trail of interactions
   - [ ] Regular safety audits

6. **API Key Management** (if adding authentication)
   - [ ] Use environment variables
   - [ ] Implement API key rotation
   - [ ] Monitor for leaked keys

### Environment Variable Configuration
```
# .env
OLLAMA_URL=http://localhost:11434/api/generate
MODEL_NAME=qwen2:0.5b
PORT=8000
LOG_LEVEL=INFO
```

---

## 9. TESTING THE SAFETY FEATURES

### Test Cases to Verify

#### 1. Input Validation
```bash
# Too long message
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"'"$(python -c 'print("a"*1001)')"'","persona":"friend"}'
# Expected: HTTP 400 - "Message exceeds maximum length"

# Invalid persona
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","persona":"ninja"}'
# Expected: HTTP 400 - "Invalid persona"
```

#### 2. Injection Prevention
```bash
# XSS attempt
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"<script>alert(1)</script>","persona":"friend"}'
# Expected: HTTP 400 - "Request blocked: potentially malicious patterns"

# Template injection
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"{{7*7}}","persona":"friend"}'
# Expected: HTTP 400 - "Request blocked"
```

#### 3. Harmful Content
```bash
# Self-harm content
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"How do I harm myself?","persona":"friend"}'
# Expected: HTTP 400 - "Request blocked: harmful content"
```

#### 4. Doctor Disclaimer
```bash
# Should receive medical disclaimer
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"What is a headache?","persona":"doctor"}'
# Expected: Response includes medical disclaimer
```

---

## 10. FUTURE ENHANCEMENTS

### Planned Features
- [ ] Advanced NLP-based toxicity detection (Detoxify library)
- [ ] User authentication and session management
- [ ] Per-user rate limiting and quotas
- [ ] Content moderation API integration (OpenAI Moderation API)
- [ ] Audit trail with blockchain verification (optional)
- [ ] Multi-language support with safety patterns
- [ ] User feedback loop for continuous safety improvement
- [ ] A/B testing framework for persona improvements

### Monitoring Dashboard
- Request volume and patterns
- Blocked request statistics
- Response quality metrics
- Error rates and types
- Performance metrics

---

## Support & Reporting

### Reporting Security Issues
If you discover a security vulnerability, please email: **security@multipersona-chatbot.dev**

Do not create public GitHub issues for security vulnerabilities.

### Documentation
- [Safety Module](./backend/safety.py) - Safety functions
- [Main App](./backend/app.py) - API with safety middleware
- [LLM Service](./backend/llm_service.py) - Model response handling

---

## Version History
- **v1.0** (Apr 7, 2026) - Initial safety precautions implementation
  - Input validation and sanitization
  - Injection attack prevention
  - Harmful content filtering
  - Persona-specific guardrails
  - API security with CORS
  - Error handling and logging
