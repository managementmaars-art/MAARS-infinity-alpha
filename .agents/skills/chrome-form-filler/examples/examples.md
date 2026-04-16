# Chrome Form Filler - Examples

## Example 1: Simple Contact Form

**User Request:**
```
"Fill out this contact form with my info:
Name: Sarah Johnson
Email: sarah.j@example.com
Phone: (555) 987-6543
Message: Interested in learning more about your services"
```

**Workflow:**

### Step 1: Get Context and Present Plan
```javascript
tabs_context_mcp(createIfEmpty=true)
// Returns: { tabIds: [101], activeTabId: 101 }

update_plan(
  domains=["contactus.example.com"],
  approach=[
    "Identify form fields on contact page",
    "Fill 4 fields with provided information",
    "Verify each field after filling",
    "Request approval before submission",
    "Submit form and verify confirmation"
  ]
)
// Wait for user approval
```

### Step 2: Discover and Map Fields
```javascript
read_page(101, filter="interactive")
```

**Response Analysis:**
```
Form fields found:
- ref_1: input[type=text] label="Name" required
- ref_2: input[type=email] label="Email Address" required
- ref_3: input[type=tel] label="Phone Number"
- ref_4: textarea label="Your Message" required
- ref_5: button type="submit" text="Send Message"
```

**Present to User:**
```
Found contact form with 4 fields:

Required Fields:
- Name → "Sarah Johnson"
- Email Address → "sarah.j@example.com"
- Your Message → "Interested in learning more about your services"

Optional Fields:
- Phone Number → "(555) 987-6543"

Proceed with filling? (yes/no)
```

### Step 3: Fill and Verify Each Field
```javascript
// Field 1: Name
form_input(101, ref="ref_1", value="Sarah Johnson")
read_page(101, ref_id="ref_1")
// ✅ Verified: "Sarah Johnson"

// Field 2: Email
form_input(101, ref="ref_2", value="sarah.j@example.com")
read_page(101, ref_id="ref_2")
// ✅ Verified: "sarah.j@example.com"

// Field 3: Phone
form_input(101, ref="ref_3", value="(555) 987-6543")
read_page(101, ref_id="ref_3")
// ✅ Verified: "(555) 987-6543"

// Field 4: Message
form_input(101, ref="ref_4", value="Interested in learning more about your services")
read_page(101, ref_id="ref_4")
// ✅ Verified: [message text]
```

### Step 4: Pre-Submission Review
```
Form ready for submission:

Name: Sarah Johnson
Email Address: sarah.j@example.com
Phone Number: (555) 987-6543
Your Message: Interested in learning more about your services

Submit this form? (yes/no)
```

### Step 5: Submit and Verify
```javascript
// User approves
computer(101, action="left_click", ref="ref_5")
computer(101, action="wait", duration=2)
read_page(101)
```

**Confirmation Found:**
```
✅ Form Submitted Successfully

Confirmation message: "Thank you for contacting us! We'll respond within 24 hours."
```

---

## Example 2: Registration Form with Sensitive Fields

**User Request:**
```
"Register me for this service:
Name: Michael Chen
Email: m.chen@email.com
Phone: 555-123-4567
Create a password for me"
```

**Workflow:**

### Step 1-2: Context and Discovery
```javascript
tabs_context_mcp(createIfEmpty=true)
update_plan(domains=["signup.example.com"], approach=[...])

read_page(102, filter="interactive")
```

**Fields Found:**
```
- ref_1: input[type=text] name="fullname" label="Full Name"
- ref_2: input[type=email] name="email" label="Email"
- ref_3: input[type=tel] name="phone" label="Phone"
- ref_4: input[type=password] name="password" label="Password" ⚠️ SENSITIVE
- ref_5: input[type=password] name="confirm" label="Confirm Password" ⚠️ SENSITIVE
- ref_6: checkbox name="terms" label="I agree to Terms"
- ref_7: button type="submit"
```

