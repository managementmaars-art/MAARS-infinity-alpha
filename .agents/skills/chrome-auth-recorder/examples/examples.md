# Chrome Auth Recorder - Examples

Comprehensive workflow recording examples across platforms.

## 1. GitHub - Create New Repository

**User:** "Record my workflow for creating a new GitHub repository"

**Workflow:**
1. Get context: `tabs_context_mcp()` → tabId=101 on github.com
2. Present plan with domains=["github.com"]
3. User approves
4. Start recording + capture first frame
5. Guide user: "Click '+' → 'New repository'"
6. Guide user: "Fill in repository name"
7. Guide user: "Select visibility → Create"
8. Monitor console (no errors)
9. Monitor network (POST /api/repos → 201)
10. Capture final frame + stop recording
11. Export: `github-create-repo.gif` with annotations

**Output:** 45-second GIF, 23 frames, <2MB, all annotations enabled

---

## 2. Notion - Create Database with Properties

**User:** "Document how I set up project tracking in Notion"

**Workflow:**
1. Get context → tabId=102 on notion.so
2. Present plan for notion.so
3. User approves
4. Start recording
5. **User-Guided Mode:**
   - "Click 'New Page' in sidebar"
   - "Select 'Database - Table' template"
   - "Name it 'Project Tracker'"
   - "Add property: Status (Select type)"
   - "Add property: Due Date (Date type)"
   - "Add property: Owner (Person type)"
6. Monitor console (check for sync errors)
7. Monitor network (verify database creation API)
8. Stop + export: `notion-project-tracker-setup.gif`

**Output:** 60-second GIF showing complete database setup

---

## 3. Jira - Create Epic with User Stories

**User:** "Record creating an epic with stories in Jira"

**Workflow:**
1. Get context → tabId=103 on atlassian.net
2. Present plan for atlassian.net
3. User approves
4. Start recording
5. **Automated Mode (user pre-approved steps):**
   ```
   computer(action="left_click", ref="create_button")
   wait(2)
   form_input(ref="issue_type", value="Epic")
   form_input(ref="summary", value="Q1 Platform Migration")
   computer(action="left_click", ref="create_submit")
   ```
6. Monitor console (check for validation errors)
7. Monitor network (POST /rest/api/2/issue)
8. Stop + export

**Output:** Automated workflow with precise click indicators

---

## 4. Google Admin - Create New User

**User:** "Show me adding a user to Google Workspace"

**Workflow:**
1. Get context → tabId=104 on admin.google.com
2. Present plan for admin.google.com
3. User approves
4. Start recording
5. **User-Guided (sensitive data):**
   - "Click 'Add new user'"
   - "Fill in first/last name"
   - **STOP before email entry**
   - Assistant: "I'll pause recording while you enter email/password"
   - User completes sensitive fields
   - Assistant: "Recording resumed, click 'Create User'"
6. Monitor for provisioning success
7. Stop + export: `google-workspace-add-user.gif`

**Key:** Privacy protection - pause during credential entry

---

## 5. Stripe Dashboard - Refund Transaction

**User:** "Record how to issue a refund in Stripe"

**Workflow:**
1. Get context → tabId=105 on dashboard.stripe.com
2. Present plan for dashboard.stripe.com
3. User approves
4. Start recording
5. User-Guided:
   - "Search for transaction ID"
   - "Click transaction to open details"
   - "Click 'Refund' button"
   - "Enter refund amount"
   - "Add refund reason"
   - "Confirm refund"
6. Monitor console (check for API errors)
7. Monitor network:
   ```
   read_network_requests(tabId=105, urlPattern="/refunds")
   → POST /v1/refunds (200 OK)
   ```
8. Stop + export

**Output:** Complete refund workflow with API verification

---

## 6. Slack - Create Channel and Set Permissions

**User:** "Document creating a private Slack channel"

**Workflow:**
1. Get context → tabId=106 on slack.com
2. Present plan for slack.com
3. User approves
4. Start recording
5. Hybrid Mode (mix user-guided + automated):
   - User: "Click '+' next to Channels"
   - Automated: `computer(action="left_click", ref="create_channel_btn")`
   - Automated: `form_input(ref="channel_name", value="engineering-private")`
   - Automated: `computer(action="left_click", ref="private_toggle")`
   - User: "Add team members from dropdown"
   - Automated: `computer(action="left_click", ref="create_btn")`
6. Monitor for channel creation confirmation
7. Stop + export

**Output:** Shows both automated precision and user flexibility

---

## 7. AWS Console - Launch EC2 Instance

**User:** "Record launching an EC2 instance step-by-step"

**Workflow:**
1. Get context → tabId=107 on console.aws.amazon.com
2. Present plan for console.aws.amazon.com
3. User approves
4. Start recording
5. User-Guided (complex multi-page workflow):
   - "Navigate to EC2 Dashboard"
   - "Click 'Launch Instance'"
   - "Select Amazon Linux 2 AMI"
   - "Select t2.micro instance type"
   - "Configure instance details (leave defaults)"
   - "Add storage (leave defaults)"
   - "Add tags: Name=WebServer"
   - "Configure security group"
   - "Review and launch"
6. Monitor console throughout (check for validation errors)
7. Monitor network (track API calls for each config step)
8. Stop + export: `aws-ec2-launch.gif`

**Output:** Long-form tutorial (90 seconds) split into 2 GIFs if needed

---

## 8. Error Reproduction - Capture Failed Workflow

**User:** "The submit button isn't working, can you record what happens?"

**Workflow:**
1. Get context → tabId=108 on app.example.com
2. Present plan for app.example.com
3. User approves
4. Start recording
5. User-Guided reproduction:
   - "Fill in the form as you normally would"
   - [User fills form]
   - "Now click Submit"
   - [User clicks - error occurs]
6. **Monitor console captures error:**
   ```
   read_console_messages(tabId=108, onlyErrors=true)
   → ERROR: Uncaught TypeError: Cannot read property 'value' of null
   →   at submitForm (app.js:234)
   ```
7. **Monitor network shows failed request:**
   ```
   read_network_requests(tabId=108)
   → POST /api/submit (400 Bad Request)
   → Response: {"error": "Missing required field: email"}
   ```
8. Stop + export: `submit-error-reproduction.gif`
9. Report to user:
   ```
   Error recorded with evidence:
   - Console error at line 234 in app.js
   - API returned 400: missing email field
   - GIF shows complete reproduction
   ```

**Output:** Debug-ready GIF with error context for bug report

---

## Example Patterns Summary

| Pattern | Use Case | Mode | Duration |
|---------|----------|------|----------|
| Simple CRUD | GitHub repo creation | User-Guided | 30-60s |
| Complex Setup | Notion database | User-Guided | 60-90s |
| Pre-Approved | Jira epic creation | Automated | 20-40s |
| Privacy-Aware | Google user creation | User-Guided + Pauses | 45-75s |
| API Verification | Stripe refund | User-Guided + Monitoring | 40-60s |
| Hybrid | Slack channel | Mixed | 30-50s |
| Long-Form | AWS EC2 launch | User-Guided | 90-120s |
| Error Debug | Submit failure | User-Guided + Evidence | 30-45s |

**Key Takeaways:**
- User-Guided: Best for complex/manual workflows
- Automated: Best for repetitive/pre-approved steps
- Always monitor console + network
- Split long workflows (>90s) into multiple GIFs
- Pause during sensitive data entry
- Include error context in debug recordings
