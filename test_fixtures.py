#!/usr/bin/env python3
"""
Test fixtures and mock data for claude-code-dev-logger tests
"""
import json
from datetime import datetime
from pathlib import Path


class TestFixtures:
    """Centralized test data and fixtures"""
    
    @staticmethod
    def sample_session_metadata():
        """Return sample session metadata for testing"""
        return {
            "sessions": [
                {
                    "id": "20240724_143000",
                    "timestamp": "2024-07-24T14:30:00",
                    "project": "test-project", 
                    "methodology": "context-driven",
                    "working_directory": "/home/user/test-project",
                    "command": "claude implement feature",
                    "log_file": "/home/user/.claude-logs/claude_test-project_context-driven_20240724_143000.log",
                    "duration": 300.5,
                    "end_time": "2024-07-24T14:35:00",
                    "features_worked_on": ["authentication", "user-management"],
                    "creative_energy": 3
                },
                {
                    "id": "20240724_150000",
                    "timestamp": "2024-07-24T15:00:00", 
                    "project": "api-service",
                    "methodology": "command-based",
                    "working_directory": "/home/user/api-service",
                    "command": "claude refactor code",
                    "log_file": "/home/user/.claude-logs/claude_api-service_command-based_20240724_150000.log",
                    "duration": 180.2,
                    "end_time": "2024-07-24T15:03:00",
                    "features_worked_on": ["database", "optimization"],
                    "creative_energy": 2
                },
                {
                    "id": "20240724_160000",
                    "timestamp": "2024-07-24T16:00:00",
                    "project": "web-app",
                    "methodology": "unknown",
                    "working_directory": "/home/user/web-app", 
                    "command": "claude debug issue",
                    "log_file": "/home/user/.claude-logs/claude_web-app_unknown_20240724_160000.log",
                    "duration": 450.8,
                    "end_time": "2024-07-24T16:07:30",
                    "features_worked_on": ["frontend", "styling"],
                    "creative_energy": 1
                }
            ]
        }
    
    @staticmethod
    def sample_log_content_context_driven():
        """Return sample log content for context-driven methodology"""
        return """=== Claude CLI Session Started ===
Timestamp: 2024-07-24T14:30:00
Project: test-project
Methodology: context-driven
Working Directory: /home/user/test-project  
Command: claude implement feature
==================================================

Human: I need to implement user authentication for my web application.

Assistant: Excellent! I'd be happy to help you implement user authentication. Let me understand your requirements better. 

A few questions to get started:
- What authentication methods do you need (email/password, social login, etc.)?
- Will you need multi-factor authentication?
- What's your current tech stack?

Human: We're using Node.js with Express, and I want email/password auth with JWT tokens.

Assistant: Perfect! That's a great setup. Let me walk you through implementing JWT-based authentication. As we discussed in the project context, we'll want to follow security best practices. 

```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');
const User = require('../models/User');

// Authentication middleware
const authenticateToken = (req, res, next) => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1];
  
  if (!token) {
    return res.sendStatus(401);
  }
  
  jwt.verify(token, process.env.JWT_SECRET, (err, user) => {
    if (err) return res.sendStatus(403);
    req.user = user;
    next();
  });
};
```

This looks fantastic! 🎉 The middleware will handle token verification for protected routes.

Human: That's not quite what I meant? I also need the registration and login endpoints.

Assistant: Let me clarify - you're absolutely right! I should have included the complete auth flow. Here are the registration and login endpoints:

```javascript
// Registration endpoint
app.post('/api/auth/register', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Check if user already exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ error: 'User already exists' });
    }
    
    // Hash password
    const saltRounds = 12;
    const hashedPassword = await bcrypt.hash(password, saltRounds);
    
    // Create user
    const user = new User({
      email,
      password: hashedPassword
    });
    
    await user.save();
    
    // Generate JWT
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: '24h' }
    );
    
    res.status(201).json({ token, user: { id: user._id, email: user.email } });
  } catch (error) {
    res.status(500).json({ error: 'Registration failed' });
  }
});

// Login endpoint  
app.post('/api/auth/login', async (req, res) => {
  try {
    const { email, password } = req.body;
    
    // Find user
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Verify password
    const validPassword = await bcrypt.compare(password, user.password);
    if (!validPassword) {
      return res.status(401).json({ error: 'Invalid credentials' });
    }
    
    // Generate JWT
    const token = jwt.sign(
      { userId: user._id, email: user.email },
      process.env.JWT_SECRET, 
      { expiresIn: '24h' }
    );
    
    res.json({ token, user: { id: user._id, email: user.email } });
  } catch (error) {
    res.status(500).json({ error: 'Login failed' });
  }
});
```

Human: Great! Love it when we can work through the complete solution together. One more question - what about password reset functionality?

Assistant: Absolutely! Password reset is crucial for a complete auth system. Here's how we can implement it:

```javascript
const crypto = require('crypto');

// Password reset request
app.post('/api/auth/forgot-password', async (req, res) => {
  try {
    const { email } = req.body;
    
    const user = await User.findOne({ email });
    if (!user) {
      // Don't reveal if email exists
      return res.json({ message: 'If email exists, reset link sent' });
    }
    
    // Generate reset token
    const resetToken = crypto.randomBytes(32).toString('hex');
    const resetTokenExpiry = Date.now() + 3600000; // 1 hour
    
    user.resetToken = resetToken;
    user.resetTokenExpiry = resetTokenExpiry;
    await user.save();
    
    // Send email (implement with your email service)
    await sendResetEmail(user.email, resetToken);
    
    res.json({ message: 'If email exists, reset link sent' });
  } catch (error) {
    res.status(500).json({ error: 'Reset request failed' });
  }
});

// Password reset confirmation
app.post('/api/auth/reset-password', async (req, res) => {
  try {
    const { token, newPassword } = req.body;
    
    const user = await User.findOne({
      resetToken: token,
      resetTokenExpiry: { $gt: Date.now() }
    });
    
    if (!user) {
      return res.status(400).json({ error: 'Invalid or expired token' });
    }
    
    // Hash new password
    const hashedPassword = await bcrypt.hash(newPassword, 12);
    
    // Update user
    user.password = hashedPassword;
    user.resetToken = undefined;
    user.resetTokenExpiry = undefined;
    await user.save();
    
    res.json({ message: 'Password reset successful' });
  } catch (error) {
    res.status(500).json({ error: 'Password reset failed' });
  }
});
```

This gives you a complete, secure authentication system! The reset tokens expire after 1 hour for security.

==================================================
=== Claude CLI Session Ended ===
End Time: 2024-07-24T14:35:00
Duration: 300.50 seconds
=================================================="""    
    
    @staticmethod
    def sample_log_content_command_based():
        """Return sample log content for command-based methodology"""
        return """=== Claude CLI Session Started ===
Timestamp: 2024-07-24T15:00:00
Project: api-service
Methodology: command-based
Working Directory: /home/user/api-service
Command: claude refactor code
==================================================

Human: /refine database connection pooling

Assistant: I'll help you refine the database connection pooling. Let me analyze the current implementation.

```javascript
const mysql = require('mysql2/promise');

// Current basic pool
const pool = mysql.createPool({
  host: 'localhost',
  user: 'dbuser',
  password: 'password',
  database: 'myapp',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0
});
```

Human: /analyze pool configuration

Assistant: Analyzing your pool configuration:

**Issues found:**
1. Connection limit is too low for production
2. No connection timeout settings
3. Missing reconnection logic
4. No connection health checks

```javascript
const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  user: process.env.DB_USER,
  password: process.env.DB_PASSWORD,
  database: process.env.DB_NAME,
  waitForConnections: true,
  connectionLimit: 50,  // Increased for production
  queueLimit: 0,
  acquireTimeout: 60000,  // 60 seconds
  timeout: 60000,
  reconnect: true,
  idleTimeout: 300000,    // 5 minutes
  enableKeepAlive: true,
  keepAliveInitialDelay: 0
});
```

Human: /review error handling

Assistant: Reviewing error handling patterns:

```javascript
// Add connection event handlers
pool.on('connection', (connection) => {
  console.log('New connection established as id ' + connection.threadId);
});

pool.on('error', (err) => {
  console.error('Database pool error:', err);
  if(err.code === 'PROTOCOL_CONNECTION_LOST') {
    // Handle connection lost
    console.log('Reconnecting to database...');
  }
});

// Wrapper function with retry logic
async function executeQuery(query, params = []) {
  let retries = 3;
  
  while (retries > 0) {
    try {
      const [rows] = await pool.execute(query, params);
      return rows;
    } catch (error) {
      retries--;
      
      if (retries === 0 || !shouldRetry(error)) {
        throw error;
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}

function shouldRetry(error) {
  const retryableCodes = [
    'PROTOCOL_CONNECTION_LOST',
    'ECONNRESET', 
    'ETIMEDOUT'
  ];
  return retryableCodes.includes(error.code);
}
```

==================================================
=== Claude CLI Session Ended ===
End Time: 2024-07-24T15:03:00
Duration: 180.20 seconds
=================================================="""        

    @staticmethod
    def sample_log_content_with_confusion():
        """Return sample log content with confusion markers for testing"""
        return """Human: Can you help me with this function?

Assistant: Of course! I'd be happy to help.

Human: That's not quite what I meant. Wait, let me clarify.

Assistant: No problem! Let me clarify what you're looking for.

Human: Hmm, I'm still confused about the approach.

Assistant: I understand the confusion. Actually no, let me explain it differently.

Human: I meant something else entirely.

Assistant: Got it! As we discussed earlier, you wanted a different approach. Remember when we talked about this pattern?"""
    
    @staticmethod    
    def create_test_log_file(logs_dir: Path, filename: str, content: str):
        """Helper to create test log files"""
        log_file = logs_dir / filename  
        with open(log_file, 'w') as f:
            f.write(content)
        return log_file
    
    @staticmethod
    def create_test_metadata_file(logs_dir: Path, sessions_data: dict):
        """Helper to create test metadata files"""
        metadata_file = logs_dir / "sessions_metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(sessions_data, f, indent=2)
        return metadata_file
    
    @staticmethod
    def create_test_claude_md(project_dir: Path, methodology_type: str = "context-driven"):
        """Helper to create test .claude/CLAUDE.md files"""
        claude_dir = project_dir / ".claude"
        claude_dir.mkdir(exist_ok=True)
        
        if methodology_type == "context-driven":
            content = "# Context-Driven Spec Development\nThis is a context-driven methodology."
        elif methodology_type == "command-based":  
            content = "# Spec-Driven Agentic Development\nThis is a command-based methodology."
        else:
            content = "# Some Other Methodology\nUnknown methodology type."
        
        claude_md = claude_dir / "CLAUDE.md"
        with open(claude_md, 'w') as f:
            f.write(content)
        return claude_md