### Step 3: Present Field Mapping with Sensitive Warning
```
Found registration form with 6 fields:

Safe to Auto-Fill:
- Full Name → "Michael Chen"
- Email → "m.chen@email.com"
- Phone → "555-123-4567"
- I agree to Terms → [REQUIRES YOUR APPROVAL]

⚠️ SENSITIVE FIELDS (you must fill manually):
- Password → USER MUST CREATE
- Confirm Password → USER MUST CREATE

I cannot create passwords for security reasons. After I fill the safe fields,
you'll need to:
1. Create a password
2. Enter it in both password fields
3. Tell me when ready to submit

Proceed with filling safe fields? (yes/no)
```

### Step 4: Fill Non-Sensitive Fields
```javascript
form_input(102, ref="ref_1", value="Michael Chen")
// ✅ Verified

form_input(102, ref="ref_2", value="m.chen@email.com")
// ✅ Verified

form_input(102, ref="ref_3", value="555-123-4567")
// ✅ Verified
```

### Step 5: Terms Checkbox - Request Approval
```
The form requires agreeing to Terms and Conditions.
Should I check the "I agree to Terms" box? (yes/no)
```

**User:** "Yes"

```javascript
form_input(102, ref="ref_6", value=true)
// ✅ Verified checked
```

### Step 6: Inform User of Manual Steps
```
✅ Filled 4 fields successfully:
- Full Name: Michael Chen
- Email: m.chen@email.com
- Phone: 555-123-4567
- I agree to Terms: ✓

⚠️ Action Required:
Please create and enter your password in both password fields.

When done, tell me "ready to submit" and I'll complete the registration.
```

**User:** "ready to submit"

### Step 7: Final Verification and Submit
```
Verifying all fields before submission...

✅ Full Name: filled
✅ Email: filled
✅ Phone: filled
⚠️ Password: [please confirm you filled this]
⚠️ Confirm Password: [please confirm you filled this]
✅ Terms: agreed

Confirm password fields are complete and ready to submit? (yes/no)
```

**User:** "yes"

```javascript
computer(102, action="left_click", ref="ref_7")
computer(102, action="wait", duration=3)
read_page(102)
```

**Outcome:**
```
✅ Registration Complete

Welcome message: "Account created successfully! Check your email for verification."
```

---

## Example 3: Form Filling Error Recovery

**User Request:**
```
"Fill this survey form"
```

### Discovery Phase
```javascript
read_page(103, filter="interactive")
```

**Fields Found:**
```
- ref_1: input[type=text] label="Name"
- ref_2: select label="Age Range"
- ref_3: input[type=email] label="Email"
```

### Filling with Errors

**Field 1: Success**
```javascript
form_input(103, ref="ref_1", value="Alex Rivera")
// ✅ Verified: "Alex Rivera"
```

**Field 2: Failure - Missing Data**
```
⚠️ Field "Age Range" requires a value but none provided.

Available options:
- Under 18
- 18-25
- 26-35
- 36-50
- 51+

Which age range should I select? (provide option text)
```

**User:** "26-35"

```javascript
form_input(103, ref="ref_2", value="26-35")
// ✅ Verified: "26-35" selected
```

**Field 3: Validation Error**
```javascript
form_input(103, ref="ref_3", value="alex.rivera")
read_page(103, ref_id="ref_3")
```

**Verification reveals error message:**
```
⚠️ Field "Email" validation failed

Error message shown: "Please enter a valid email address"
Current value: "alex.rivera"

This looks like an incomplete email (missing @domain.com).
Should I correct it to "alex.rivera@[domain]"? Please provide the full email.
```

**User:** "alex.rivera@gmail.com"

```javascript
// Clear field first
computer(103, action="left_click", ref="ref_3")
computer(103, action="key", text="cmd+a")
computer(103, action="key", text="Delete")

// Re-fill with correct value
form_input(103, ref="ref_3", value="alex.rivera@gmail.com")
read_page(103, ref_id="ref_3")
// ✅ Verified: "alex.rivera@gmail.com", no error message
```

