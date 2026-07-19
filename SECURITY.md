# 🔒 Security Policy

## Supported Versions

| Version | Supported          |
|---------|:------------------:|
| 2.0.x   | ✅ Yes             |
| < 2.0   | ❌ No              |

## 🛡️ Reporting a Vulnerability

If you discover a security vulnerability within TelegramDL, please send an email to **ikx7a@hotmail.com** instead of using the issue tracker.

**Please include the following information in your report:**

- Type of issue (e.g., buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## 📋 What to Expect

- **Acknowledgment**: We'll acknowledge receipt of your vulnerability report within 48 hours.
- **Assessment**: We'll assess the vulnerability and determine its impact within 7 days.
- **Resolution**: We'll work on a fix and release it as soon as possible.
- **Credit**: We'll credit you in the release notes (unless you prefer to remain anonymous).

## 🚫 Out of Scope

The following are NOT considered security vulnerabilities:

- Issues related to Telegram's API rate limits
- Issues that require physical access to a user's device
- Issues in third-party dependencies (report these to the respective maintainers)
- Social engineering attacks

## 🔐 Security Best Practices

### For Users

1. **Never share your session string** - Treat it like a password
2. **Use environment variables** - Don't hardcode credentials in files
3. **Keep dependencies updated** - Run `pip install --upgrade -r requirements.txt`
4. **Use LOGIN_SYSTEM=true** - Each user authenticates separately
5. **Monitor your bot** - Check logs regularly for suspicious activity

### For Developers

1. **Validate all inputs** - Never trust user input
2. **Use parameterized queries** - Prevent injection attacks
3. **Sanitize filenames** - Prevent path traversal
4. **Rate limit API calls** - Prevent abuse
5. **Log security events** - Track suspicious activity

## 📞 Contact

For security-related inquiries, contact:

- **Email**: ikx7a@hotmail.com
- **Telegram**: [@Shineii86](https://t.me/Shineii86)

---

**Last Updated**: 2026-01-19
