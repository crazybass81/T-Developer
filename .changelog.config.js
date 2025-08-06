module.exports = {
  "types": [
    { "type": "feat", "section": "✨ Features", "hidden": false },
    { "type": "fix", "section": "🐛 Bug Fixes", "hidden": false },
    { "type": "perf", "section": "⚡ Performance", "hidden": false },
    { "type": "docs", "section": "📚 Documentation", "hidden": false },
    { "type": "style", "section": "💎 Styles", "hidden": true },
    { "type": "refactor", "section": "♻️ Refactoring", "hidden": false },
    { "type": "test", "section": "✅ Tests", "hidden": true },
    { "type": "chore", "section": "🔧 Chores", "hidden": true },
    { "type": "build", "section": "📦 Build", "hidden": true },
    { "type": "ci", "section": "👷 CI", "hidden": true }
  ],
  "releaseCommitMessageFormat": "chore(release): 🚀 v{{currentTag}}",
  "commitUrlFormat": "{{host}}/{{owner}}/{{repository}}/commit/{{hash}}",
  "compareUrlFormat": "{{host}}/{{owner}}/{{repository}}/compare/{{previousTag}}...{{currentTag}}",
  "issueUrlFormat": "{{host}}/{{owner}}/{{repository}}/issues/{{id}}",
  "userUrlFormat": "{{host}}/{{user}}",
  "issuePrefixes": ["#", "GH-"]
};