### Recovery Complete
```
✅ All errors resolved:
- Name: Alex Rivera
- Age Range: 26-35
- Email: alex.rivera@gmail.com

Proceed with submission? (yes/no)
```

---

## Example 4: Multi-Page Form

**User Request:**
```
"Complete this job application"
```

### Page 1: Personal Information

```javascript
read_page(104, filter="interactive")
```

**Fields:**
```
- ref_1: input name="firstName" label="First Name"
- ref_2: input name="lastName" label="Last Name"
- ref_3: input name="email" label="Email"
- ref_4: input name="phone" label="Phone"
- ref_5: button text="Next: Work Experience"
```

**Fill Page 1:**
```javascript
form_input(104, ref="ref_1", value="Emily")
form_input(104, ref="ref_2", value="Watson")
form_input(104, ref="ref_3", value="e.watson@email.com")
form_input(104, ref="ref_4", value="(555) 246-8135")
```

**Present for Review:**
```
Page 1/3 Complete - Personal Information:
- First Name: Emily
- Last Name: Watson
- Email: e.watson@email.com
- Phone: (555) 246-8135

Continue to next page? (yes/no)
```

**User:** "yes"

```javascript
computer(104, action="left_click", ref="ref_5")
computer(104, action="wait", duration=2)
```

### Page 2: Work Experience

```javascript
read_page(104, filter="interactive")
```

**Fields:**
```
- ref_6: input label="Current/Most Recent Job Title"
- ref_7: input label="Company Name"
- ref_8: input label="Years of Experience"
- ref_9: button text="Back"
- ref_10: button text="Next: Upload Resume"
```

**Missing Data - Request from User:**
```
Page 2/3 - Work Experience

I need the following information to continue:
- Current/Most Recent Job Title: ?
- Company Name: ?
- Years of Experience: ?

Please provide this information.
```

**User:** "Software Engineer at TechCorp, 5 years"

```javascript
form_input(104, ref="ref_6", value="Software Engineer")
form_input(104, ref="ref_7", value="TechCorp")
form_input(104, ref="ref_8", value="5")
```

**Review and Continue:**
```
Page 2/3 Complete - Work Experience:
- Job Title: Software Engineer
- Company: TechCorp
- Years: 5

Continue to final page? (yes/no)
```

```javascript
computer(104, action="left_click", ref="ref_10")
computer(104, action="wait", duration=2)
```

### Page 3: Document Upload

```javascript
read_page(104, filter="interactive")
```

**Fields:**
```
- ref_11: input[type=file] label="Upload Resume"
- ref_12: textarea label="Cover Letter (optional)"
- ref_13: button text="Submit Application"
```

**File Upload Requires Different Approach:**
```
Page 3/3 - Final Step

This page requires file upload (Resume), which needs the upload_image tool.

Resume upload: [Please upload your resume file manually or provide file path]
Cover Letter (optional): [Provide text or skip?]

Note: File uploads require special handling. Please either:
1. Upload the resume manually, then I'll continue
2. Provide the file path for automated upload
```

**User:** "Skip cover letter, I uploaded resume manually"

### Final Submission
```
Ready for final submission:

✅ Page 1: Personal info complete
✅ Page 2: Work experience complete
✅ Page 3: Resume uploaded (by you)
⏭️ Cover Letter: skipped (optional)

Submit application? (yes/no)
```

```javascript
computer(104, action="left_click", ref="ref_13")
computer(104, action="wait", duration=3)
read_page(104)
```

**Confirmation:**
```
✅ Application Submitted Successfully

Confirmation: "Thank you for applying! Application ID: #12345
We'll review your application and contact you within 5 business days."
```

---

## Example 5: Dynamic Form with Conditional Fields

**User Request:**
```
"Fill out the shipping form"
```

### Initial Fields
```javascript
read_page(105, filter="interactive")
```

**Fields Found:**
```
- ref_1: input label="Full Name"
- ref_2: radio name="shipping" value="standard" label="Standard Shipping (Free)"
- ref_3: radio name="shipping" value="express" label="Express Shipping ($15)"
- ref_4: radio name="addressType" value="home" label="Home Address"
- ref_5: radio name="addressType" value="business" label="Business Address"
```

**Fill Basic Fields:**
```javascript
form_input(105, ref="ref_1", value="David Park")
```

### Conditional Field Trigger

**Present Shipping Options:**
```
Shipping method required. Options:
- Standard Shipping (Free)
- Express Shipping ($15)

Which shipping method? (standard/express)
```

**User:** "express"

```javascript
computer(105, action="left_click", ref="ref_3")
computer(105, action="wait", duration=1)
```

### Re-Scan for New Fields

**Dynamic field appeared after Express selection:**
```javascript
read_page(105, filter="interactive")
```

**New Field Detected:**
```
- ref_6: input label="Preferred Delivery Date" (NEW - appeared after Express selected)
```

**Request Additional Data:**
```
Express shipping requires delivery date.
Preferred Delivery Date: ?
```

**User:** "2024-12-25"

```javascript
form_input(105, ref="ref_6", value="2024-12-25")
```

### Address Type Trigger

**Present Address Options:**
```
Address type required. Options:
- Home Address
- Business Address

Which address type? (home/business)
```

**User:** "business"

```javascript
computer(105, action="left_click", ref="ref_5")
computer(105, action="wait", duration=1)
```

### More Dynamic Fields

```javascript
read_page(105, filter="interactive")
```

**New Business-Specific Fields:**
```
- ref_7: input label="Company Name" (NEW)
- ref_8: input label="Department (optional)" (NEW)
```

**Request Business Info:**
```
Business address requires company name.
Company Name: ?
Department (optional): ?
```

**User:** "TechStart Inc, Engineering Department"

```javascript
form_input(105, ref="ref_7", value="TechStart Inc")
form_input(105, ref="ref_8", value="Engineering Department")
```

### Complete Dynamic Form

**Final Review:**
```
Shipping form complete:

Basic Info:
- Full Name: David Park

Shipping:
- Method: Express Shipping ($15)
- Delivery Date: 2024-12-25

Address Type: Business
- Company: TechStart Inc
- Department: Engineering Department

All conditional fields resolved. Submit? (yes/no)
```

---

## Example 6: Form Validation Error Handling

**User Request:**
```
"Submit this registration form"
```

### Fill and Initial Submit Attempt

```javascript
// Fields filled (abbreviated)
form_input(106, ref="ref_username", value="user123")
form_input(106, ref="ref_email", value="user@example.com")
// ... other fields

computer(106, action="left_click", ref="ref_submit")
computer(106, action="wait", duration=2)
read_page(106)
```

### Server-Side Validation Errors

**Page shows error messages:**
```
⚠️ Form Submission Failed

Validation errors detected:

1. Username "user123":
   Error: "Username must be at least 6 characters"

2. Email "user@example.com":
   Error: "This email is already registered"

3. Password:
   Error: "Password must contain at least one special character"

I need to correct these issues before resubmitting.
```

### Error Resolution - Field by Field

**Username Error:**
```
Username "user123" is too short (minimum 6 characters).
Suggested: "user1234" or longer

What username should I use instead?
```

**User:** "user12345"

```javascript
computer(106, action="left_click", ref="ref_username")
computer(106, action="key", text="cmd+a")
form_input(106, ref="ref_username", value="user12345")
// ✅ Verified
```

**Email Error:**
```
Email "user@example.com" is already registered.

Please provide a different email address.
```

**User:** "user2024@example.com"

```javascript
computer(106, action="left_click", ref="ref_email")
computer(106, action="key", text="cmd+a")
form_input(106, ref="ref_email", value="user2024@example.com")
// ✅ Verified
```

**Password Error:**
```
Password must contain at least one special character.

This is a sensitive field - you must update it manually.
Please modify your password to include a special character (!@#$%^&*).

Let me know when updated.
```

**User:** "done"

### Retry Submission

```
All errors corrected:
✅ Username: user12345 (meets 6 character minimum)
✅ Email: user2024@example.com (different email)
✅ Password: [updated by you with special character]

Retry submission? (yes/no)
```

**User:** "yes"

```javascript
computer(106, action="left_click", ref="ref_submit")
computer(106, action="wait", duration=2)
read_page(106)
```

**Success:**
```
✅ Registration Successful

Welcome message: "Account created! Please check your email to verify."
```

---

## Example 7: Survey with Mixed Field Types

**User Request:**
```
"Complete this customer feedback survey"
```

### Complex Field Mix

```javascript
read_page(107, filter="interactive")
```

**Fields Found:**
```
- ref_1: input[type=text] label="Name (optional)"
- ref_2: input[type=email] label="Email"
- ref_3: select label="How did you hear about us?"
- ref_4: input[type=range] label="Overall Satisfaction (1-10)"
- ref_5: checkbox label="Product Quality"
- ref_6: checkbox label="Customer Service"
- ref_7: checkbox label="Pricing"
- ref_8: textarea label="Additional Comments"
- ref_9: radio name="recommend" value="yes" label="Yes"
- ref_10: radio name="recommend" value="no" label="No"
- ref_11: radio name="recommend" value="maybe" label="Maybe"
```

### Gather Information

**Present Survey Questions:**
```
Customer Feedback Survey - 7 questions:

1. Name (optional): [Skip or provide?]
2. Email: ?
3. How did you hear about us?: [Options: Google, Friend, Advertisement, Other]
4. Overall Satisfaction (1-10): ?
5. What did you like? (check all): Product Quality, Customer Service, Pricing
6. Would you recommend us?: Yes / No / Maybe
7. Additional Comments (optional): ?

Please provide your responses.
```

**User:**
```
"Skip name,
Email: feedback@customer.com,
Heard from Friend,
Satisfaction 8,
Liked Product Quality and Customer Service,
Would recommend Yes,
Comments: Great experience overall!"
```

### Fill Survey

**Text inputs:**
```javascript
form_input(107, ref="ref_2", value="feedback@customer.com")
// ✅ Email verified
```

**Select dropdown:**
```javascript
form_input(107, ref="ref_3", value="Friend")
// ✅ "Friend" selected
```

**Range slider:**
```javascript
form_input(107, ref="ref_4", value=8)
// ✅ Slider at 8
```

**Checkboxes (multiple):**
```javascript
form_input(107, ref="ref_5", value=true)  // Product Quality
form_input(107, ref="ref_6", value=true)  // Customer Service
form_input(107, ref="ref_7", value=false) // Pricing (not checked)
// ✅ All verified
```

**Radio buttons:**
```javascript
computer(107, action="left_click", ref="ref_9") // Yes
// ✅ "Yes" selected
```

**Textarea:**
```javascript
form_input(107, ref="ref_8", value="Great experience overall!")
// ✅ Comments verified
```

### Review and Submit

```
Survey Complete:

✅ Name: [skipped - optional]
✅ Email: feedback@customer.com
✅ Source: Friend
✅ Satisfaction: 8/10
✅ Liked: Product Quality ✓, Customer Service ✓
✅ Recommend: Yes
✅ Comments: Great experience overall!

Submit survey? (yes/no)
```

**Submit and confirm as previous examples...**

---

## Key Patterns Demonstrated

1. **Permission workflow** - update_plan, field approval, submission approval
2. **Sensitive field detection** - passwords blocked from auto-fill
3. **Error recovery** - validation errors corrected iteratively
4. **Multi-page forms** - sequential page handling with state tracking
5. **Dynamic fields** - conditional field detection and re-scanning
6. **Mixed field types** - text, select, checkbox, radio, textarea, range
7. **Data validation** - format checking, required field verification
8. **User collaboration** - requesting missing data, confirming choices
